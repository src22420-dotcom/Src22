# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio 
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, BotCommand
from config import API_ID, API_HASH, ERROR_MESSAGE, LOGIN_SYSTEM, STRING_SESSION, CHANNEL_ID, WAITING_TIME
from database.db import db
from TechVJ.strings import HELP_TXT
from bot import TechVJUser

# ==========================================
# 👑 ADMIN SYSTEM (Yahan Apni Telegram ID Daalein)
# ==========================================
# In IDs ke liye koi limit nahi hogi (Unlimited Usage)
ADMIN_IDS = [5450796741, 9876543210] # <--- YAHAN APNI NUMBER WALI ID DAALEIN

# ==========================================
# डेटा और मेमोरी ट्रैकिंग के लिए
# ==========================================
class batch_temp(object):
    IS_BATCH = {}
    USER_DESTINATIONS = {}
    USER_DOWNLOAD_COUNT = {} # NEW: Free users ke downloads track karne ke liye

class ServerStats:
    downloaded_bytes = 0
    uploaded_bytes = 0

async def downstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)
      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Downloaded:** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

# upload status
async def upstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Uploaded:** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

# progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

# साइज़ कन्वर्टर (MB/GB के लिए)
def get_size(bytes_size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0

# फाइल साइज़ निकालने के लिए Helper Function
def get_file_size(msg: Message):
    if msg.document: return msg.document.file_size
    if msg.video: return msg.video.file_size
    if msg.audio: return msg.audio.file_size
    if msg.animation: return msg.animation.file_size
    if msg.voice: return msg.voice.file_size
    if msg.photo: return msg.photo.file_size
    return 0

# ==========================================
# PRO UI & TEXT VARIABLES
# ==========================================

DEMO_OVER_TEXT = """<b>🚫 Arey Bhai Bhai Bhai! Ruko Zara, Sabar Karo! 😂</b>

Aapka <b>Free Demo Quota</b> yahi samapt hota hai! 
<i>(Limit: Max 5 Files ya 50MB se badi file allowed nahi hai).</i>

😎 <b>Kya aapko ye Bot pasand aaya?</b>
Itna mast aur powerful bot free mein thodi milega! Agar aap chahte ho ki aapka khud ka aisa hi <b>PRO Bot</b> ho, jisme koi limit na ho, 4GB tak upload ho, unlimited channels auto-forward ho, aur doston ke samne aapka bhaukal tight rahe! 🚀

💎 <b>Apna Personal Bot Banwayein / Source Code Kharidein!</b>
Neeche diye gaye button par click karein aur seedha Admin se baat karein. Ekdum saste rate mein poora PRO Source Code aur setup support milega! 👇"""

BUY_PRO_BUTTON = InlineKeyboardMarkup([
    [InlineKeyboardButton("👑 Buy PRO Code / Contact Admin", url="https://t.me/rajk98765a")] # <--- YAHAN APNA TG USERNAME DAALEIN
])

HELP_TEXT = """╭━━━ 🛠 𝗛𝗢𝗪 𝗧𝗢 𝗨𝗦𝗘 𝗕𝗢𝗧 🛠 ━━━╮

💡 𝗦𝗧𝗘𝗣-𝗕𝗬-𝗦𝗧𝗘𝗣 𝗚𝗨𝗜𝗗𝗘:

𝟭. 🔐 𝗟𝗼𝗴𝗶𝗻 (𝗠𝗮𝗻𝗱𝗮𝘁𝗼𝗿𝘆)
➜ Send `/login` to connect your account. 

𝟮. 📡 𝗦𝗲𝘁𝘂𝗽 𝗔𝘂𝘁𝗼-𝗨𝗽𝗹𝗼𝗮𝗱 𝗖𝗵𝗮𝗻𝗻𝗲𝗹𝘀
➜ Forward ANY message from your target channel to this bot.
➜ Bot will save it. You can add multiple channels!

𝟯. 📥 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱 𝗖𝗼𝗻𝘁𝗲𝗻𝘁
➜ Send the post link from the restricted channel.

𝟰. ✏️ 𝗖𝗮𝗽𝘁𝗶𝗼𝗻 𝗘𝗱𝗶𝘁𝗼𝗿 (𝗔𝘂𝘁𝗼)
➜ Bot automatically removes unwanted links and replaces old names.

𝟱. 🗑 𝗠𝗮𝗻𝗮𝗴𝗲𝗺𝗲𝗻𝘁
➜ `/clear` - Reset destination channels list.
➜ `/cancel` - Stop a running batch process.
➜ `/stats` - Check Server Data & Users.

╰━━━ ⚙️ 𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬 𝗣𝗥𝗢 Jaat ⚙️ ━━━╯"""

def get_welcome_text(first_name):
    return f"""╭━━━ ⚡ 𝗥𝗘𝗦 𝗖𝗢𝗡𝗧𝗘𝗡𝗧 𝗦𝗔𝗩𝗘𝗥 ⚡ ━━━╮

👋 𝗪𝗘𝗟𝗖𝗢𝗠𝗘, {first_name}!

🤖 𝗬𝗢𝗨𝗥 𝗔𝗟𝗟-𝗜𝗡-𝗢𝗡𝗘 𝗖𝗢𝗡𝗧𝗘𝗡𝗧 𝗧𝗢𝗢𝗟 🚀

┏━━━━━━━━━━━━━━━━━━━━┓
┃ 💎 𝗣𝗥𝗢 𝗕𝗢𝗧 𝗙𝗘𝗔𝗧𝗨𝗥𝗘𝗦
┣━━━━━━━━━━━━━━━━━━━━┫
┃ 🔑 Secure Account Login
┃ 📡 Multiple Channels Add
┃ ✏️ Auto Caption Editor
┃ 📥 Res. Content Save
┃ 🔄 Fast Forward & Bypass
┃ 📊 Server Stats Tracker
┗━━━━━━━━━━━━━━━━━━━━┛

🎯 𝗦𝗜𝗠𝗣𝗟𝗘 𝗪𝗢𝗥𝗞𝗙𝗟𝗢𝗪
➜ 𝗦𝘁𝗲𝗽 𝟭: Send /login to connect.
➜ 𝗦𝘁𝗲𝗽 𝟮: Forward your channel msg to set destination.
➜ 𝗦𝘁𝗲𝗽 𝟯: Send restricted links to save!

━━━━━━━━━━━━━━━━━━━━

👇 𝗚𝗘𝗧 𝗦𝗧𝗔𝗥𝗧𝗘𝗗 𝗡𝗢𝗪 👇

╰━━━ ⚙️ 𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬 𝗣𝗥𝗢 Jaat ⚙️ ━━━╯"""

def get_home_buttons():
    return [
        [
            InlineKeyboardButton("🔑 𝗟𝗼𝗴𝗶𝗻", callback_data="login_instruction"),
            InlineKeyboardButton("📊 𝗦𝘁𝗮𝘁𝘀", callback_data="show_stats")
        ],
        [
            InlineKeyboardButton("❣️ Dᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/rajk98765a"),
            InlineKeyboardButton("🤖 Uᴘᴅᴀᴛᴇs", url="https://t.me/+lVCFkJZxLy00ZmFl")
        ],
        [
            InlineKeyboardButton("❓ ʜᴏᴡ ᴛᴏ ᴜsᴇ (ʜᴇʟᴘ)", callback_data="show_help")
        ]
    ]

# ==========================================
# COMMAND HANDLERS
# ==========================================

@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    
    try:
        await client.set_bot_commands([
            BotCommand("start", "🚀 Start the bot"),
            BotCommand("login", "🔑 Login to your account"),
            BotCommand("stats", "📊 Check Data & Server Stats"),
            BotCommand("help", "❓ How to use the bot"),
            BotCommand("clear", "🗑 Clear added channels"),
            BotCommand("cancel", "🛑 Cancel ongoing task")
        ])
    except:
        pass 

    reply_markup = InlineKeyboardMarkup(get_home_buttons())
    first_name = message.from_user.first_name if message.from_user.first_name else "User"

    await client.send_message(
        chat_id=message.chat.id, 
        text=get_welcome_text(first_name), 
        reply_markup=reply_markup, 
        reply_to_message_id=message.id
    )

@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(message.chat.id, text=HELP_TEXT, reply_to_message_id=message.id)

@Client.on_message(filters.command(["stats"]))
async def send_stats(client: Client, message: Message):
    try:
        total_users = await db.total_users_count()
    except:
        total_users = "Unknown"

    dl = get_size(ServerStats.downloaded_bytes)
    ul = get_size(ServerStats.uploaded_bytes)
    total_data = get_size(ServerStats.downloaded_bytes + ServerStats.uploaded_bytes)

    stats_msg = f"""╭━━━ 📊 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦 📊 ━━━╮\n\n👥 𝗧𝗼𝘁𝗮𝗹 𝗨𝘀𝗲𝗿𝘀 (𝗠𝗼𝗻𝗴𝗼𝗗𝗕): {total_users}\n🔑 𝗔𝗰𝘁𝗶𝘃𝗲 𝗟𝗼𝗴𝗶𝗻𝘀: Secured in DB\n\n⬇️ 𝗦𝗲𝗿𝘃𝗲𝗿 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱𝗲𝗱: {dl}\n⬆️ 𝗦𝗲𝗿𝘃𝗲𝗿 𝗨𝗽𝗹𝗼𝗮𝗱𝗲𝗱: {ul}\n🔄 𝗧𝗼𝘁𝗮𝗹 𝗗𝗮𝘁𝗮 𝗨𝘀𝗲𝗱: {total_data}\n\n╰━━━ ⚙️ 𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬 𝗣𝗥𝗢 Jaat ⚙️ ━━━╯"""
    await client.send_message(message.chat.id, stats_msg)

# ==========================================
# CALLBACK HANDLERS
# ==========================================

@Client.on_callback_query(filters.regex("show_help"))
async def help_callback(client: Client, query):
    await query.message.edit_text(text=HELP_TEXT, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="back_start")]]))

