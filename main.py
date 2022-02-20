from telethon import TelegramClient, events, Button
from DB.products.products_db import AllProductsDB
from DB.products.structured_data import StructuredProductData
from DB.temp.temporary_products import TemporaryProducts
from DB.users.users_db import AllUsersDB
from my_token import cred
from Myntra.FetchedData import fetched_from_myntra
from Date.get_time import date_now
import re
from updates.price_updater import PriceUpdater

bot = TelegramClient("cache/bot", api_id=cred()['api_id'],
                     api_hash=cred()['api_hash']).start(bot_token=cred()['bot_token'])


@bot.on(events.NewMessage(func=lambda e: e.is_private and e.text == "/only_admin_for_me" and e.chat.id == 1114526265))
async def starts(event):
    await bot.send_message(event.chat.id, "updating from now")
    await PriceUpdater().update_prices(bot, event)


@bot.on(events.NewMessage(func=lambda e: e.is_private and e.text == "/start"))
async def start(event):
    AllUsersDB().new_user(chat_id=event.chat.id, name=event.chat.first_name)

    msg = "I am bla bla.. bot 😁😁, please send me a product link"
    await bot.send_message(event.chat.id, f"**Hi {event.chat.first_name}**, {msg}", link_preview=False)


@bot.on(events.NewMessage(func=lambda e: e.is_private and "myntra.com" in re.findall('://www.([\w\-\.]+)', e.text)))
async def check_product(event):
    AllUsersDB().new_user(chat_id=event.chat.id, name=event.chat.first_name)
    product_url = re.search("(?P<url>https?://[^\s]+)", event.message.message).group("url")

    try:
        product_code = product_url.split("/")[-2]
        fetched_product = fetched_from_myntra(product_code=product_code, product_url=product_url)
        img_url = f"[‎]({fetched_product['image']})"
        brand_formatted_link = f"[{fetched_product['product_name']}]({product_url})"
        discounted_price = fetched_product['discounted_Price']
        mrp = fetched_product['MRP']
        rating = fetched_product['average_Rating']
        available_count = fetched_product['available_Count']

        msg = f"**Brand: ** {brand_formatted_link}\n" \
              f" **Discounted Price: ** ₹{discounted_price}\n" \
              f" **MRP: ** ₹~~{mrp}~~\n" \
              f" **Rating: ** {rating}\n" \
              f" **Available Count: ** {available_count}"

        msg_to_send = f"{img_url} {msg}"
        await bot.send_message(event.chat.id, msg_to_send, link_preview=True)

        if not TemporaryProducts().find_product(_id=event.chat.id) is None:
            TemporaryProducts().delete_temporary_product(_id=event.chat.id)

        data = {'_id': event.chat.id,
                'product_code': product_code,
                'product_brand': fetched_product['product_name'],
                'URL': product_url,
                'discounted_price': discounted_price,
                'MRP': mrp,
                'total_available': available_count,
                'rating': rating,
                'fetched_date': date_now()['date'],
                'fetched_time': date_now()['time'],
                'user_name': event.chat.first_name,
                'chat_id': event.chat.id}

        TemporaryProducts().add_temporary_product(data=data)  # Adding product to Temporary DB

        keyboard = [Button.inline("Yes", b"valid_product"), Button.inline("Nope", b"not_valid_product")]
        await bot.send_message(event.chat_id, "Is this a product you are trying to target?", buttons=keyboard)


    except Exception as e:
        print(e)
        dev = "[developer](tg://user?id=1114526265)"
        await bot.send_message(event.chat_id, "Invalid product link 🧐 __Probably link to the expected product is "
                                              "invalid__ or if you believe provided information "
                                              f" is correct you can contact to {dev}")


async def verify_if_following(event, temp_product, item_name, item_price):
    followed_products = [_['product_id'] for _ in AllUsersDB().find_user(_id=event.chat.id)['products']]

    if temp_product['product_code'] in followed_products:  # user already following this product
        keyboard = [Button.inline(f"Show options for {temp_product['product_brand']}", b"enter_main_menu")]
        await event.edit(f"**Good job {event.chat.first_name}.** The current price of {item_name} is **₹{item_price}**"
                         f" and you be notified whenever the price of this product changes 🤙", link_preview=False,
                         buttons=keyboard)

    elif not temp_product['product_code'] in followed_products:  # user is not following this product
        keyboard = [[Button.inline(f"Follow {temp_product['product_brand']}",
                                   b"follow_product")], [Button.inline("Some other day", b"not_follow")]]

        await event.edit("**Tap on follow button to see advanced options**"
                         " and get notified whenever the price of this product changes", buttons=keyboard)


