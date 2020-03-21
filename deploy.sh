#!/bin/bash -xe
BUCKET_NAME=midaisuk-public-templates
TEMPLATE_NAME=aws-batch-job-monitor.template
BUILD_TEMPLATE_NAME=aws-batch-job-monitor-build.template
INCLUDE_LAMBDA=src/batch-job-monitor-lambda.py
LAMBDA_SPACE="                    "

echo "" > $BUILD_TEMPLATE_NAME

cat $TEMPLATE_NAME | while IFS= read line
do
    if [ "$line" = "##INCLUDE_LAMBDA##" ]; then
        sed "s/^/${LAMBDA_SPACE}/" $INCLUDE_LAMBDA >> $BUILD_TEMPLATE_NAME
    else
        echo -e "$line" >> $BUILD_TEMPLATE_NAME
    fi
done

aws s3 cp $BUILD_TEMPLATE_NAME s3://${BUCKET_NAME}/aws-batch-job-monitor/ --acl public-read