@Client.on_callback_query(filters.regex("login_instruction"))
async def login_callback(client: Client, query):
    await query.answer("Type and send /login in the chat to start the login process!", show_alert=True)

@Client.on_callback_query(filters.regex("show_stats"))
async def stats_callback(client: Client, query):
    try: total_users = await db.total_users_count()
    except: total_users = "Unknown"
    dl = get_size(ServerStats.downloaded_bytes)
    ul = get_size(ServerStats.uploaded_bytes)
    total_data = get_size(ServerStats.downloaded_bytes + ServerStats.uploaded_bytes)
    stats_msg = f"""╭━━━ 📊 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦 📊 ━━━╮\n\n👥 𝗧𝗼𝘁𝗮𝗹 𝗨𝘀𝗲𝗿𝘀 (𝗠𝗼𝗻𝗴𝗼𝗗𝗕): {total_users}\n🔑 𝗔𝗰𝘁𝗶𝘃𝗲 𝗟𝗼𝗴𝗶𝗻𝘀: Secured in DB\n\n⬇️ 𝗦𝗲𝗿𝘃𝗲𝗿 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱𝗲𝗱: {dl}\n⬆️ 𝗦𝗲𝗿𝘃𝗲𝗿 𝗨𝗽𝗹𝗼𝗮𝗱𝗲𝗱: {ul}\n🔄 𝗧𝗼𝘁𝗮𝗹 𝗗𝗮𝘁𝗮 𝗨𝘀𝗲𝗱: {total_data}\n\n╰━━━ ⚙️ 𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬 𝗣𝗥𝗢 Jaat ⚙️ ━━━╯"""
    await query.message.edit_text(text=stats_msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="back_start")]]))

