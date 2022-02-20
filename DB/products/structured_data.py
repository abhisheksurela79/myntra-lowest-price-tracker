import json
from telethon import Button
from telethon.errors import MessageTooLongError

from my_token import cred
import pymongo
import tempfile


class StructuredProductData:
    def __init__(self):
        client = pymongo.MongoClient(cred()['db_string'])
        db = client["chats"]
        self.collection = db["Structured Product Data"]

    def find_product(self, _id):
        data = self.collection.find_one({"_id": _id})
        return data

    def add_new_product(self, data):
        self.collection.insert_one(data)  # Adding new data

    def append_new_data(self, _id, new_data):
        self.collection.update_many({"_id": _id}, new_data)

    async def return_json(self, bot, event, product_id, item_name):
        data = self.find_product(_id=product_id)
        json_object = json.dumps(data, indent=8)

        try:
            keyboard = [Button.inline(f"Back to main menu", b"main_menu_back")]
            await event.edit(f"Fetching Since Targeting: {item_name}\n\n"
                             f"`{json_object}`", link_preview=False, buttons=keyboard)

        except MessageTooLongError:
            keyboard = [Button.inline(f"Back to main menu", b"main_menu_back")]
            await event.edit(f"Fetching Since Targeting: {item_name}", link_preview=False, buttons=keyboard)

        finally:
            await bot.send_message(event.chat.id, f"{data['product_brand']}_{data['product_code']}",
                                   file=json_object.encode())





