import pytest
import requests
from unittest.mock import patch, MagicMock
from flask import Flask
from gateway.errors import Unauthorized, Forbidden
from gateway.gateway import ExceptionHandling

app = Flask(__name__)

@pytest.fixture
def app_context():
    with app.app_context():
        yield

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@patch("gateway.requests.get")
def test_validate_access_authorized(mock_get, app_context):
    handler = ExceptionHandling()
    headers = {"Authorization": "Bearer token"}
    endpoint = "http://test.com/resource"

    mock_get.return_value = MagicMock(
        status_code=200,
        json=lambda: {"company": "TestCompany", "rol": "admin", "plan": "premium"},
        headers={"X-Abcall-Transaction": "transaction-id"}
    )

    with app.test_request_context(headers=headers):
        updated_headers = handler.validate_access(headers, endpoint)

    assert updated_headers["X-Abcall-Company"] == "TestCompany"
    assert updated_headers["X-Abcall-Rol"] == "admin"
    assert updated_headers["X-Abcall-Plan"] == "premium"
    assert updated_headers["X-Abcall-Transaction"] == "transaction-id"

@patch("gateway.requests.get")
def test_validate_access_unauthorized(mock_get, app_context):
    handler = ExceptionHandling()
    headers = {"Authorization": "Bearer token"}
    endpoint = "http://example.com/resource"

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"message": "Unauthorized access"}
    mock_get.return_value = mock_response

    with app.test_request_context(headers=headers):
        with pytest.raises(Unauthorized, match="Unauthorized access"):
            handler.validate_access(headers, endpoint)

@patch("gateway.requests.get")
def test_validate_access_forbidden(mock_get, app_context):
    handler = ExceptionHandling()
    headers = {"Authorization": "Bearer token"}
    endpoint = "http://test.com/resource"

    mock_get.return_value = MagicMock(
        status_code=403,
        json=lambda: {"message": "Forbidden"}
    )

    with app.test_request_context(headers=headers):
        with pytest.raises(Forbidden) as exc_info:
            handler.validate_access(headers, endpoint)
    assert str(exc_info.value) == "Forbidden"

def test_get_message_not_found_url(app_context):
    handler = ExceptionHandling()
    response, status_code = handler.get_message_not_found_url()
    assert status_code == 404
    assert response.json == {
        "message": "Resource not found, please contact with support",
        "status_code": 404
    }

@patch("gateway.requests.request")
def test_communicate_to_microservice_timeout(mock_request, app_context):
    handler = ExceptionHandling()
    endpoint = "http://test.com/resource"
    headers = {"Authorization": "Bearer token"}

    mock_response = MagicMock(status_code=504, content=b'{"message": "Error to send request, please try again"}')
    mock_request.return_value = mock_response

    with app.test_request_context(headers=headers):
        response = handler.communicate_to_microservice(endpoint, "sync")

    response_json = response[0].get_json()
    assert response_json["message"] == "Error to send request, please try again"

@patch("gateway.requests.request")
def test_communicate_sync_microservice(mock_request, app_context):
    handler = ExceptionHandling()
    endpoint = "http://test.com/resource"
    headers = {"Authorization": "Bearer token"}

    mock_response = MagicMock(status_code=200, content=b'{"result": "success"}')
    mock_request.return_value = mock_response

    with app.test_request_context(headers=headers):
        response = handler.communicate_sync_microservice(endpoint, headers)

    assert response.status_code == 200

@patch("gateway.ExceptionHandling.validate_access")
@patch("gateway.Queue.send_message_queue")
def test_communicate_to_microservice_async_incidents(mock_send_message_queue, mock_validate_access, app_context):
    handler = ExceptionHandling()
    endpoint = "http://test.com/resource"
    headers = {"Authorization": "Bearer token"}
    event = "incident_event"

    mock_validate_access.return_value = headers
    mock_send_message_queue.return_value = {"status": "success"}

    with app.test_request_context(headers=headers):
        response = handler.communicate_to_microservice(endpoint, "async_incidents", event)

    assert response != None


