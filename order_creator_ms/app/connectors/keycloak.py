import os

KEYCLOAK_HOST = os.environ.get('KEYCLOAK_HOST',"172.19.0.114")
KEYCLOAK_REALM = os.environ.get('KEYCLOAK_REALM',"order-management-realm")
KEYCLOAK_URL = f"http://{KEYCLOAK_HOST}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"