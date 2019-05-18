#!/usr/bin/env python3

# Convenience wrapper around 'aws ssm start-session'
# Author: Michael Ludvig (https://aws.nz)

# The script can list available instances, resolve instance names,
# and host names, etc. In the end it executes 'aws' to actually
# start the session.

import os
import sys
import re
import argparse
import boto3

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
    group_general.add_argument('-v', '--verbose', action='count', dest='verbose', help='Increate verbosity level')
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

    # If the user specified --region he probably wants to have it exported
    if args.region and args.region_var == '':
        # Figure out the default '--region-var' variable
        args.region_var = parser.parse_args(['--region-var']).region_var

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
    print(command)
    os.system(command)

class InstanceResolver():
    def __init__(self, args):
        session = boto3.session.Session(profile_name=args.profile, region_name=args.region)
        ssm_client = session.client('ssm')
        ec2_client = session.client('ec2')

if __name__ == "__main__":
    ## Split command line to main args and optional command to run
    argv = sys.argv[1:]
    args = parse_args(argv)

    if args.instance:
        start_session(args.instance, profile=args.profile, region=args.region)
