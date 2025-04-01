import os

KEYCLOAK_HOST = os.environ.get('KEYCLOAK_HOST',"192.168.97.212")
KEYCLOAK_REALM = os.environ.get('KEYCLOAK_REALM',"ecommerce-realm")
KEYCLOAK_URL = f"http://{KEYCLOAK_HOST}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"