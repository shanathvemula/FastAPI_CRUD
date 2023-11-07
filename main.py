# Importing Libraries
import dateutil.utils
import jwt
import pymongo

import uvicorn
from fastapi import FastAPI, APIRouter, status, HTTPException, Request, Response, Depends, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from typing import Optional, Annotated
from uuid import UUID, uuid4
# from pymongo import MongoClient
from Schemas import User, Blog, UserCreate, SecretStr
from database import DBClient, ObjectId, DBName, Collection, ASCENDING, UserCollection
from authentication import AccessToken, RefreshToken, VerifyToken, jwtBearer, decodeJWT
from California_House_Pricing.California_House_Pricing import CHP_Prediction, CHP

# CORSMiddleware for Cross-Origin Resource Sharing
from fastapi.middleware.cors import CORSMiddleware

# from fastapi.security

# Initializing the App
app = FastAPI()

origins = ['*']
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=['*'],
                   allow_headers=['*'])

templates = Jinja2Templates(directory="templates")


# Default Route
@app.get("/")  # decorator for the get request
def home(request: Request):
    return templates.TemplateResponse('home.html', {"request": request})


class testDepends:
    def __init__(self, dbname: str):
        self.dbname = dbname

    async def __call__(self, request: Request):
        # print(self.dbname)
        # print(request.headers)
        data = decodeJWT(request.headers['authorization'].replace('Bearer ', ''))
        user = DBClient[self.dbname]['user'].find_one({'username': data['username']})
        # print(user['Additional']['Login'])
        # print(request.headers['host'])
        if request.headers['host'] not in user['Additional']['Login'] and len(user['Additional']['Login']) == 2:
            raise HTTPException(status_code=403, detail="You are login device limit over")
        elif request.headers['host'] not in user['Additional']['Login']:
            user['Additional']['Login'].append(request.headers['host'])
            u = DBClient[self.dbname]['user'].update_one({'_id': user['_id']}, {"$set": user})
            # print(u.raw_result)
        # raise jwt.InvalidAudienceError()
        # user['Additional'] = [{'Login': [request.headers['host']]}]
        # print(user)
        # u = DBClient[self.dbname]['user'].update_one({'_id': user['_id']}, {"$set": user})
        # print(u.raw_result)


# Connecting to db
# DBClient = MongoClient('mongodb://localhost:27017/')

# print(list(DBClient[DBName]['user'].find()))
@app.post('/access-token')
def token(cred: dict, request: Request):
    cred['host'] = request.headers['host']
    # user = list(
    #     DBClient[DBName]['user'].find({'$and': [{'username': cred['username']}, {'password': cred['password']}]}))
    # if len(user) == 1:
    return AccessToken(cred)
    # else:
    #     return {"Error": "With given credential user doesn't exists"}


@app.post('/refresh-token')  # , dependencies=[Depends(testDepends(DBName))]
def Refresh_Token(request: dict):
    return RefreshToken(request)
    # try:
    #     if request['token']:
    #         vt = RefreshToken(request)
    #         return JSONResponse(status_code=200, content=vt)
    #     else:
    #         raise ValueError("Token required")
    # except Exception as e:
    #     if str(e) == 'Signature has expired':
    #         return JSONResponse(content={"Error": str(e)}, status_code=401)
    #     return JSONResponse(content={"Error": str(e)}, status_code=400)


@app.post('/verify-token')
def Verify_Token(request: dict):
    return VerifyToken(request)
    # try:
    #     if request['token']:
    #         vt = VerifyToken(request)
    #         return JSONResponse(status_code=200, content=vt)
    #     else:
    #         raise ValueError("Token required")
    # except Exception as e:
    #     if str(e) == 'Signature has expired':
    #         return JSONResponse(content={"Error": str(e)}, status_code=401)
    #     return JSONResponse(content={"Error": str(e)}, status_code=400)


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
@app.get('/blogs/', dependencies=[Depends(jwtBearer()), Depends(testDepends(dbname=DBName))])
def get_blogs_list(page: int, size: int):
    try:
        res = list(DBClient[DBName][Collection].find(sort=[('id', ASCENDING)]).skip(page * size).limit(size))
        count = len(list(DBClient[DBName][Collection].find()))
        for i in res:
            i['_id'] = str(i['_id'])
        return dict(count=count, Page=page, data=res)
    except Exception as e:
        return e


@app.post('/blogs/', dependencies=[Depends(jwtBearer()), Depends(testDepends(dbname=DBName))])
def filter_blogs(data: dict, request: Request):
    try:
        # print(request.headers)
        page = data['page']
        size = data['size']
        filters_data = data['filters']
        filters = [{k: filters_data[k]} for k in filters_data.keys()]
        count = len(list(DBClient[DBName][Collection].find({'$and': filters})))
        res = list(DBClient[DBName][Collection].find({'$and': filters}).skip(page * size).limit(size))
        for i in res:
            i['_id'] = str(i['_id'])
        return dict(count=count, Page=page, data=res)
    except Exception as e:
        return JSONResponse({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@app.put('/blogs/')
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


@app.patch('/blogs/')
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


@app.post("/user/", status_code=status.HTTP_201_CREATED)  # ,
# dependencies=[Depends(jwtBearer()), Depends(testDepends(dbname=DBName))])
def create_user(user: UserCreate, request: Request):
    try:
        usr = dict(user)
        if usr['Additional'] == ['string']:
            usr['Additional'] = {}
        print(request.headers)
        res = DBClient[DBName][UserCollection].insert_one(dict(user))
        usr['_id'] = str(res.inserted_id)
        # print(user)
        # created_user = User(user)
        # return created_user
        return usr
    except Exception as e:
        print(e)
        return JSONResponse({"Error": "Document is not created"}, status_code=status.HTTP_400_BAD_REQUEST)


@app.post("/chp_predict_api/")
def CHP_Predict_API(request: Request, chp: CHP):
    result = CHP_Prediction(chp)
    return JSONResponse({"California_House_Pricing": result})


@app.get("/chp")
def chp_home(request: Request):
    return templates.TemplateResponse('California_House_Prediction.html', {"request": request})


@app.post("/chp_predict/", response_class=HTMLResponse)
async def chp_predict(request: Request, MedInc: Annotated[str, Form()], HouseAge: Annotated[str, Form()],
                      AveRooms: Annotated[str, Form()], AveBedrms: Annotated[str, Form()],
                      Population: Annotated[str, Form()], AveOccup: Annotated[str, Form()],
                      Latitude: Annotated[str, Form()], Longitude: Annotated[str, Form()]):
    # print("MedInc", MedInc)
    data = {
        "MedInc": MedInc,
        "HouseAge": HouseAge,
        "AveRooms": AveRooms,
        "AveBedrms": AveBedrms,
        "Population": Population,
        "AveOccup": AveOccup,
        "Latitude": Latitude,
        "Longitude": Longitude
    }
    result = CHP_Prediction(CHP(**data))
    return templates.TemplateResponse('California_House_Prediction.html',
                                      {"request": request, "prediction_text": result})


if __name__ == "__main__":
    uvicorn.run("main:app", host='127.0.0.1', port=8000, reload=True, workers=3)
