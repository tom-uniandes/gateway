from flask import request, json, jsonify
import requests
from .queue import Queue
import logging
import os
from.errors import Unauthorized, Forbidden
from urllib.parse import urlparse

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

    def validate_access(self, headers, endpoint):
        headers = dict(request.headers)
        uri = urlparse(endpoint).path
        url_base_auth_api = 'http://auth-api-microservice:5002'
        if os.environ.get("URL_BASE_AUTH_API"):
            url_base_auth_api = os.environ.get("URL_BASE_AUTH_API")

        create_auth_api_url = f'{url_base_auth_api}/auth/verify-authorization?uri={uri}'
        headers["X-Abcall-Transaction"] = os.environ.get("API_KEY_AUTH_API")
        response = requests.get(create_auth_api_url, headers=headers)

        if response.status_code == 403:
            raise Forbidden(response.json().get("message"))
        
        if response.status_code == 401:
            raise Unauthorized(response.json().get("message"))

        data = response.json()
        if data:
            headers["X-Abcall-Company"] = data.get("company")
            headers["X-Abcall-Rol"] = data.get("rol")
            headers["X-Abcall-Plan"] = data.get("plan")

        if response.headers:
            headers["X-Abcall-Transaction"] = response.headers.get("X-Abcall-Transaction")

        return headers

    def communicate_to_incidents_queue(self, event, endpoint):
        method = request.method
        params = request.args
        try:
            body = request.get_json()
        except Exception as e:
            body = {}

        response = Queue.send_message_queue(self, event, endpoint, method, params, body)    
        logger.info(f"Response: {response}")
        return jsonify(response)

    def communicate_sync_microservice(self, endpoint, headers):
        method = request.method
        params = request.args

        try:
            body = request.get_json()
        except Exception as e:
            body = {}

        response = requests.request(
            method = method,
            url = endpoint,
            headers = headers,
            data = request.get_data(),
            params = params,
            json = body,
            timeout=20
        )
        logger.info(f"Response: {response}")
        return response

    def communicate_to_microservice(self, endpoint, communication, event=None):
        try:
            headers = self.validate_access(self, request.headers, endpoint)
            if communication == "sync":
                response = self.communicate_sync_microservice(self, endpoint, headers)
                return json.loads(response.content), response.status_code

            if communication == "async_incidents":
                response = self.communicate_to_incidents_queue(self, event, endpoint)
                # If response is a requests.Response object
                if isinstance(response, requests.Response):
                    return response.json(), response.status_code
                # If response is a custom dictionary
                elif isinstance(response, dict):
                    return response, 200
                elif response.is_json:
                    return response.get_json(), response.status_code
                else:
                    # Handle unexpected response types
                    logger.error("Unexpected response type")
                    return {"message": "Unexpected response type"}, 500
        
        except requests.exceptions.Timeout as e:
            logger.info("Log error: " + str(e))
            status_code = 504
            response = jsonify(self.get_response(status_code, message_error))
            return response, status_code
        
        except Unauthorized as e:
            logger.info("Log error: " + str(e))
            status_code = 401
            response = jsonify(self.get_response(status_code, str(e)))
            return response, status_code
        
        except Forbidden as e:
            logger.info("Log error: " + str(e))
            status_code = 403
            response = jsonify(self.get_response(status_code, str(e)))
            return response, status_code
        
        except Exception as e:
            logger.info("Log error: " + str(e))
            status_code = 500
            response = jsonify(self.get_response(status_code, message_error))
            return response, status_code
        