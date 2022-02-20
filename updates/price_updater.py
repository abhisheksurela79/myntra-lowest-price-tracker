import asyncio
import pymongo
from Date.get_time import date_now
from Myntra.FetchedData import fetched_from_myntra
from DB.products.structured_data import StructuredProductData
from DB.products.products_db import AllProductsDB
from my_token import cred
from DB.users.users_db import AllUsersDB
import random


class PriceUpdater:
    def __init__(self):
        client = pymongo.MongoClient(cred()['db_string'])
        db = client["chats"]
        self.collection = db["All Products"]

    def find_product(self, _id):
        data = self.collection.find_one({"_id": _id})
        return data

    async def update_prices(self, bot, event):
        while True:
            for document in self.collection.find():
                data_from_myntra = fetched_from_myntra(product_code=document['_id'], product_url=document['URL'])
                # print("started")
                # print(data_from_myntra)
                # print()
                # print(document)

                img_url = f"[‎]({data_from_myntra['image']})"
                brand_formatted_link = f"[{data_from_myntra['product_name']}]({data_from_myntra['product_url']})"
                discounted_price = data_from_myntra['discounted_Price']
                mrp = data_from_myntra['MRP']
                rating = data_from_myntra['average_Rating']
                available_count = data_from_myntra['available_Count']

                if document['discounted_price'] != data_from_myntra['discounted_Price']:
                    msg = f"❗️❗️ Price Changed ❗️❗️❗️\n\n" \
                          f" **Brand: ** {brand_formatted_link}\n" \
                          f" **Before => **₹{document['discounted_price']}\n" \
                          f" **Now** => ₹{discounted_price}\n" \
                          f" **Available Count: ** {available_count}"

                    msg_to_send = f"{img_url} {msg}"

                    users_following_this_product = AllUsersDB().get_all_users(product_id=document['product_code'])
                    for user in users_following_this_product:
                        try:
                            # Send alert to all users who subscribed this product
                            await bot.send_message(user, msg_to_send, link_preview=True)
                            await asyncio.sleep(random.randint(60, 120))

                        except Exception as f:
                            print(f)

                    # append new dataset to structured data because product price is changed
                    structured_data = StructuredProductData().find_product(_id=document["_id"])

                    new_value = {"$push": {'data': {"discounted_price": discounted_price,
                                                    "MRP": mrp,
                                                    "total_available": available_count,
                                                    "rating": rating,
                                                    "fetched_date": date_now()['date'],
                                                    "fetched_time": date_now()['time']}}}

                    StructuredProductData().append_new_data(_id=structured_data['_id'], new_data=new_value)

                # updating new values to All product DB
                data = {"fetched_date": date_now()['date'],
                        'fetched_time': date_now()['time'],
                        'discounted_price': discounted_price,
                        'MRP': mrp,
                        'total_available': available_count,
                        'rating': rating}

                AllProductsDB().update_new_values(_id=document["_id"], data=data)

                await asyncio.sleep(random.randint(30, 120))  # Sleeping random seconds to update each products in DB

            await asyncio.sleep(random.randint(1800, 3600))  # Sleeping random seconds to update with next iteration

