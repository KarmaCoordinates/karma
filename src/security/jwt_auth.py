import datetime
import jwt
import __configs
from starlette.authentication import AuthenticationBackend, AuthenticationError, AuthCredentials, SimpleUser
import cachetools

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
        
            payload = decode_token(token)
            payload['auth_code']=token
            cache[payload["sub"]] = payload
            user = SimpleUser(payload["sub"])

            return AuthCredentials(["authenticated"]), user

        except AuthenticationError:
            return
        except ValueError:
            return

    
def create_access_token(subject: str, nonce: str, expires_in_days: 1):
    # Never put the emailed sign-in code in here: a JWT can be read by anyone who has it.
    # The nonce only links the token to the code kept on the server (security/otp_store.py).
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=expires_in_days)
    to_encode = {"exp": expire, "sub": subject, "nonce": nonce}
    jwt_secret = __configs.get_config().jwt_secret
    jwt_algorithm=__configs.get_config().jwt_algorithm
    encoded_jwt = jwt.encode(to_encode, jwt_secret, algorithm=jwt_algorithm)
    return encoded_jwt

def decode_token(token: str):
    try:
        return jwt.decode(token, __configs.get_config().jwt_secret, __configs.get_config().jwt_algorithm)    
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")

