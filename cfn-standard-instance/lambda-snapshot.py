# AWS Lambda function for creating an image from a given instance.
# By Michael Ludvig - https://aws.nz

# Trigger this function from CloudWatch Scheduler (cron-like)
# Pass the Instance ID in 'instance_id' environment variable.
# The IAM Role must allow ec2:DescribeInstance, ec2:CreateImage,
# ec2:RegisterImage and ec2:CreateTags on the instance ID.

from __future__ import print_function
import os
import boto3
from datetime import datetime

ec2 = boto3.client('ec2')

def create_image(instance_id):
    snapshot_timestamp = datetime.strftime(datetime.now(), '%s')
    print('%s @ %s: Snapshotting instance' % (instance_id, snapshot_timestamp))
    instance = ec2.describe_instances(InstanceIds=[instance_id])
    description = ''
    tags = {}

    try:
        tags = {item['Key']:item['Value'] for item in instance['Reservations'][0]['Instances'][0]['Tags']}
    except:
        pass

    if 'Name' in tags:
        description = tags['Name']
    elif 'aws:cloudformation:stack-name' in tags:
        description = tags['aws:cloudformation:stack-name']
    else:
        description = instance_id

    name = instance_id + '_' + snapshot_timestamp
    description = description + ' ' + datetime.strftime(datetime.now(), '%Y-%m-%d %H-%M-%S')
    print('%s @ %s: Creating image: %s' % (instance_id, snapshot_timestamp, name))
    response = ec2.create_image(
        InstanceId = instance_id,
        Name = name,
        Description = description,
        NoReboot = False,
    )
    image_id = response['ImageId']
    print('%s @ %s: Created Image: id=%s [%s]' % (instance_id, snapshot_timestamp, image_id, name))
    image_tags = [
        {'Key': 'SnapshotTimestamp', 'Value': snapshot_timestamp },
        {'Key': 'InstanceId', 'Value': instance_id }
    ]
    if 'Name' in tags:
        image_tags.append({ 'Key': 'Name', 'Value': tags['Name'] })
    ec2.create_tags(Resources = [image_id], Tags = image_tags)
    image_tags_string = ', '.join(map(lambda x: '%(Key)s=%(Value)s' % x, image_tags))
    print('%s @ %s: Created Tags: %s' % (instance_id, snapshot_timestamp, image_tags_string))

    return (image_id, snapshot_timestamp)

def lambda_handler(event, context):
    try:
        instance_id = os.environ['instance_id']
    except:
        print('Environment variable [instance_id] must be set')
        raise

    image_id, snapshot_timestamp = create_image(instance_id)

    return image_id
