# Importing Libraries
import dateutil.utils
import pymongo

import uvicorn
from fastapi import FastAPI, APIRouter, status
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
# from pymongo import MongoClient
from Schemas import User, Blog, UserCreate
from database import DBClient, ObjectId, DBName, Collection, ASCENDING

# Initializing the App
app = FastAPI()


# Connecting to db
# DBClient = MongoClient('mongodb://localhost:27017/')


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
@app.post("/blog/", status_code=status.HTTP_201_CREATED)
def create_blog(request: Blog):
    try:
        bl = dict(request)
        res = DBClient[DBName][Collection].insert_one(dict(bl))
        bl['_id'] = str(res.inserted_id)
        return bl
    except Exception as e:
        return {"Error": "Document is not created"}


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
        return {"Error": str(e)}


# Update By Oid
@app.put('/blog/{Oid}')
@app.patch('/blog/{Oid}')
def blog_update(Oid, request: Blog):
    try:
        res = DBClient[DBName][Collection].update_one({'_id': ObjectId(Oid)}, {'$set': dict(request)})
        if res.raw_result['updatedExisting']:
            return {"Message": "Data Updated Successfully"}
        return {"Error": "Data Not Updated"}
    except Exception as e:
        return {"Error": str(e)}


# Delete By Oid
@app.delete('/blog/{Oid}')
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


@app.post('/blogs/')
def filter_blogs(request: dict):
    page = request['page']
    size = request['size']
    data = request['filters']
    filters = [{k: data[k]} for k in data.keys()]
    count = len(list(DBClient[DBName][Collection].find({'$and': filters})))
    res = list(DBClient[DBName][Collection].find({'$and': filters}).skip(page * size).limit(size))
    for i in res:
        i['_id'] = str(i['_id'])
    return dict(count=count, Page=page, data=res)


@app.put('/blogs/')
def search_blogs(request: dict):
    page = request['page']
    size = request['size']
    data = request['filters']
    filters = [{k: data[k]} for k in data.keys()]
    count = len(list(DBClient[DBName][Collection].find({'$or': filters})))
    res = list(DBClient[DBName][Collection].find({'$or': filters}).skip(page * size).limit(size))
    for i in res:
        i['_id'] = str(i['_id'])
    return dict(count=count, Page=page, data=res)


@app.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    created_user = User(**user.model_dump())
    return created_user


if __name__ == "__main__":
    uvicorn.run("main:app", host='127.0.0.1', port=8000, reload=True, debug=True, workers=3)
