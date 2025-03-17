import jwt
import requests
import json
import redis
from jwt.algorithms import RSAAlgorithm
from cryptography.hazmat.primitives import serialization
import re
# Keycloak Config
KEYCLOAK_DNS = "172.19.0.114"
KEYCLOAK_REALM = "order-management-realm"
KEYCLOAK_URL = f"http://{KEYCLOAK_DNS}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"
JWT_TOKEN_TEXT = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIxU0Y4VWtjVEN3VTM4RGh6N1l4MVAxYjdpRGxHWURSQk1DWExJRF96TXUwIn0.eyJleHAiOjE3NDA2MTgxNDAsImlhdCI6MTc0MDYxNzY2MCwianRpIjoiMTNjOTUzNjItZjJmZC00ZTNkLWJlMmItYTQ5OWRkZjY1OWZiIiwiaXNzIjoiaHR0cDovLzE3Mi4xOS4wLjExNC9yZWFsbXMvb3JkZXItbWFuYWdlbWVudC1yZWFsbSIsInR5cCI6IkJlYXJlciIsImF6cCI6ImNyZWF0ZS1vcmRlcnMtY2xpZW50Iiwic2lkIjoiZjdmYmFjMjktZWIwMC00NmE4LTljZDMtMDgyM2VkNThmOGY4IiwicmVzb3VyY2VfYWNjZXNzIjp7ImNyZWF0ZS1vcmRlcnMtY2xpZW50Ijp7InJvbGVzIjpbImNyZWF0ZS1vcmRlcnMtY2xpZW50LXJvbGUiXX19LCJzY29wZSI6ImNyZWF0ZV9vcmRlcnNfc2NvcGUifQ.iYvn_0IcAjUgErgC6FMhvGeac5YwzYBF-wfFPVGZAfy8krubEbCokoI_J9NyhGtLxNeciJOndgFIKCHWekYouAqwiQ3SC6MofkIEPMFAe1nFtbhtbJ66YzhZGKISfRGiVfnk1r-EmdYWRlUrXnCJmpuU4LYcWRy0veSppmQw6MzWLECrGWa6P05oZkDB_v8FEeoYSWj3g7cjPAaw5keqFv9H5C-1B9U70-0JF_NDbDyuiUZoi5nKtBVrjaKD4YqfbrRLzKN7UQt-igEfqzN0WBVy8wGk_wNiiPC1Fhr1UFweiGMnVBMXRkx8Ml8PoRaGvvmg2TakqSdpKN4vPbLl7Q"
redis_client = redis.Redis(host='172.19.0.112', port=6379, db=0)

# Fetch Public Key from Keycloak
def get_public_key(token):
    kid = retrieve_kid_from_token(token)
    public_key = get_cashed_key(kid)
    if public_key:
        print(f"Public key for {kid} found in Redis")
        return public_key
    else:
        print(f"Public key for {kid} not found in Redis")

    response = requests.get(KEYCLOAK_URL)
    jwks = response.json()

    for key in jwks["keys"]:
        if key["kid"] == kid:
            public_key = json.dumps(key)
            break
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(public_key)
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")
    print(f"public pem key to be stored in redis: {public_key_pem}")
    redis_client.setex(kid,20, public_key_pem)
    return public_key


# Verify JWT
def verify_jwt(token_text):
    token = extract_token(token_text)
    print(f"JWT Token: {token}")
    public_key = get_public_key(token)
    try:
        decoded_token = jwt.decode(token, public_key, algorithms=["RS256"], options={"verify_aud": False})
        print("✅ JWT Verified Successfully!")
        print(json.dumps(decoded_token, indent=2))
        if 'create-orders-client-role' in decoded_token.get("resource_access", {}).get("create-orders-client", {}).get("roles", []):
            if 'create_orders_scope' in decoded_token.get('scope', ''):
                # User is authorized to create orders
                print("✅ User is authorized to create orders")
        return False
    except jwt.ExpiredSignatureError:
        print("❌ Token has expired")
    except jwt.InvalidTokenError:
        print("❌ Invalid Token")

def get_cashed_key(kid):
    retrieved_pem = redis_client.get(kid)

    if retrieved_pem:
        retrieved_pem = retrieved_pem.decode("utf-8")
        print(f"Retrieved pem: {retrieved_pem}")
        retrieved_pem_bytes = retrieved_pem.encode("utf-8")
        retrieved_public_key = serialization.load_pem_public_key(retrieved_pem_bytes)
        return retrieved_public_key
    else:
        print(f"Public key for {kid} not found in Redis")
        return None

def retrieve_kid_from_token(token):
    kid = None
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        print(f"Key ID (kid): {kid}")
        return kid
    except jwt.InvalidTokenError:
        raise ValueError("jwt token is invalid")
def extract_token(token_text):
    match = re.search(r'Bearer\s+([\w\.-]+)', token_text)
    token = None
    if match:
        token = match.group(1)
        print("Extracted Token:", token)
    else:
        print("Token not found")
    return token

if __name__ == '__main__':
    verify_jwt(JWT_TOKEN_TEXT)