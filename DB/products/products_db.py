from DB.temp.temporary_products import TemporaryProducts
from DB.products.structured_data import StructuredProductData
from Date.get_time import date_now
from my_token import cred
import pymongo


class AllProductsDB:
    def __init__(self):
        client = pymongo.MongoClient(cred()['db_string'])
        db = client["chats"]
        self.collection = db["All Products"]

    def find_product(self, _id):
        data = self.collection.find_one({"_id": _id})
        return data

    def add_new_product(self, event):
        from_temp = TemporaryProducts().find_product(_id=event.chat.id)
        find_existing_product = self.find_product(_id=from_temp['product_code'])
        contributor = {"name": event.chat.first_name, "chat_id": event.chat_id}

        if find_existing_product is None:

            data_to_add = {'_id': from_temp['product_code'],
                           'product_code': from_temp['product_code'],
                           'product_brand': from_temp['product_brand'],
                           'URL': from_temp['URL'],
                           'discounted_price': from_temp['discounted_price'],
                           'MRP': from_temp['MRP'],
                           'total_available': from_temp['total_available'],
                           'rating': from_temp['rating'],
                           'fetched_date': from_temp['fetched_date'],
                           'fetched_time': from_temp['fetched_time'],
                           'contributors': [contributor]}

            self.collection.insert_one(data_to_add)  # Adding new data

            to_structured = {'_id': from_temp['product_code'],
                             'product_code': from_temp['product_code'],
                             'product_brand': from_temp['product_brand'],
                             'URL': from_temp['URL'],
                             'since_date': date_now()['date'],
                             'since_time': date_now()['time'],
                             'data': [{'discounted_price': from_temp['discounted_price'],
                                       'MRP': from_temp['MRP'],
                                       'total_available': from_temp['total_available'],
                                       'rating': from_temp['rating'],
                                       'fetched_date': from_temp['fetched_date'],
                                       'fetched_time': from_temp['fetched_time']}]
                             }

            StructuredProductData().add_new_product(data=to_structured)


        elif not find_existing_product is None:
            users = [_['chat_id'] for _ in find_existing_product['contributors']]

            if event.chat.id not in users:  # verifying chat.id is unique and doesn't exist in users: list
                new_value = {"$push": {'contributors': contributor}}

                # adding unique chat.id in added_by array, All products
                self.collection.update_one({"_id": find_existing_product['_id']}, new_value)

    def update_new_values(self, _id, data):
        self.collection.update_many({"_id": _id}, {"$set": data}, upsert=True)