@Client.on_callback_query(filters.regex("back_start"))
async def back_callback(client: Client, query):
    first_name = query.from_user.first_name if query.from_user.first_name else "User"
    await query.message.edit_text(text=get_welcome_text(first_name), reply_markup=InlineKeyboardMarkup(get_home_buttons()))

@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(chat_id=message.chat.id, text="**Batch Successfully Cancelled.**")

@Client.on_message(filters.forwarded & filters.private)
async def add_target_channel(client: Client, message: Message):
    if message.forward_from_chat and message.forward_from_chat.type == enums.ChatType.CHANNEL:
        chat_id = message.forward_from_chat.id
        user_id = message.from_user.id
        if user_id not in batch_temp.USER_DESTINATIONS:
            batch_temp.USER_DESTINATIONS[user_id] = []
        if chat_id not in batch_temp.USER_DESTINATIONS[user_id]:
            batch_temp.USER_DESTINATIONS[user_id].append(chat_id)
            await message.reply_text(f"✅ **चैनल सेट हो गया!**\n\n📌 नाम: {message.forward_from_chat.title}\n📊 टोटल सेट चैनल्स: {len(batch_temp.USER_DESTINATIONS[user_id])}\n\nℹ️ *और चैनल ऐड करने हैं तो उनका भी मैसेज फॉरवर्ड करें।*\n*(नोट: बॉट को इन चैनल्स में Admin होना ज़रूरी है!)*\n\n🗑️ लिस्ट क्लियर करने के लिए /clear भेजें.")
        else:
            await message.reply_text("⚠️ यह चैनल पहले से ही लिस्ट में है।")
    else:
        await message.reply_text("❌ कृपया किसी चैनल (Channel) से मैसेज फॉरवर्ड करें।")

