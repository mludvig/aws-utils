#!/usr/bin/env python3

# Convenience wrapper around 'aws ssm start-session'
# Author: Michael Ludvig (https://aws.nz)

# The script can list available instances, resolve instance names,
# and host names, etc. In the end it executes 'aws' to actually
# start the session.

import os
import sys
import re
import logging
import argparse
import boto3

def configure_logging(level):
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(name)s] %(levelname)s: %(message)s"
    )
    streamHandler.setFormatter(formatter)
    logger = logging.getLogger("ssm-session")
    logger.setLevel(level)
    logger.addHandler(streamHandler)
    logger.debug("Logging level set to DEBUG")

    return logger

def parse_args(argv):
    """
    Parse command line arguments.
    """
    def _type_instance_id(value):
        """
        Validate Instance ID type, make sure it is i-1234...
        """
        if not re.match('^i-[a-f0-9]+$', value):
            raise argparse.ArgumentTypeError("must be an instance id, e.g. i-1234abcd1234abcd")
        return value

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, add_help=False)

    group_general = parser.add_argument_group('General Options')
    group_general.add_argument('-p', '--profile', dest='profile', type=str, help='Configuration profile from ~/.aws/{credentials,config}')
    group_general.add_argument('-r', '--region', dest='region', type=str, help='Set / override AWS region.')
    group_general.add_argument('-v', '--verbose', action='store_const', dest='log_level', const=logging.INFO, default=logging.WARN, help='Increase log_level level')
    group_general.add_argument('-d', '--debug', action='store_const', dest='log_level', const=logging.DEBUG, help='Increase log_level level')
    group_general.add_argument('-h', '--help', action="help", help='Print this help and exit')

    group_instance_wrapper = parser.add_argument_group('Instance Selection')
    group_instance = group_instance_wrapper.add_mutually_exclusive_group(required=True)
    group_instance.add_argument('-l', '--list', dest='list', action="store_true", help='List instances available for SSM Session')
    group_instance.add_argument('-i', '--instance-id', dest='instance', metavar='INSTANCE_ID', type=_type_instance_id, help='Instance ID in a form i-1234abcd1234abcd')
    group_instance.add_argument('-n', '--name', dest='name', metavar="INSTANCE_NAME", help='Instance name or host name')

    parser.usage = "{} [OPTIONS] [-- COMMAND [ARG ...]]".format(parser.prog)

    parser.description='Start SSM session to a given instance'
    parser.epilog='''
Examples:



Visit https://aws.nz/aws-utils/ssm-session for more info
and more usage examples.
'''.format(prog=parser.prog)

    # Parse supplied arguments
    args = parser.parse_args(argv)

    return args

def update_env(env, var_names, var_value):
    if var_names and var_value:
        for var_name in var_names.split(','):
            env[var_name] = var_value

def start_session(instance_id, profile=None, region=None):
    extra_args = ""
    if profile:
        extra_args += f"--profile {profile} "
    if region:
        extra_args += f"--region {region} "
    command = f'aws {extra_args} ssm start-session --target {instance_id}'
    logger.info("Running command: %s", command)
    os.system(command)

class InstanceResolver():
    def __init__(self, args):
        session = boto3.session.Session(profile_name=args.profile, region_name=args.region)
        self.ssm_client = session.client('ssm')
        self.ec2_client = session.client('ec2')

    def get_list(self):
        items = {}

        # List instances from SSM
        logger.debug("Fetching SSM inventory")
        inventory = self.ssm_client.get_inventory()
        for entity in inventory["Entities"]:
            try:
                content = entity['Data']['AWS:InstanceInformation']["Content"][0]

                # At the moment we only support EC2 Instances
                assert content["ResourceType"] == "EC2Instance"

                # Ignore Terminated instances
                if content.get("InstanceStatus") == "Terminated":
                    logger.debug("Ignoring terminated instance: %s", entity)
                    continue

                # Add to the list
                instance_id = content['InstanceId']
                items[instance_id] = {
                    "InstanceId": instance_id,
                    "HostName": content.get("ComputerName"),
                }
                logger.debug("Added instance: %s: %r", instance_id, items[instance_id])
            except (KeyError, ValueError):
                logger.debug("SSM inventory entity not recognised: %s", entity)
                continue

        # Add attributes from EC2
        reservations = self.ec2_client.describe_instances(InstanceIds=list(items.keys()))
        for reservation in reservations['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                if not instance_id in items:
                    continue
                items[instance_id]['Addresses'] = []
                items[instance_id]['Addresses'].append(instance.get('PrivateIpAddress'))
                items[instance_id]['Addresses'].append(instance.get('PublicIpAddress'))
                for tag in instance['Tags']:
                    if tag['Key'] == 'Name':
                        items[instance_id]['InstanceName'] = tag['Value']
                logger.debug("Updated instance: %s: %r", instance_id, items[instance_id])
        return items

    def print_list(self):
        hostname_len = 0
        instname_len = 0

        items = self.get_list()
        if not items:
            logger.warn("No instances registered in SSM!")
            return

        for key in items:
            item = items[key]
            hostname_len = max(hostname_len, len(item['HostName']))
            instname_len = max(instname_len, len(item['InstanceName']))
        for key in items:
            item = items[key]
            print(f"{item['InstanceId']}   {item['HostName']:{hostname_len}}   {item['InstanceName']:{instname_len}}")

    def resolve_name(self, name):
        instances = []

        items = self.get_list()
        for instance_id in items:
            item = items[instance_id]
            if name.lower() in [item['HostName'].lower(), item['InstanceName'].lower()]:
                instances.append(instance_id)

        if not instances:
            return None

        if len(instances) > 1:
            logger.warn("Found %d instances with name '%s': %s", len(instances), name, " ".join(instances))
            logger.warn("Use --instance-id INSTANCE_ID to connect to a specific one")
            return None

        # Found only one instance - return it
        return instances[0]

if __name__ == "__main__":
    ## Split command line to main args and optional command to run
    argv = sys.argv[1:]
    args = parse_args(argv)

    logger = configure_logging(args.log_level)

    instance = None
    if args.list:
        InstanceResolver(args).print_list()
        quit(0)
    elif args.instance:
        instance = args.instance
    elif args.name:
        instance = InstanceResolver(args).resolve_name(args.name)

    if not instance:
        logger.warning("Could not resolve instance")
        quit(1)

    start_session(instance, profile=args.profile, region=args.region)
