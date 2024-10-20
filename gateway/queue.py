from flask import json
import boto3
import os

if os.environ.get('AWS_REGION'):
    region = os.environ.get('AWS_REGION')
    sqs = boto3.client('sqs', region_name=region)
else:
    raise Exception("Region must be defined")

if os.environ.get('SQS_QUEUE_URL'):
    queue_url = os.environ.get('SQS_QUEUE_URL')
    print("SQS PRODUCTION URL: " + queue_url)
else:
    queue_url = "test-queue"
    print("SQS TEST URL: " + queue_url)

class Queue():
    def send_message_queue(self, event, url_origin, method, params, body):
        body = json.dumps(body)
        response = sqs.send_message(
            QueueUrl=queue_url,
            DelaySeconds=0,
            MessageAttributes={
                'event': {
                    'DataType': 'String',
                    'StringValue': event
                },
                'url_origin': {
                    'DataType': 'String',
                    'StringValue': url_origin
                },
                'method': {
                    'DataType': 'String',
                    'StringValue': method
                }
            },
            MessageBody=(
                body
            )
        )
        return response
