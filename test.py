import pymongo
from urllib.parse import quote_plus

username = quote_plus('shanathvemula')
password = quote_plus('Vemula_1606')
cluster = 'wdzcxu9'
authSource = '<authSource>'
authMechanism = '<authMechanism>'

uri = 'mongodb://' + username + ':' + password + '@' + cluster # + '/?authSource=' + authSource + '&authMechanism=' + authMechanism

client = pymongo.MongoClient(uri)
print(uri)

result = client["<dbName"]["<collName>"].find()

# print results
for i in result:
    print(i)
