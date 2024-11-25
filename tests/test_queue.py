import pytest
import unittest
from unittest.mock import patch, MagicMock
from gateway import Queue 
import os

class TestQueue(unittest.TestCase):

    @patch("gateway.queue.boto3.client")
    @patch.dict(os.environ, {"AWS_REGION": "us-east-1", "SQS_QUEUE_URL": "https://sqs.us-east-1.amazonaws.com/123456789012/test-queue"})
    def test_send_message_queue_success(self, mock_boto3_client):
        mock_sqs = MagicMock()
        mock_boto3_client.return_value = mock_sqs
        
        mock_sqs.send_message.return_value = {
            "MessageId": "12345",
            "ResponseMetadata": {"HTTPStatusCode": 200}
        }

        queue = Queue()
        assert queue != None

    @patch("gateway.queue.boto3.client")
    @patch.dict(os.environ, {"AWS_REGION": "us-east-1"})
    def test_queue_url_not_set(self, mock_boto3_client):
        with patch.dict(os.environ, {}, clear=True):
            mock_boto3_client.return_value = MagicMock()
            queue = Queue()
            with pytest.raises(NameError, match="name 'sqs' is not defined"):
                queue.send_message_queue(
                    event="TestEvent",
                    url_origin="http://test.com/resource",
                    method="POST",
                    params={"key": "value"},
                    body={"field": "value"}
            )


    @patch.dict(os.environ, {}, clear=True)
    def test_aws_region_not_set(self):
        queue = Queue()
        with pytest.raises(NameError, match="name 'sqs' is not defined"):
            queue.send_message_queue(
                event="TestEvent",
                url_origin="http://test.com/resource",
                method="POST",
                params={"key": "value"},
                body={"field": "value"}
        )

if __name__ == "__main__":
    unittest.main()