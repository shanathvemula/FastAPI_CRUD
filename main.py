# Importing Libraries
import dateutil.utils
import pymongo

import uvicorn
from fastapi import FastAPI, APIRouter, status, HTTPException, Request, Response, Depends
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
# from pymongo import MongoClient
from Schemas import User, Blog, UserCreate, SecretStr
from database import DBClient, ObjectId, DBName, Collection, ASCENDING
from authentication import AccessToken, RefreshToken, VerifyToken, jwtBearer

# from fastapi.security

# Initializing the App
app = FastAPI()


# Connecting to db
# DBClient = MongoClient('mongodb://localhost:27017/')

# print(list(DBClient[DBName]['user'].find()))
@app.post('/access-token')
def token(cred: dict):
    user = list(
        DBClient[DBName]['user'].find({'$and': [{'username': cred['username']}, {'password': cred['password']}]}))
    if len(user) == 1:
        return AccessToken(user[0])
    else:
        return {"Error": "With given credential user doesn't exists"}


@app.post('/refresh-token')
def Refresh_Token(request: dict):
    try:
        if request['token']:
            vt = RefreshToken(request)
            return JSONResponse(status_code=200, content=vt)
        else:
            raise ValueError("Token required")
    except Exception as e:
        if str(e) == 'Signature has expired':
            return JSONResponse(content={"Error": str(e)}, status_code=401)
        return JSONResponse(content={"Error": str(e)}, status_code=400)


@app.post('/verify-token')
def Verify_Token(request: dict):
    try:
        if request['token']:
            vt = VerifyToken(request)
            return JSONResponse(status_code=200, content=vt)
        else:
            raise ValueError("Token required")
    except Exception as e:
        if str(e) == 'Signature has expired':
            return JSONResponse(content={"Error": str(e)}, status_code=401)
        return JSONResponse(content={"Error": str(e)}, status_code=400)

# Default Route
@app.get("/")  # decorator for the get request
def home():
    return {"Message": "Request call from get"}


@app.post('/')
def home_post():
    return {"Message": "Request call from post"}


@app.get("/items/")
def read_item(item_id: int, q: str):
    return {"item_id": item_id, "q": q}


# CRUD Operations
# Create Operation
@app.post("/blog/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(jwtBearer())])
def create_blog(blog: Blog, request: Request):
    try:
        bl = dict(blog)
        print(bl)
        res = DBClient[DBName][Collection].insert_one(dict(blog))
        bl['_id'] = str(res.inserted_id)
        return bl
    except Exception as e:
        return JSONResponse({"Error": "Document is not created"}, status=status.HTTP_400_BAD_REQUEST)


# Getting By Oid
@app.get('/blog/{Oid}', status_code=status.HTTP_200_OK)
def get_blog(Oid):
    try:
        res = DBClient[DBName][Collection].find_one({'_id': ObjectId(Oid)})
        if res == None:
            return {"Message": "Document does n't exists with " + str(Oid)}
        res['_id'] = str(res['_id'])
        return res
    except Exception as e:
        return JSONResponse({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Update By Oid
@app.put('/blog/{Oid}', dependencies=[Depends(jwtBearer())])
@app.patch('/blog/{Oid}', dependencies=[Depends(jwtBearer())])
def blog_update(Oid, blog: Blog):
    try:
        res = DBClient[DBName][Collection].update_one({'_id': ObjectId(Oid)}, {'$set': dict(blog)})
        if res.raw_result['updatedExisting']:
            return {"Message": "Data Updated Successfully"}
        return {"Error": "Data Not Updated"}
    except Exception as e:
        return JSONResponse({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Delete By Oid
@app.delete('/blog/{Oid}', dependencies=[Depends(jwtBearer())])
def blog_delete(Oid):
    res = DBClient[DBName][Collection].delete_one({'_id': ObjectId(Oid)})
    if res.deleted_count:
        return {"Message": "Blog is deleted"}
    else:
        return {"Error": "Data is not deleted"}


# Additional Operations
# List Operations
@app.get('/blogs/', status_code=status.HTTP_200_OK)
def get_blogs_list(page: int, size: int):
    res = list(DBClient[DBName][Collection].find(sort=[('id', ASCENDING)]).skip(page * size).limit(size))
    count = len(list(DBClient[DBName][Collection].find()))
    for i in res:
        i['_id'] = str(i['_id'])
    return dict(count=count, Page=page, data=res)


@app.post('/blogs/', dependencies=[Depends(jwtBearer())])
def filter_blogs(data: dict, request: Request):
    print(request.headers)
    page = data['page']
    size = data['size']
    filters_data = data['filters']
    filters = [{k: filters_data[k]} for k in filters_data.keys()]
    count = len(list(DBClient[DBName][Collection].find({'$and': filters})))
    res = list(DBClient[DBName][Collection].find({'$and': filters}).skip(page * size).limit(size))
    for i in res:
        i['_id'] = str(i['_id'])
    return dict(count=count, Page=page, data=res)


@app.put('/blogs/', dependencies=[Depends(jwtBearer())])
def search_blogs(data: dict, request: Request):
    print(request.headers)
    page = data['page']
    size = data['size']
    filters_data = data['filters']
    filters = [{k: filters_data[k]} for k in filters_data.keys()]
    count = len(list(DBClient[DBName][Collection].find({'$or': filters})))
    res = list(DBClient[DBName][Collection].find({'$or': filters}).skip(page * size).limit(size))
    for i in res:
        i['_id'] = str(i['_id'])
    return dict(count=count, Page=page, data=res)


@app.patch('/blogs/', dependencies=[Depends(jwtBearer())])
def list_blogs_in_date_range(request: dict):
    page = request['page']
    size = request['size']
    count = len(
        list(DBClient[DBName][Collection].find(
            {'published_at': {'$gt': datetime.strptime(request['startdate'], '%Y-%m-%d'),
                              "$lt": datetime.strptime(request['enddate'], '%Y-%m-%d')}})))  # '2032-04-25'
    res = list(DBClient[DBName][Collection].find({'published_at': {
        '$gt': datetime.strptime(request['startdate'], '%Y-%m-%d'),
        '$lt': datetime.strptime(request['enddate'], '%Y-%m-%d')}}).skip(page * size).limit(size))
    for i in res:
        i['_id'] = str(i['_id'])
    return dict(count=count, Page=page, data=res)


@app.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    created_user = User(**user.model_dump())
    return created_user


if __name__ == "__main__":
    uvicorn.run("main:app", host='127.0.0.1', port=8000, reload=True, debug=True, workers=3)
