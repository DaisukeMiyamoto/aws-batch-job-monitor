# aws-batch-job-monitor

Monitoring AWS Batch job status and send to CloudWatch

## Usage

[![Launch](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=JobMonitor&templateURL=https://midaisuk-public-templates.s3.amazonaws.com/aws-batch-job-monitor/aws-batch-job-monitor-build.template
)

or with CLI

```bash
$ aws cloudformation create-stack --stack-name JobMonitor --template-url https://midaisuk-public-templates.s3.amazonaws.com/aws-batch-job-monitor/aws-batch-job-monitor-build.template --capabilities CAPABILITY_NAMED_IAM
```

## Collected Metrics from AWS Batch

- Job: number of jobs in each status[^1] in each queue
- Job vCPUs: total amount of requested vCPUs in each status[^1] in each queue
- Job Memory: total amount of requested memory in each status[^1] in each queue
- Array Job: total number of array job size in each status[^1] in each queue
- Array Job vCPUs: total amount of requested vCPUs from array job in each status[^1] in each queue
- Array Job Memory: total amount of requested Memory from array job in each status[^1] in each queue

[^1]: job status in `SUBMITTED`, `PENDING`, `RUNNABLE`, `STARTING', 'RUNNING` are collected. `SUCCEEDED`, `FAILED` are not collected by default.

## Screen Shots

![JobStatusMetrics](./img/job_status_screenshot.png)


## TODO

- support multi node job
- counting GPU requests


