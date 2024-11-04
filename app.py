from flask import Flask
from flask_cors import CORS
import os
import logging

from gateway import \
    ExceptionHandling

app = Flask(__name__)

app_context = app.app_context()
app_context.push()

cors = CORS(app)

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# URL to Test in local with docker
url_base_manejo_clientes = 'http://clientes-microservice:5001'
url_base_auth_api = 'http://auth-api-microservice:5002'
url_base_incidents = 'http://incidents-microservice:5003'
url_base_chatbot_api = 'http://chatbot-api:5008/api'
url_base_analitica = 'http://analitica-microservice:5005'

# Get URL to production
if os.environ.get("URL_BASE_INCIDENTS"):
    url_base_incidents = os.environ.get("URL_BASE_INCIDENTS")

if os.environ.get("URL_BASE_AUTH_API"):
    url_base_auth_api = os.environ.get("URL_BASE_AUTH_API")

incidents_on_local = True
if os.environ.get("URL_BASE_MANEJO_CLIENTES"):
    incidents_on_local = False
    url_base_manejo_clientes = os.environ.get("URL_BASE_MANEJO_CLIENTES")

if os.environ.get("URL_BASE_CHATBOT_API"):
    url_base_chatbot_api = os.environ.get("URL_BASE_CHATBOT_API")

if os.environ.get("URL_BASE_ANALITICA"):
    url_base_analitica = os.environ.get("URL_BASE_ANALITICA")

logger.info(f"URL BASE INCIDENTS: {url_base_incidents}")
logger.info(f"URL BASE AUTH API: {url_base_auth_api}")
logger.info(f"URL BASE MANEJO CLIENTES: {url_base_manejo_clientes}")
logger.info(f"URL BASE CHATBOT API: {url_base_chatbot_api}")
logger.info(f"URL BASE ANALITICA: {url_base_analitica}")

EVENT_INCIDENTS = "incident"

COMUNNICATION_INCIDENT = "async_incidents"
COMUNNICATION_SYNC = "sync"

# --------------------------------------------
# Routes to microservice auth-api
#---------------------------------------------
@app.route('/auth/register', methods=['POST'])
def post_register():
    return ExceptionHandling.communicate_to_microservice(ExceptionHandling, url_base_auth_api + "/auth/register", COMUNNICATION_SYNC)
    
@app.route('/auth/login', methods=['POST'])
def post_login():
    return ExceptionHandling.communicate_to_microservice(ExceptionHandling, url_base_auth_api + "/auth/login", COMUNNICATION_SYNC)

@app.route('/auth/logout', methods=['POST'])
def post_logout():
    return ExceptionHandling.communicate_to_microservice(ExceptionHandling, url_base_auth_api + "/auth/logout", COMUNNICATION_SYNC)

@app.route('/auth/verify-authorization', methods=['GET'])
def get_verify_authorization():
    return ExceptionHandling.communicate_to_microservice(ExceptionHandling, url_base_auth_api + "/auth/verify-authorization", COMUNNICATION_SYNC)


# --------------------------------------------
# Routes to microservice manejo clientes
#---------------------------------------------    
@app.route('/clients/create_client', methods=['POST'])
def post_create_client():
    return ExceptionHandling.communicate_to_microservice(ExceptionHandling, url_base_manejo_clientes + "/clients/create_client", COMUNNICATION_SYNC)
 
@app.route('/clients/get_client/<id>', methods=['GET'])
def get_client(id):
    return ExceptionHandling.communicate_to_microservice(ExceptionHandling, url_base_manejo_clientes + f"/clients/get_client/{id}", COMUNNICATION_SYNC)

@app.route('/clients/update_client_plan', methods=['PUT'])
def update_client_plan():
     return ExceptionHandling.communicate_to_microservice(ExceptionHandling, url_base_manejo_clientes + f"/clients/update_client_plan", COMUNNICATION_SYNC)

# --------------------------------------------
# Routes to microservice incidents
#---------------------------------------------
@app.route('/incidents/get_incidents/<client>', methods=['GET'])
def get_incidents(client):
    if incidents_on_local:
        return ExceptionHandling.communicate_to_microservice(ExceptionHandling, url_base_incidents + f"/incidents/get_incidents/{client}", COMUNNICATION_SYNC)
    else: 
        return ExceptionHandling.communicate_to_microservice(ExceptionHandling, url_base_incidents + f"/incidents/get_incidents/{client}", COMUNNICATION_INCIDENT)

@app.route('/incidents/get_user/<id>/<client>', methods=['GET'])
def get_user(id, client):
    if incidents_on_local:
        return ExceptionHandling.communicate_to_microservice(ExceptionHandling, url_base_incidents + f"/incidents/get_user/{id}/{client}", COMUNNICATION_SYNC)
    else: 
        return ExceptionHandling.communicate_to_microservice(ExceptionHandling, url_base_incidents + f"/incidents/get_user/{id}/{client}", COMUNNICATION_INCIDENT)

@app.route('/incidents/get_incident/<id>/<client>', methods=['GET'])
def get_incident(id, client):
    if incidents_on_local:
        return ExceptionHandling.communicate_to_microservice(ExceptionHandling, url_base_incidents + f"/incidents/get_incident/{id}/{client}", COMUNNICATION_SYNC)
    else: 
        return ExceptionHandling.communicate_to_microservice(ExceptionHandling, url_base_incidents + f"/incidents/get_incident/{id}/{client}", COMUNNICATION_INCIDENT)

@app.route('/incidents/create_user', methods=['POST'])
def create_user():
        return ExceptionHandling.communicate_to_microservice(ExceptionHandling, url_base_incidents + f"/incidents/create_user", COMUNNICATION_SYNC)
    
@app.route('/incidents/create_incident', methods=['POST'])
def create_incident():
    if incidents_on_local:
        return ExceptionHandling.communicate_to_microservice(ExceptionHandling, url_base_incidents + f"/incidents/create_incident", COMUNNICATION_SYNC)
    else: 
        return ExceptionHandling.communicate_to_microservice(ExceptionHandling, url_base_incidents + f"/incidents/create_incident", COMUNNICATION_INCIDENT, EVENT_INCIDENTS)
    
@app.route('/incidents/update_incident_response', methods=['PUT'])
def update_incident_response():
    return ExceptionHandling.communicate_to_microservice(ExceptionHandling, url_base_incidents + f"/incidents/update_incident_response", COMUNNICATION_SYNC)

# --------------------------------------------
# Routes to chatbot api
#---------------------------------------------
@app.route('/getnode', methods=['GET'])
def get_node():
    return ExceptionHandling.communicate_to_microservice(ExceptionHandling, url_base_chatbot_api + "/getnode", COMUNNICATION_SYNC)

@app.route('/getsolutions', methods=['GET'])
def get_solutions():
    return ExceptionHandling.communicate_to_microservice(ExceptionHandling, url_base_chatbot_api + "/getsolutions", COMUNNICATION_SYNC)

# --------------------------------------------
# Routes to microservice analitica
# ---------------------------------------------
@app.route('/analitica/get_incidents', methods=['GET'])
def get_incidents_analitica():
    return ExceptionHandling.communicate_to_microservice(ExceptionHandling,url_base_analitica + f"/analitica/get_incidents",COMUNNICATION_SYNC)
# Error handler
@app.errorhandler(404)
def resource_not_found(error):
    return ExceptionHandling.get_message_not_found_url(ExceptionHandling)

# Ping endpoint
@app.route('/ping', methods=['GET'])
def ping():
    return "pong", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