@Client.on_message(filters.command(["clear"]) & filters.private)
async def clear_channels(client: Client, message: Message):
    batch_temp.USER_DESTINATIONS[message.from_user.id] = []
    await message.reply_text("🗑️ **सभी चैनल्स लिस्ट से हटा दिए गए हैं!**\nअब फाइलें सीधे यहीं (Bot के इनबॉक्स में) आएँगी।")

# ==========================================
# MAIN CORE (DOWNLOAD & UPLOAD)
# ==========================================

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    if ("https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text) and LOGIN_SYSTEM == False:
        if TechVJUser is None:
            return await client.send_message(message.chat.id, "String Session is not Set", reply_to_message_id=message.id)
        try:
            try: await TechVJUser.join_chat(message.text)
            except Exception as e: return await client.send_message(message.chat.id, f"Error : {e}", reply_to_message_id=message.id)
            await client.send_message(message.chat.id, "Chat Joined", reply_to_message_id=message.id)
        except UserAlreadyParticipant:
            await client.send_message(message.chat.id, "Chat already Joined", reply_to_message_id=message.id)
        except InviteHashExpired:
            await client.send_message(message.chat.id, "Invalid Link", reply_to_message_id=message.id)
        return
    
    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text("**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**")
        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        try: toID = int(temp[1].strip())
        except: toID = fromID

        if LOGIN_SYSTEM == True:
            user_data = await db.get_session(message.from_user.id)
            if user_data is None:
                return await message.reply("**For Downloading Restricted Content You Have To /login First.**")
            api_id = int(await db.get_api_id(message.from_user.id))
            api_hash = await db.get_api_hash(message.from_user.id)
            try:
                acc = Client("saverestricted", session_string=user_data, api_hash=api_hash, api_id=api_id)
                await acc.connect()
            except:
                return await message.reply("**Your Login Session Expired. So /logout First Then Login Again By - /login**")
        else:
            if TechVJUser is None:
                return await client.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
            acc = TechVJUser
				
        batch_temp.IS_BATCH[message.from_user.id] = False
        for msgid in range(fromID, toID+1):
            if batch_temp.IS_BATCH.get(message.from_user.id): break
            
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])
                try: await handle_private(client, acc, message, chatid, msgid)
                except Exception as e:
                    if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                try: await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                    if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            else:
                username = datas[3]
                try: msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied: 
                    await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)
                    return
                try: await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                except:
                    try: await handle_private(client, acc, message, username, msgid)               
                    except Exception as e:
                        if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            await asyncio.sleep(WAITING_TIME)
        if LOGIN_SYSTEM == True:
            try: await acc.disconnect()
            except: pass                				
        batch_temp.IS_BATCH[message.from_user.id] = True


