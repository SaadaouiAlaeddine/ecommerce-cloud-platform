import jwt
import requests
import json
import logging
import re
import connectors.keycloak as keycloak
from jwt.algorithms import RSAAlgorithm
from cryptography.hazmat.primitives import serialization
from connectors.redis_connection import RedisConnection
from functools import wraps
from flask import request

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
redis_client = RedisConnection().get_client()


# Fetch Public Key from JWT Token
def get_public_key(jwt_token):
    kid = retrieve_kid_from_token(jwt_token)
    public_key = get_cashed_key(kid)
    if public_key:
        logger.info(f"Public key for {kid} found in Redis")
        return public_key
    else:
        logger.info(f"Public key for {kid} not found in Redis")

    response = requests.get(keycloak.KEYCLOAK_URL)
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
    logger.info(f"The fresh returned public key is: {public_key}")
    redis_client.setex(kid, 20, public_key_pem)
    return public_key

def get_cashed_key(kid):
    logger.info(f"Retrieving public key for {kid} from Redis")
    retrieved_pem = redis_client.get(kid)
    if retrieved_pem:
        logger.info(f"Retrieved public pem key {retrieved_pem:}")
        retrieved_public_key = serialization.load_pem_public_key(retrieved_pem.encode("utf-8"))
        return retrieved_public_key
    else:
        logger.info(f"Public key for {kid} not found in Redis")
        return None

def retrieve_kid_from_token(jwt_token):
    kid = None
    try:
        header = jwt.get_unverified_header(jwt_token)
        kid = header.get("kid")
        logger.info(f"Key ID (kid): {kid}")
        return kid
    except jwt.InvalidTokenError:
        raise ValueError("jwt token is invalid")

# Verify JWT
def verify_jwt(jwt_token):
    public_key = get_public_key(jwt_token)
    try:
        decoded_token = jwt.decode(jwt_token, public_key, algorithms=["RS256"], options={"verify_aud": False})
        logger.info("JWT Verified Successfully!")
        logger.info(json.dumps(decoded_token, indent=2))
        if 'order-creator-role' in decoded_token.get('scope', ''):
                # User is authorized to create orders
                logger.info("User is authorized to create orders")
                return True
        else:
            raise ValueError("User is not authorized to create orders")
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid Token")


def validate_jwt(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token_text = request.headers.get("Authorization")
        logger.info(f"Authorization text: {token_text}")
        match = re.search(r'Bearer\s+([\w\.-]+)', token_text)
        if match:
            token = match.group(1)
            logger.info(f"Authorization token: {token}")
        else:
            raise ValueError("Authorization token missing")

        if verify_jwt(token):
            return func(*args, **kwargs)

    return wrapper