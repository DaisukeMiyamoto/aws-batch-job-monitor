#!/bin/bash -xe
BUCKET_NAME=midaisuk-public-templates
aws s3 cp aws-batch-job-monitor.template s3://${BUCKET_NAME}/aws-batch-job-monitor/ --acl public-read