async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty: return 
    msg_type = get_message_type(msg)
    if not msg_type: return 
    
    user_id = message.from_user.id
    is_admin = user_id in ADMIN_IDS # ADMIN CHECKER

    # ==========================================
    # 🚫 LIMITS SYSTEM FOR DEMO USERS
    # ==========================================
    if not is_admin:
        # 1. Track File Download Count Limit (Max 5)
        current_count = batch_temp.USER_DOWNLOAD_COUNT.get(user_id, 0)
        if current_count >= 5:
            await client.send_message(message.chat.id, DEMO_OVER_TEXT, reply_markup=BUY_PRO_BUTTON, parse_mode=enums.ParseMode.HTML)
            return

        # 2. Track File Size Limit (Max 50MB)
        file_size = get_file_size(msg)
        if file_size and file_size > (50 * 1024 * 1024):
            await client.send_message(message.chat.id, DEMO_OVER_TEXT, reply_markup=BUY_PRO_BUTTON, parse_mode=enums.ParseMode.HTML)
            return
    # ==========================================

    dest_chats = batch_temp.USER_DESTINATIONS.get(user_id, [])
    
    if not dest_chats:
        if CHANNEL_ID:
            try: dest_chats = [int(CHANNEL_ID)]
            except: dest_chats = [message.chat.id]
        else:
            dest_chats = [message.chat.id]
            
    primary_chat = dest_chats[0]
    if batch_temp.IS_BATCH.get(message.from_user.id): return 

    # --- कैप्शन एडिट ---
    if msg.caption or (msg_type == "Text" and msg.text):
        text_data = msg.caption if msg.caption else msg.text
        
        REPLACE_WORDS = {
            "@Tech_VJ": "@YourChannel",
            "Tech VJ": "PRO Jaat",
            "t.me/": " "
        }
        for old_word, new_word in REPLACE_WORDS.items():
            text_data = text_data.replace(old_word, new_word)
            
        CUSTOM_FOOTER = "\n\n**📥 जॉइन करें @YourChannel**"
        text_data = text_data + CUSTOM_FOOTER
        
        if msg.caption: caption = text_data
        else: msg.text = text_data
    else:
        caption = None

    if "Text" == msg_type:
        try:
            sent_msg = await client.send_message(primary_chat, msg.text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            if len(dest_chats) > 1:
                for chat in dest_chats[1:]: await sent_msg.copy(chat)
            return 
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 

    smsg = await client.send_message(message.chat.id, '**Downloading...**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, message.chat.id))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        if file and os.path.exists(file): ServerStats.downloaded_bytes += os.path.getsize(file)
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) 
        return await smsg.delete()
        
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, message.chat.id))
    
    sent_msg = None

    if "Document" == msg_type:
        try: ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
        except: ph_path = None
        try: sent_msg = await client.send_document(primary_chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e: pass
        if ph_path != None: os.remove(ph_path)
        
    elif "Video" == msg_type:
        try: ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
        except: ph_path = None
        try: sent_msg = await client.send_video(primary_chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e: pass
        if ph_path != None: os.remove(ph_path)

    elif "Animation" == msg_type:
        try: sent_msg = await client.send_animation(primary_chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except: pass
        
    elif "Sticker" == msg_type:
        try: sent_msg = await client.send_sticker(primary_chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except: pass

    elif "Voice" == msg_type:
        try: sent_msg = await client.send_voice(primary_chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except: pass

    elif "Audio" == msg_type:
        try: ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
        except: ph_path = None
        try: sent_msg = await client.send_audio(primary_chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])   
        except: pass
        if ph_path != None: os.remove(ph_path)

    elif "Photo" == msg_type:
        try: sent_msg = await client.send_photo(primary_chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except: pass
    
    if sent_msg and os.path.exists(file):
        ServerStats.uploaded_bytes += os.path.getsize(file)

    if sent_msg and len(dest_chats) > 1:
        for chat in dest_chats[1:]:
            try:
                await sent_msg.copy(chat)
                await asyncio.sleep(0.5)
            except:
                pass

    # ✅ SUCCESSFUL DOWNLOAD HONE PAR FREE USER KA COUNT BADA DO
    if not is_admin and sent_msg:
        batch_temp.USER_DOWNLOAD_COUNT[user_id] = batch_temp.USER_DOWNLOAD_COUNT.get(user_id, 0) + 1

    if os.path.exists(f'{message.id}upstatus.txt'): 
        os.remove(f'{message.id}upstatus.txt')
        os.remove(file)
    await client.delete_messages(message.chat.id,[smsg.id])

def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    if getattr(msg, "document", None): return "Document"
    if getattr(msg, "video", None): return "Video"
    if getattr(msg, "animation", None): return "Animation"
    if getattr(msg, "sticker", None): return "Sticker"
    if getattr(msg, "voice", None): return "Voice"
    if getattr(msg, "audio", None): return "Audio"
    if getattr(msg, "photo", None): return "Photo"
    if getattr(msg, "text", None): return "Text"
