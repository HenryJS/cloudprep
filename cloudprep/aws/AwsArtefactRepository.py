from cloudprep.ArtefactRepository import ArtefactRepository


class AwsArtefactRepository(ArtefactRepository):

    def __init__(self):
        super().__init__()

        self.__artefact_bucket_parameter = "ArtefactBucket"

    @property
    def artefact_bucket_parameter(self):
        return self.__artefact_bucket_parameter

    @property
    def pre_deployment_script(self):
        return """#!/usr/bin/env bash

CONFIG_FILE=cloudprep-artefact.conf
BUCKET_NAME=""
STACK_NAME=""
TEMPLATE=""

if [ -e $CONFIG_FILE ]
then
    source $CONFIG_FILE
fi

if [ -z $BUCKET_NAME ]
then
    echo "Please enter bucket name:"
    read -r BUCKET_NAME
fi
if [ -z $STACK_NAME ]
then
    echo "Please enter stack name:"
    read -r STACK_NAME
fi
if [ -z $TEMPLATE_FILE ]
then
    echo "Please enter template name:"
    read -r TEMPLATE_FILE
fi

echo "BUCKET_NAME=$BUCKET_NAME" > $CONFIG_FILE
echo "STACK_NAME=$STACK_NAME" >> $CONFIG_FILE
echo "TEMPLATE_FILE=$TEMPLATE_FILE" >> $CONFIG_FILE

nBuckets=$(aws s3api list-buckets --query "Buckets[?Name=='$BUCKET_NAME']" --output text | wc -l)
if [ $nBuckets -eq 0 ]
then
    aws s3 mb s3://$BUCKET_NAME
    if [ $? -ne 0 ]
    then
        exit
    fi
fi
aws s3 sync {} s3://$BUCKET_NAME

echo aws cloudformation deploy --parameter ArtefactBucket=$BUCKET_NAME --capabilities CAPABILITY_IAM \
              --stack-name $STACK_NAME --template $TEMPLATE_FILE
aws cloudformation deploy --parameter ArtefactBucket=$BUCKET_NAME --capabilities CAPABILITY_IAM \
              --stack-name $STACK_NAME --template $TEMPLATE_FILE
 
""".format(self._local_path)
