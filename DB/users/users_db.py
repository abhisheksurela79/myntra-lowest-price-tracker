# from DB.temp.temporary_products import TemporaryProducts
from my_token import cred
import pymongo


class AllUsersDB:
    def __init__(self):
        client = pymongo.MongoClient(cred()['db_string'])
        db = client["chats"]
        self.collection = db["All Users"]

    def find_user(self, _id):
        data = self.collection.find_one({"_id": _id})
        return data

    def new_user(self, chat_id, name):
        if self.find_user(_id=chat_id) is None:  # Verifying if user doesn't exist in DB
            data = {"_id": chat_id, "name": name, "products": []}
            self.collection.insert_one(data)

        elif not self.find_user(_id=chat_id) is None:  # User is already registered | Updating name only
            self.collection.update_one({"_id": self.find_user(_id=chat_id)['_id']},
                                       {"$set": {"name": name}}, upsert=True)

    def add_product(self, event, product_id, product_name, product_url):
        new_value = {"$push": {'products': {'product_id': product_id, 'product_name': product_name,
                                            'product_url': product_url}}}

        self.collection.update_one({"_id": event.chat.id}, new_value)  # appending unique product


    def delete_product(self, chat_id, product_id):
        self.collection.update_one({"_id": chat_id}, {"$pull": {'products': {'product_id': product_id}}})

    def get_all_users(self, product_id):
        users = []
        for document in self.collection.find():
            for _ in document['products']:
                if _['product_id'] == product_id:
                    users.append(document['_id'])

        users = list(set(users))

        return users


