from my_token import cred
import pymongo


class TemporaryProducts:
    def __init__(self):
        client = pymongo.MongoClient(cred()['db_string'])
        db = client["chats"]
        self.collection = db["Temporary Products"]

    def find_product(self, _id):
        data = self.collection.find_one({"_id": _id})
        return data

    def add_temporary_product(self, data):
        self.collection.insert_one(data)

    def delete_temporary_product(self, _id):
        self.collection.delete_one({'_id': _id})


