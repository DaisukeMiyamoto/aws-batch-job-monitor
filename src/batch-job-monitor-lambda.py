# -- coding: utf-8 --
import boto3
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

batch_client = boto3.client('batch')
cloudwatch_client = boto3.client('cloudwatch')

STATUS_LIST = ['SUBMITTED', 'PENDING', 'RUNNABLE', 'STARTING', 'RUNNING'] #['SUCCEEDED', 'FAILED']
GET_JOB_DETAIL = True

def get_job_status_in_queue(queue_arn):
    job_counter = dict()
    vcpu_counter = dict()
    memory_counter = dict()
    array_job_counter = dict()
    array_vcpu_counter = dict()
    array_memory_counter = dict()

    for status in STATUS_LIST:
        vcpu_counter[status] = 0
        memory_counter[status] = 0
        array_job_counter[status] = 0
        array_vcpu_counter[status] = 0
        array_memory_counter[status] = 0

    for status in STATUS_LIST:
        response = batch_client.list_jobs(jobQueue=queue_arn, jobStatus=status)
        
        # count job
        job_counter[status] = len(response['jobSummaryList'])

        for job in response['jobSummaryList']:
            if GET_JOB_DETAIL or 'arrayProperties' in job or 'nodeProperties' in job:
                job_detail = batch_client.describe_jobs(jobs=[job['jobId']])
            
            # Array Job
            if 'arrayProperties' in job:
                for array_status in STATUS_LIST:
                    num_status = job_detail['jobs'][0]['arrayProperties']['statusSummary'][array_status]
                    array_job_counter[array_status] += num_status
                    if GET_JOB_DETAIL:
                        container = job_detail['jobs'][0]['container']
                        vcpu_counter[status] += container['vcpus'] * num_status
                        memory_counter[status] += container['memory'] * num_status
                        array_vcpu_counter[array_status] += container['vcpus'] * num_status
                        array_memory_counter[array_status] += container['memory'] * num_status

            # count vCPU/Memory
            if GET_JOB_DETAIL and not 'arrayProperties' in job:
                container = job_detail['jobs'][0]['container']
                vcpu_counter[status] += container['vcpus']
                memory_counter[status] += container['memory']

    # build metrics
    queue_metrics = {
        'job': {'Name':'Job - ', 'counter': job_counter},
        'array_job': {'Name':'Array Job - ', 'counter': array_job_counter},
    }
    if GET_JOB_DETAIL:
        queue_metrics['vcpu'] = {'Name': 'Job vCPUs - ', 'counter': vcpu_counter}
        queue_metrics['array_vcpu'] = {'Name': 'Array Job vCPUs - ', 'counter': array_vcpu_counter}
        queue_metrics['memory'] = {'Name': 'Job Memory - ', 'counter': memory_counter}
        queue_metrics['array_memory'] = {'Name': 'Array Job Memory - ', 'counter': array_memory_counter}

    return queue_metrics
        

def put_metric_to_cloudwatch(metrics_all):
    metricdata = []
    
    for queue_name, queue_metrics in metrics_all.items():
        for metrics_name, metrics in queue_metrics.items():
            for status, job_count in metrics['counter'].items():
                metricdata.append(
                    {
                        'MetricName': metrics['Name'] + status,
                        'Dimensions': [{'Name': 'QueueName', 'Value': queue_name}], 
                        'Unit': 'Count',
                        'Value': job_count
                    }
                )
    
    logger.debug(metricdata)
    cloudwatch_client.put_metric_data(
        Namespace = 'BatchJobs',
        MetricData = metricdata
    )


def lambda_handler(event, context):
    metrics_all = dict()

    # get number of jobs in each status in each queue
    response = batch_client.describe_job_queues()
    for jobqueue in response['jobQueues']:
        metrics_all = {jobqueue['jobQueueName']: get_job_status_in_queue(jobqueue['jobQueueArn'])}

    # put metrics to CloudWatch
    put_metric_to_cloudwatch(metrics_all)

    return {
        'statusCode': 200,
        'body': 'Succeeded'
    }