async def after_following(event, item_name):
    keyboard = [[Button.inline(f"Price Comparison", b"price_comparison")],
                [Button.inline("Unfollow this product", b"unfollow_product")],
                [Button.inline("Download Structured dataset", b"dataset_download")]]

    await event.edit(f"**Product: **{item_name}", buttons=keyboard, link_preview=False)


async def unfollow_product(event, item_name):
    keyboard = [Button.inline(f"Do Nothing", b"do_not_delete_this_product"),
                Button.inline("Yes, 100% confirmed", b"delete_this_product")]

    await event.edit(f"Are you sure you really want to __delete/unfollow__ {item_name}, "
                     f"by doing this, you will not be notified of this specific product."
                     , buttons=keyboard, link_preview=False)


async def price_compare(event, temp_product, item_name):
    keyboard = [Button.inline(f"Back to main menu", b"main_menu_back")]
    last_checked = AllProductsDB().find_product(_id=temp_product['product_code'])
    structured_data = StructuredProductData().find_product(_id=temp_product['product_code'])
    to_show = sorted(structured_data['data'], key=lambda i: i['discounted_price'])
    contributor = ""

    # Checking contributors in All Products DB
    if len(last_checked['contributors']) == 1:
        contributor = "only by you"

    elif len(last_checked['contributors']) == 2:
        contributor = f"You and {len(last_checked['contributors']) - 1} more"

    elif len(last_checked['contributors']) >= 3:
        contributor = f"You and {len(last_checked['contributors']) - 1} others"

    highest = to_show[-1]['discounted_price']
    lowest = to_show[0]['discounted_price']
    average = format(((highest + lowest) / 2), '.1f')

    msg = f"**Product: **{item_name}\n\n__---Highest Price Seen---__\n" \
          f"Price:  ₹{highest}\n" \
          f"Date:   {to_show[-1]['fetched_date']}\n" \
          f"Time:   {to_show[-1]['fetched_time']}\n\n" \
          f"" \
          f"__---Average Price---__\n" \
          f"Price:  ₹{average}\n\n" \
          f"" \
          f"__---Lowest Price Seen---__\n" \
          f"Price:  ₹{lowest}\n" \
          f"Date:   {to_show[0]['fetched_date']}\n" \
          f"Time:   {to_show[0]['fetched_time']}\n\n" \
          f"" \
          f"__---Fetching since---__\n" \
          f"Date:   {structured_data['since_date']}\n" \
          f"Time:   {structured_data['since_time']}\n" \
          f"contributors: {contributor}\n\n" \
          f"" \
          f"__---Last Checked---__\n" \
          f"`{last_checked['fetched_date']}, {last_checked['fetched_time']}`"

    await event.edit(msg, buttons=keyboard, link_preview=False)


@bot.on(events.CallbackQuery())
async def product_update(event):
    dev = "[developer](tg://user?id=1114526265)"
    temp_product = TemporaryProducts().find_product(_id=event.chat.id)
    item_name = f"[{temp_product['product_brand']}]({temp_product['URL']})"
    item_price = temp_product['discounted_price']

    if event.data == b"valid_product":
        AllProductsDB().add_new_product(event)
        await verify_if_following(event, temp_product, item_name, item_price)

    elif event.data == b"not_valid_product":
        await event.edit(
            f"__Probably link to the expected product is invalid__ or if you believe provided information"
            f" is correct you can contact to {dev}")

    elif event.data == b"follow_product":
        AllUsersDB().add_product(event, temp_product['product_code'],
                                 temp_product['product_brand'],
                                 temp_product['URL'])

        await verify_if_following(event, temp_product, item_name, item_price)

    elif event.data == b"not_follow":
        await event.edit(f"😎 Cool! feel free to send me any product link and I will try my best to cut your expenses")

    elif event.data == b"enter_main_menu":
        await after_following(event, item_name)

    elif event.data == b"unfollow_product":
        await unfollow_product(event, item_name)

    elif event.data == b"do_not_delete_this_product":
        await after_following(event, item_name)

    elif event.data == b"delete_this_product":
        AllUsersDB().delete_product(chat_id=event.chat.id, product_id=temp_product['product_code'])
        await event.edit(f"Dropped {item_name} 💩", link_preview=False)

    elif event.data == b"price_comparison":
        await price_compare(event, temp_product, item_name)

    elif event.data == b"main_menu_back":
        await after_following(event, item_name)

    elif event.data == b"dataset_download":
        await StructuredProductData().return_json(bot, event, product_id=temp_product['product_code'],
                                                  item_name=item_name)


bot.start()
bot.run_until_disconnected()
