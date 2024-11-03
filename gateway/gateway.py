from flask import request, json, jsonify
import requests
from .queue import Queue
import logging
import os

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


message_error = "Error to send request, please try again"

class ExceptionHandling():

    def get_message_not_found_url(self):
        response = jsonify(self.get_response(404,"Resource not found, please contact with support"))
        return response, 404

    def get_response(status_code, message):
        data_response = {
            "message": message,
            "status_code": status_code
        }
        return data_response

    def communicate_to_incidents(self, event, endpoint):
        method = request.method
        params = request.args

        try:
            body = request.get_json()
        except Exception as e:
            body = {}

        if method == "GET":
            response = requests.request(
                method = method,
                url = endpoint,
                headers = request.headers,
                data = request.get_data(),
                params = params,
                json = body,
                timeout=20
            )
            logger.info(f"Response: {response}")
        else:
            response = Queue.send_message_queue(self, event, endpoint, method, params, body)    
            logger.info(f"Response: {response}")
            return jsonify(response)
        status_code = response.status_code

        if status_code >= 400:
            response.raise_for_status()
        
        return response

    def communicate_sync_microservice(self, endpoint):
        method = request.method
        params = request.args

        try:
            body = request.get_json()
        except Exception as e:
            body = {}

        response = requests.request(
            method = method,
            url = endpoint,
            headers = request.headers,
            data = request.get_data(),
            params = params,
            json = body,
            timeout=20
        )
        logger.info(f"Response: {response}")
        return response

    def communicate_to_microservice(self, endpoint, communication, event=None):
        try:
            if communication == "sync":
                response = self.communicate_sync_microservice(self, endpoint)

            if communication == "async_incidents":
                response = self.communicate_to_incidents(self, event, endpoint)
        
            return json.loads(response.content), response.status_code
        except requests.exceptions.Timeout as e:
            logger.info("Log error: " + str(e))
            status_code = 504
            response = jsonify(self.get_response(status_code, message_error))
            return response, status_code
        
        except Exception as e:
            logger.info("Log error: " + str(e))
            status_code = 500
            response = jsonify(self.get_response(status_code, message_error))
            return response, status_code
        