#!/usr/bin/env bash

CONFIG_FILE="cloudprep-artefact.conf"
BUCKET_NAME=""
STACK_NAME=""
TEMPLATE_FILE=""

if [ -e "$CONFIG_FILE" ]
then
    source "$CONFIG_FILE"
fi

if [ -z "$BUCKET_NAME" ]
then
    echo "Please enter bucket name:"
    read -r BUCKET_NAME
fi
if [ -z "$STACK_NAME" ]
then
    echo "Please enter stack name:"
    read -r STACK_NAME
fi
if [ -z "$TEMPLATE_FILE" ]
then
    echo "Please enter template name:"
    read -r TEMPLATE_FILE
fi

echo "BUCKET_NAME=\"$BUCKET_NAME\"" > "$CONFIG_FILE"
echo "STACK_NAME=\"$STACK_NAME\"" >> "$CONFIG_FILE"
echo "TEMPLATE_FILE=\"$TEMPLATE_FILE\"" >> "$CONFIG_FILE"

nBuckets=$(aws s3api list-buckets --query "Buckets[?Name=='$BUCKET_NAME']" --output text | wc -l)
if [ $nBuckets -eq 0 ]
then
    if ! aws s3 mb s3://"$BUCKET_NAME" 
    then
        exit
    fi
fi
aws s3 sync ./artefacts s3://"$BUCKET_NAME"

aws cloudformation deploy --parameter ArtefactBucket="$BUCKET_NAME" --capabilities CAPABILITY_IAM               --stack-name "$STACK_NAME" --template "$TEMPLATE_FILE"
 
