# This file is responsible for Login, encoding, decoding and returning jwt
import datetime
import time
import jwt
from Schemas import User
import datetime
from database import DBClient, DBName, UserCollection
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

secret = 'c427efa41a05507e7bd9637270ff5a20db6ad20f2dbb0cf8d5bbf5af4f89aea5'
algorithm = 'HS256'
AccessTimeDelta = 60  # Seconds
RefreshTimeDelta = 600  # Seconds


# Generating Access Token
def AccessToken(cred: dict):
    try:
        user = list(
            DBClient[DBName][UserCollection].find({'$and': [
                {'$or': [{'username': cred['username']}, {'phoneno': cred['username']}, {'email': cred['username']}]},
                {'password': cred['password']}]}))
        # print(user[0]['Additional'] == {} or 'Login' not in user[0]['Additional'].keys())
        if user[0]['Additional'] == {} or 'Login' not in user[0]['Additional'].keys():
            user[0]['Additional']['Login'] = [cred['host']]
            DBClient[DBName][UserCollection].update_one({'_id': user[0]['_id']}, {'$set': user[0]})
        # print(user[0]['Additional']['Login'])
        # print((cred['host'] not in user[0]['Additional']['Login']) and (len(user[0]['Additional']['Login']) < 2))
        if cred['host'] not in user[0]['Additional']['Login'] and len(user[0]['Additional']['Login']) < 2:
            user[0]['Additional']['Login'].append(cred['host'])
            DBClient[DBName][UserCollection].update_one({'_id': user[0]['_id']}, {'$set': user[0]})

        if user and cred['host'] in user[0]['Additional']['Login']:
            encode = jwt.encode(
                {'username': user[0]['username'], 'iat': datetime.datetime.now(tz=datetime.timezone.utc),
                 'exp': datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
                     seconds=AccessTimeDelta)},
                key=secret,
                algorithm=algorithm)
            # print(datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=1))
            # print(encode)
            return {'token': encode}
        elif len(user[0]['Additional']['Login']) >= 2:
            raise MemoryError("You are login device limit over")
        else:
            return {"Error": "With given credential user doesn't exists"}

        # @wraps(f)
        # def decorated(*args, **kwargs):
        #     print("OK")
        #     return f
        # return decorated
    except Exception as e:
        return JSONResponse(content={"Error": str(e)}, status_code=400)


# Refresh Access Token
def RefreshToken(data):
    try:
        d = jwt.decode(data['token'], secret, algorithm)
        # print(d)
        encode = jwt.encode({'username': d['username'], 'iat': datetime.datetime.now(tz=datetime.timezone.utc),
                             'exp': datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
                                 seconds=RefreshTimeDelta)},
                            key=secret, algorithm=algorithm)
        return JSONResponse(content={'token': encode}, status_code=200)
    except jwt.ExpiredSignatureError as e:
        return JSONResponse(content={"Error": str(e)}, status_code=401)
    except Exception as e:
        return JSONResponse(content={"Error": str(e)}, status_code=400)


# Verify Access Token
def VerifyToken(data):
    try:
        d = jwt.decode(data['token'], secret, algorithm, verify_exp=data['token'])
        return JSONResponse(content=data, status_code=200)
    except jwt.ExpiredSignatureError as e:
        return JSONResponse(content={"Error": str(e)}, status_code=401)
    except Exception as e:
        return JSONResponse(content={"Error": str(e)}, status_code=400)


def decodeJWT(token: str) -> dict:
    try:
        token = token.replace(' ', '')
        decoded_token = jwt.decode(token, secret, algorithms=[algorithm])
        print(decoded_token["exp"])
        print(int(datetime.datetime.now().timestamp()))
        return decoded_token if decoded_token["exp"] >= int(datetime.datetime.now().timestamp()) else None
    except Exception as e:
        return str(e)


# Verifying access token from the Headers
# This class helps to check whether the request is authorized or not using the HTTPBearer
class jwtBearer(HTTPBearer):
    def __int__(self, auto_Error: bool = True):
        super(jwtBearer, self.__init__(auto_error=auto_Error))

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(jwtBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == 'Bearer':
                raise HTTPException(status_code=403, detail="Invalid or Expered Token")
            data = decodeJWT(credentials.credentials)
            if data == "Signature has expired":
                raise HTTPException(status_code=403, detail="Signature has expired")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid or Expired Token")

    def verify_jwt(self, jwtoken: str):
        isTokenValid: bool = False  # Default Flag
        payload = decodeJWT(jwtoken)
        if payload:
            isTokenValid = True
        return isTokenValid
