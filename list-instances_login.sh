#!/bin/sh

# profile.d script for aws-utils' list-instances command
# Copy to /etc/profile.d and update the AWS_UTILS path below if needed
# See https://aws.nz/aws-utils/list-instances

export AWS_UTILS=/opt/aws-utils

_OUR_REGION=$(curl -s http://169.254.169.254/latest/meta-data/local-hostname | cut -d. -f2)
export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:=${_OUR_REGION}}
unset _OUR_REGION

echo
echo -e '\e[36m=== Running EC2 instances:\e[32m'
${AWS_UTILS}/list-instances/list-instances
echo -e '\e[36m=== Run \e[34mlist-instances\e[36m to display the list again.\e[0m'
echo

alias list-instances=/opt/aws-utils/list-instances/list-instances
