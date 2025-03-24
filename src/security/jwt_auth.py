import datetime
import jwt
import _configs
from starlette.authentication import AuthenticationBackend, AuthenticationError, AuthCredentials, SimpleUser
import cachetools
from fastapi import Request, Response
import json

cache = cachetools.TTLCache(maxsize=1000, ttl=120)

class JWTAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        if "Authorization" not in conn.headers:
            return
        
        auth = conn.headers["Authorization"]
        try:
            scheme, token = auth.split()
            if scheme.lower() != "bearer":
                return
        except ValueError:
            return
        
        payload = decode_token(token)
        payload['auth_code']=token
        cache[payload["sub"]] = payload
        user = SimpleUser(payload["sub"])

        return AuthCredentials(["authenticated"]), user
    

    # async def dispatch(self, request: Request, call_next):
    #     response = await call_next(request)
    #     if response.headers.get('content-type') == 'application/json':
    #         existing_body = b""
    #         async for chunk in response.body_iterator:
    #             existing_body += chunk

    #         try:
    #             response_body = json.loads(existing_body.decode('utf-8'))
    #             modified_response_body = json.dumps(response_body).encode('utf-8')

    #             response = Response(
    #                 content=modified_response_body,
    #                 status_code=response.status_code,
    #                 headers=response.headers,
    #                 media_type=response.media_type
    #             )
    #             response.headers['Content-Length'] = str(len(modified_response_body))
    #         except json.JSONDecodeError:
    #             pass

    #     return response    

def create_access_token(subject: str, otp: str, expires_in_days: 1):
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=expires_in_days)
    to_encode = {"exp": expire, "sub": subject, "otp": otp}
    jwt_secret = _configs.get_config().jwt_secret
    jwt_algorithm=_configs.get_config().jwt_algorithm
    encoded_jwt = jwt.encode(to_encode, jwt_secret, algorithm=jwt_algorithm)
    return encoded_jwt

def decode_token(token: str):
    try:
        return jwt.decode(token, _configs.get_config().jwt_secret, _configs.get_config().jwt_algorithm)    
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")

