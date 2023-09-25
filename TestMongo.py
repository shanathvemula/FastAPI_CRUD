# Pymongo
from pymongo import MongoClient, DESCENDING, ASCENDING
from bson import ObjectId

# Connecting to database
client = MongoClient("mongodb://localhost:27017/")

# Getting list of database names
dbs = client.list_database_names()

# getting list of Database Names with respective collection names
# info = [{'dbname': db, "collection_names": [collection for collection in client[db].list_collection_names()]} for db in
#         client.list_database_names()]
# print(info)

db = 'Tdb'  # input('Enter Database Name: ')
collection = 'Tcollection'  # input('Enter Collection Name: ')

# Inserting a record using insert_one function
# client[db][collection].insert_one({"name": "shanath"})  ## Here 'Tdb' is Database Name, 'Tcollection' is collection Name

# Inserting multiple records using insert_many function
# client[db][collection].insert_many([{"name": "Shanath"}, {"name": "Kumar"}, {"name": "Vemula"}])  ## Here 'Tdb' is Database Name, 'Tcollection' is collection Name

# # Getting all the documents from given database and collection using find()
# print(list(client[db][collection].find()))
#
# # Getting particular the documents from given database and collection using find_one()
# print(client[db][collection].find_one({'name': 'Shanath'}))
#
# # Getting particular the documents from given database and collection using find()
# print(list(client[db][collection].find({'name': 'Shanath'})))
#
# # Getting recently inserted document using '_id' column
# print(client[db][collection].find_one(sort=[('_id', DESCENDING)]))

# Getting documents descending order using '_id' column
# print(list(client[db][collection].find(sort=[('_id', DESCENDING)])))

# Updating document
# Oid = '650bc75d82181a2535fd6037'
# k = client[db][collection].update_one({'_id': ObjectId(Oid)}, {'$set': {"name": "Shanath", "age": 26}})
# if k.raw_result['updatedExisting']:
#     print("Document is Updated")
#
# # Updating many documents
# # name = 'Shanath'
# k = client[db][collection].update_many({'name': 'Shanath'}, {'$set': {"name": "Shanath", "age": 28}})
# if k.raw_result['updatedExisting']:
#     print("Documents are Updated")

# # Deleting a document
# d = client[db][collection].delete_one({'_id': ObjectId(Oid)})
# if d.deleted_count:
#     print(d.deleted_count)
#     print("Document is deleted")
#
# # Deleting many documents using filter
# d = client[db][collection].delete_many({'name': 'Shanath'})
# if d.deleted_count:
#     print(d.deleted_count)
#     print("Multiple documents are deleted")
#
# # Deleting all documents
# d = client[db][collection].delete_many({})
# if d.deleted_count:
#     print(d.deleted_count)
#     print("All documents are deleted")

print(list(client['blogs']['blog'].find(sort=[('_id', DESCENDING)])))

# Pagination
# print(list(client[db][collection].find({}).skip(2).limit(10)))


client.drop_database(db)
