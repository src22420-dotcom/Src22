# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio 
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, BotCommand
from config import API_ID, API_HASH, ERROR_MESSAGE, LOGIN_SYSTEM, STRING_SESSION, CHANNEL_ID, WAITING_TIME
from database.db import db
from TechVJ.strings import HELP_TXT
from bot import TechVJUser

# ==========================================
# 👑 ADMIN SYSTEM (Yahan Apni ID Daalein)
# ==========================================
ADMIN_IDS = [5450796741, 9876543210] # <--- YAHAN APNI NUMBER WALI ID DAALEIN

# ==========================================
# TEMPORARY MEMORY DATA
# ==========================================
class batch_temp(object):
    IS_BATCH = {}
    USER_DESTINATIONS = {}
    USER_DOWNLOAD_COUNT = {} 
    FORCE_SUB_CHANNELS = [] # F-Sub channels list

class ServerStats:
    downloaded_bytes = 0
    uploaded_bytes = 0

# --- Progress Functions ---
async def downstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile): break
        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread: txt = downread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Downloaded:** **{txt}**")
            await asyncio.sleep(10)
        except: await asyncio.sleep(5)

async def upstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile): break
        await asyncio.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread: txt = upread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Uploaded:** **{txt}**")
            await asyncio.sleep(10)
        except: await asyncio.sleep(5)

def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

def get_size(bytes_size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0: return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0

def get_file_size(msg: Message):
    if getattr(msg, "document", None): return msg.document.file_size
    if getattr(msg, "video", None): return msg.video.file_size
    if getattr(msg, "audio", None): return msg.audio.file_size
    if getattr(msg, "animation", None): return msg.animation.file_size
    if getattr(msg, "voice", None): return msg.voice.file_size
    if getattr(msg, "photo", None): return msg.photo.file_size
    return 0

# ==========================================
# 🛑 FORCE SUB SYSTEM CHECKER
# ==========================================
async def check_fsub(client, user_id):
    if user_id in ADMIN_IDS: return True
    if not batch_temp.FORCE_SUB_CHANNELS: return True
    
    not_joined = []
    for chat_id in batch_temp.FORCE_SUB_CHANNELS:
        try:
            member = await client.get_chat_member(chat_id, user_id)
            if member.status in [enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.LEFT]:
                not_joined.append(chat_id)
        except UserNotParticipant:
            not_joined.append(chat_id)
        except Exception:
            pass 
    
    if not_joined:
        buttons = []
        for chat_id in not_joined:
            try:
                chat = await client.get_chat(chat_id)
                link = chat.invite_link
                if not link: link = await client.export_chat_invite_link(chat_id)
                buttons.append([InlineKeyboardButton(f"🔗 Join {chat.title}", url=link)])
            except: pass
        if buttons: return buttons
    return True

# ==========================================
# PRO UI & TEXT VARIABLES
# ==========================================
DEMO_OVER_TEXT = """<b>🚫 Arey Bhai Bhai Bhai! Ruko Zara, Sabar Karo! 😂</b>\n\nAapka <b>Free Demo Quota</b> yahi samapt hota hai! \n<i>(Limit: Max 5 Files ya 50MB se badi file allowed nahi hai).</i>\n\n😎 <b>Kya aapko ye Bot pasand aaya?</b>\nItna mast aur powerful bot free mein thodi milega! Agar aap chahte ho ki aapka khud ka aisa hi <b>PRO Bot</b> ho, jisme koi limit na ho, 4GB tak upload ho, unlimited channels auto-forward ho, aur doston ke samne aapka bhaukal tight rahe! 🚀\n\n💎 <b>Apna Personal Bot Banwayein / Source Code Kharidein!</b>\nNeeche diye gaye button par click karein aur seedha Admin se baat karein. Ekdum saste rate mein poora PRO Source Code aur setup support milega! 👇"""

BUY_PRO_BUTTON = InlineKeyboardMarkup([[InlineKeyboardButton("👑 Buy PRO Code / Contact Admin", url="https://t.me/kingvj01")]])

HELP_TEXT = """╭━━━ 🛠 𝗛𝗢𝗪 𝗧𝗢 𝗨𝗦𝗘 𝗕𝗢𝗧 🛠 ━━━╮\n\n💡 𝗦𝗧𝗘𝗣-𝗕𝗬-𝗦𝗧𝗘𝗣 𝗚𝗨𝗜𝗗𝗘:\n\n𝟭. 🔐 𝗟𝗼𝗴𝗶𝗻 (𝗠𝗮𝗻𝗱𝗮𝘁𝗼𝗿𝘆)\n➜ Send `/login` to connect your account. \n\n𝟮. 📡 𝗦𝗲𝘁𝘂𝗽 𝗔𝘂𝘁𝗼-𝗨𝗽𝗹𝗼𝗮𝗱 𝗖𝗵𝗮𝗻𝗻𝗲𝗹𝘀\n➜ Forward ANY message from your target channel to this bot.\n\n𝟯. 📥 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱 𝗖𝗼𝗻𝘁𝗲𝗻𝘁\n➜ Send the post link from the restricted channel.\n\n𝟰. ✏️ 𝗖𝗮𝗽𝘁𝗶𝗼𝗻 𝗘𝗱𝗶𝘁𝗼𝗿 (𝗔𝘂𝘁𝗼)\n➜ Bot automatically removes unwanted links and replaces old names.\n\n𝟱. 🗑 𝗠𝗮𝗻𝗮𝗴𝗲𝗺𝗲𝗻𝘁\n➜ `/clear` - Reset destination channels list.\n➜ `/cancel` - Stop a running batch process.\n\n╰━━━ ⚙️ 𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬 𝗣𝗥𝗢 Jaat ⚙️ ━━━╯"""

def get_welcome_text(first_name):
    return f"""╭━━━ ⚡ 𝗥𝗘𝗦 𝗖𝗢𝗡𝗧𝗘𝗡𝗧 𝗦𝗔𝗩𝗘𝗥 ⚡ ━━━╮\n\n👋 𝗪𝗘𝗟𝗖𝗢𝗠𝗘, {first_name}!\n\n🎯 𝗦𝗜𝗠𝗣𝗟𝗘 𝗪𝗢𝗥𝗞𝗙𝗟𝗢𝗪\n➜ 𝗦𝘁𝗲𝗽 𝟭: Click Login to connect.\n➜ 𝗦𝘁𝗲𝗽 𝟮: Forward your channel msg to set destination.\n➜ 𝗦𝘁𝗲𝗽 𝟯: Send restricted links to save!\n\n━━━━━━━━━━━━━━━━━━━━\n\n👇 𝗚𝗘𝗧 𝗦𝗧𝗔𝗥𝗧𝗘𝗗 𝗡𝗢𝗪 👇\n\n╰━━━ ⚙️ 𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬 𝗣𝗥𝗢 Jaat ⚙️ ━━━╯"""

def get_home_buttons():
    return [
        [InlineKeyboardButton("🔑 𝗟𝗼𝗴𝗶𝗻", callback_data="start_login"), InlineKeyboardButton("📊 𝗦𝘁𝗮𝘁𝘀 (Admin)", callback_data="show_stats")],
        [InlineKeyboardButton("❣️ Dᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/kingvj01"), InlineKeyboardButton("🤖 Uᴘᴅᴀᴛᴇs", url="https://t.me/vj_bots")],
        [InlineKeyboardButton("❓ ʜᴏᴡ ᴛᴏ ᴜsᴇ (ʜᴇʟᴘ)", callback_data="show_help")]
    ]

# ==========================================
# ADMIN FORCE SUB COMMANDS
# ==========================================
@Client.on_message(filters.command(["addfsub"]) & filters.private)
async def add_fsub(client, message):
    if message.from_user.id not in ADMIN_IDS: return
    if message.reply_to_message and message.reply_to_message.forward_from_chat:
        chat_id = message.reply_to_message.forward_from_chat.id
        if chat_id not in batch_temp.FORCE_SUB_CHANNELS:
            batch_temp.FORCE_SUB_CHANNELS.append(chat_id)
            await message.reply(f"✅ **Done Admin!**\nChannel `{chat_id}` ko Force Sub list mein add kar diya gaya hai. Ab sabhi ko pehle isey join karna padega!")
        else:
            await message.reply("⚠️ Ye channel pehle se F-Sub list mein hai.")
    else:
        await message.reply("❌ **Tariqa Galat Hai Admin!**\nPehle channel se koi message bot ko Forward karein, fir us forwarded message ka Reply dekar `/addfsub` likhein.")

@Client.on_message(filters.command(["fsublist"]) & filters.private)
async def fsub_list(client, message):
    if message.from_user.id not in ADMIN_IDS: return
    if not batch_temp.FORCE_SUB_CHANNELS:
        return await message.reply("📋 **Force Sub Channels:**\nAbhi koi channel add nahi hai.")
    text = "📋 **Active Force Sub Channels:**\n\n"
    for i, chat_id in enumerate(batch_temp.FORCE_SUB_CHANNELS):
        try:
            chat = await client.get_chat(chat_id)
            text += f"{i+1}. {chat.title} (`{chat_id}`)\n"
        except:
            text += f"{i+1}. `{chat_id}` (Error: Bot is not Admin here)\n"
    text += "\n🗑 Remove karne ke liye `/delfsub <ID>` use karein."
    await message.reply(text)

@Client.on_message(filters.command(["delfsub"]) & filters.private)
async def del_fsub(client, message):
    if message.from_user.id not in ADMIN_IDS: return
    try:
        chat_id = int(message.text.split()[1])
        if chat_id in batch_temp.FORCE_SUB_CHANNELS:
            batch_temp.FORCE_SUB_CHANNELS.remove(chat_id)
            await message.reply(f"✅ Removed `{chat_id}` from Force Sub.")
        else:
            await message.reply("⚠️ Ye ID list mein nahi mili.")
    except:
        await message.reply("❌ Sahi Format: `/delfsub -100123456789`")

# ==========================================
# GENERAL COMMANDS
# ==========================================
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    # F-Sub Check before Start
    fsub_check = await check_fsub(client, message.from_user.id)
    if fsub_check is not True and len(fsub_check) > 0:
        return await message.reply("❌ **Ruko Bhai! Bot use karne ke liye pehle in channels ko Join karo:**\nJoin karne ke baad wapas `/start` bhejna.", reply_markup=InlineKeyboardMarkup(fsub_check))

    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    
    # 🔥 DYNAMIC BOT MENU GENERATOR
    try:
        cmds = [
            BotCommand("start", "🚀 Start Bot"), 
            BotCommand("login", "🔑 Login Account"), 
            BotCommand("logout", "🚪 Logout Account"),
            BotCommand("help", "❓ Help Menu"), 
            BotCommand("clear", "🗑 Clear Channels"),
            BotCommand("cancel", "🛑 Cancel Task")
        ]
        if message.from_user.id in ADMIN_IDS:
            cmds.extend([
                BotCommand("stats", "📊 Server Stats"), 
                BotCommand("addfsub", "➕ Add Force Sub"),
                BotCommand("fsublist", "📋 FSub List"),
                BotCommand("delfsub", "🗑 Delete FSub")
            ])
        await client.set_bot_commands(cmds)
    except: pass 

    await client.send_photo(
        chat_id=message.chat.id, 
        photo="Image.jpg", 
        caption=get_welcome_text(message.from_user.first_name or "User"), 
        reply_markup=InlineKeyboardMarkup(get_home_buttons()), 
        reply_to_message_id=message.id
    )

@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(message.chat.id, text=HELP_TEXT, reply_to_message_id=message.id)

@Client.on_message(filters.command(["stats"]))
async def send_stats(client: Client, message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.reply("❌ **Aukaat mein reh! Ye command sirf PRO Admin ke liye hai.**")
    
    try: total_users = await db.total_users_count()
    except: total_users = "Unknown"
    dl = get_size(ServerStats.downloaded_bytes)
    ul = get_size(ServerStats.uploaded_bytes)
    total_data = get_size(ServerStats.downloaded_bytes + ServerStats.uploaded_bytes)

    stats_msg = f"""╭━━━ 📊 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦 📊 ━━━╮\n\n👥 𝗧𝗼𝘁𝗮𝗹 𝗨𝘀𝗲𝗿𝘀 (𝗠𝗼𝗻𝗴𝗼𝗗𝗕): {total_users}\n🔑 𝗔𝗰𝘁𝗶𝘃𝗲 𝗟𝗼𝗴𝗶𝗻𝘀: Secured in DB\n\n⬇️ 𝗦𝗲𝗿𝘃𝗲𝗿 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱𝗲𝗱: {dl}\n⬆️ 𝗦𝗲𝗿𝘃𝗲𝗿 𝗨𝗽𝗹𝗼𝗮𝗱𝗲𝗱: {ul}\n🔄 𝗧𝗼𝘁𝗮𝗹 𝗗𝗮𝘁𝗮 𝗨𝘀𝗲𝗱: {total_data}\n\n╰━━━ ⚙️ 𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬 𝗣𝗥𝗢 Jaat ⚙️ ━━━╯"""
    await client.send_message(message.chat.id, stats_msg)

# ==========================================
# CALLBACK HANDLERS (BUTTON CLICKS)
# ==========================================
@Client.on_callback_query(filters.regex("show_help"))
async def help_callback(client: Client, query):
    await query.message.edit_caption(caption=HELP_TEXT, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="back_start")]]))

# 🔥 DIRECT LOGIN TRIGGER BY BUTTON
@Client.on_callback_query(filters.regex("start_login"))
async def login_callback(client: Client, query):
    await query.answer("Starting Login Process...", show_alert=False)
    # generate.py ke function ko bula kar direct trigger karna
    from TechVJ.generate import main as login_process
    
    # Message object copy banakar usme text daalna
    mock_message = query.message
    mock_message.from_user = query.from_user
    mock_message.text = "/login"
    
    # Puraana welcome message delete karna aur login chalana
    await query.message.delete()
    await login_process(client, mock_message)

@Client.on_callback_query(filters.regex("show_stats"))
async def stats_callback(client: Client, query):
    if query.from_user.id not in ADMIN_IDS:
        return await query.answer("❌ Only PRO Admin can view Stats!", show_alert=True)
    try: total_users = await db.total_users_count()
    except: total_users = "Unknown"
    dl = get_size(ServerStats.downloaded_bytes)
    ul = get_size(ServerStats.uploaded_bytes)
    stats_msg = f"""╭━━━ 📊 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦 📊 ━━━╮\n\n👥 𝗧𝗼𝘁𝗮𝗹 𝗨𝘀𝗲𝗿𝘀 (𝗠𝗼𝗻𝗴𝗼𝗗𝗕): {total_users}\n🔑 𝗔𝗰𝘁𝗶𝘃𝗲 𝗟𝗼𝗴𝗶𝗻𝘀: Secured in DB\n\n⬇️ 𝗦𝗲𝗿𝘃𝗲𝗿 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱𝗲𝗱: {dl}\n⬆️ 𝗦𝗲𝗿𝘃𝗲𝗿 𝗨𝗽𝗹𝗼𝗮𝗱𝗲𝗱: {ul}\n🔄 𝗧𝗼𝘁𝗮𝗹 𝗗𝗮𝘁𝗮 𝗨𝘀𝗲𝗱: {get_size(ServerStats.downloaded_bytes + ServerStats.uploaded_bytes)}\n\n╰━━━ ⚙️ 𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬 𝗣𝗥𝗢 Jaat ⚙️ ━━━╯"""
    await query.message.edit_caption(caption=stats_msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="back_start")]]))

@Client.on_callback_query(filters.regex("back_start"))
async def back_callback(client: Client, query):
    await query.message.edit_caption(caption=get_welcome_text(query.from_user.first_name or "User"), reply_markup=InlineKeyboardMarkup(get_home_buttons()))

@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(chat_id=message.chat.id, text="**Batch Successfully Cancelled.**")

# --- User Destination Channels Setup ---
@Client.on_message(filters.forwarded & filters.private)
async def add_target_channel(client: Client, message: Message):
    if message.forward_from_chat and message.forward_from_chat.type == enums.ChatType.CHANNEL:
        # Puraani /addfsub request check kar raha hai, skip normal process
        if message.reply_to_message: return
        
        chat_id = message.forward_from_chat.id
        user_id = message.from_user.id
        if user_id not in batch_temp.USER_DESTINATIONS: batch_temp.USER_DESTINATIONS[user_id] = []
        if chat_id not in batch_temp.USER_DESTINATIONS[user_id]:
            batch_temp.USER_DESTINATIONS[user_id].append(chat_id)
            await message.reply_text(f"✅ **Auto-Upload चैनल सेट हो गया!**\n\n📌 नाम: {message.forward_from_chat.title}\n*(नोट: बॉट को इन चैनल्स में Admin होना ज़रूरी है!)*\n\n🗑️ लिस्ट क्लियर करने के लिए /clear भेजें.")
        else:
            await message.reply_text("⚠️ यह चैनल पहले से ही डेस्टिनेशन लिस्ट में है।")
    else:
        pass

@Client.on_message(filters.command(["clear"]) & filters.private)
async def clear_channels(client: Client, message: Message):
    batch_temp.USER_DESTINATIONS[message.from_user.id] = []
    await message.reply_text("🗑️ **Auto-Upload चैनल्स लिस्ट से हटा दिए गए हैं!**")

# ==========================================
# MAIN CORE (DOWNLOAD & UPLOAD)
# ==========================================
@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    if message.text.startswith("/"): return

    # 🔥 Link bhejte time bhi Force Sub Check
    if "https://t.me/" in message.text:
        fsub_check = await check_fsub(client, message.from_user.id)
        if fsub_check is not True and len(fsub_check) > 0:
            return await message.reply("❌ **Pehle in channels ko join karo, fir link bhejna!**", reply_markup=InlineKeyboardMarkup(fsub_check))

    if ("https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text) and LOGIN_SYSTEM == False:
        if TechVJUser is None: return await client.send_message(message.chat.id, "String Session is not Set")
        try:
            try: await TechVJUser.join_chat(message.text)
            except Exception as e: return await client.send_message(message.chat.id, f"Error : {e}")
            await client.send_message(message.chat.id, "Chat Joined")
        except UserAlreadyParticipant: await client.send_message(message.chat.id, "Chat already Joined")
        except InviteHashExpired: await client.send_message(message.chat.id, "Invalid Link")
        return
    
    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text("**One Task Is Already Processing... Use /cancel**")
        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        try: toID = int(temp[1].strip())
        except: toID = fromID

        if LOGIN_SYSTEM == True:
            user_data = await db.get_session(message.from_user.id)
            if user_data is None: return await message.reply("**For Downloading Restricted Content You Have To /login First.**")
            api_id = int(await db.get_api_id(message.from_user.id))
            api_hash = await db.get_api_hash(message.from_user.id)
            try:
                acc = Client("saverestricted", session_string=user_data, api_hash=api_hash, api_id=api_id)
                await acc.connect()
            except: return await message.reply("**Your Login Session Expired. /login Again**")
        else:
            if TechVJUser is None: return await client.send_message(message.chat.id, f"**String Session is not Set**")
            acc = TechVJUser
				
        batch_temp.IS_BATCH[message.from_user.id] = False
        for msgid in range(fromID, toID+1):
            if batch_temp.IS_BATCH.get(message.from_user.id): break
            
            if "https://t.me/c/" in message.text:
                try: await handle_private(client, acc, message, int("-100" + datas[4]), msgid)
                except Exception as e:
                    if ERROR_MESSAGE: await client.send_message(message.chat.id, f"Error: {e}")
            elif "https://t.me/b/" in message.text:
                try: await handle_private(client, acc, message, datas[4], msgid)
                except Exception as e:
                    if ERROR_MESSAGE: await client.send_message(message.chat.id, f"Error: {e}")
            else:
                username = datas[3]
                try: msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied: 
                    await client.send_message(message.chat.id, "Username not occupied")
                    return
                try: await client.copy_message(message.chat.id, msg.chat.id, msg.id)
                except:
                    try: await handle_private(client, acc, message, username, msgid)               
                    except Exception as e:
                        if ERROR_MESSAGE: await client.send_message(message.chat.id, f"Error: {e}")

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
    is_admin = user_id in ADMIN_IDS

    # 🚫 LIMITS FOR DEMO USERS
    if not is_admin:
        if batch_temp.USER_DOWNLOAD_COUNT.get(user_id, 0) >= 5:
            return await client.send_message(message.chat.id, DEMO_OVER_TEXT, reply_markup=BUY_PRO_BUTTON, parse_mode=enums.ParseMode.HTML)
        file_size = get_file_size(msg)
        if file_size and file_size > (50 * 1024 * 1024):
            return await client.send_message(message.chat.id, DEMO_OVER_TEXT, reply_markup=BUY_PRO_BUTTON, parse_mode=enums.ParseMode.HTML)

    dest_chats = batch_temp.USER_DESTINATIONS.get(user_id, [])
    if not dest_chats: dest_chats = [int(CHANNEL_ID)] if CHANNEL_ID else [message.chat.id]
    primary_chat = dest_chats[0]
    if batch_temp.IS_BATCH.get(message.from_user.id): return 

    # --- Caption Edit ---
    if msg.caption or (msg_type == "Text" and msg.text):
        text_data = msg.caption if msg.caption else msg.text
        REPLACE_WORDS = {"@Tech_VJ": "@YourChannel", "Tech VJ": "PRO Jaat", "t.me/": " "}
        for old, new in REPLACE_WORDS.items(): text_data = text_data.replace(old, new)
        text_data += "\n\n**📥 जॉइन करें @YourChannel**"
        
        if msg.caption: caption = text_data
        else: msg.text = text_data
    else: caption = None

    if "Text" == msg_type:
        try:
            sent_msg = await client.send_message(primary_chat, msg.text, entities=msg.entities)
            for chat in dest_chats[1:]: await sent_msg.copy(chat)
            return 
        except: return 

    smsg = await client.send_message(message.chat.id, '**Downloading...**')
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, message.chat.id))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        if file and os.path.exists(file): ServerStats.downloaded_bytes += os.path.getsize(file)
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        return await smsg.delete()
        
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, message.chat.id))
    
    sent_msg = None

    if "Document" == msg_type:
        try: ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
        except: ph_path = None
        try: sent_msg = await client.send_document(primary_chat, file, thumb=ph_path, caption=caption, progress=progress, progress_args=[message,"up"])
        except: pass
        if ph_path: os.remove(ph_path)
    elif "Video" == msg_type:
        try: ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
        except: ph_path = None
        try: sent_msg = await client.send_video(primary_chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, progress=progress, progress_args=[message,"up"])
        except: pass
        if ph_path: os.remove(ph_path)
    elif "Animation" == msg_type:
        try: sent_msg = await client.send_animation(primary_chat, file, caption=caption)
        except: pass
    elif "Sticker" == msg_type:
        try: sent_msg = await client.send_sticker(primary_chat, file)
        except: pass
    elif "Voice" == msg_type:
        try: sent_msg = await client.send_voice(primary_chat, file, caption=caption)
        except: pass
    elif "Audio" == msg_type:
        try: ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
        except: ph_path = None
        try: sent_msg = await client.send_audio(primary_chat, file, thumb=ph_path, caption=caption, progress=progress, progress_args=[message,"up"])   
        except: pass
        if ph_path: os.remove(ph_path)
    elif "Photo" == msg_type:
        try: sent_msg = await client.send_photo(primary_chat, file, caption=caption)
        except: pass
    
    if sent_msg and os.path.exists(file): ServerStats.uploaded_bytes += os.path.getsize(file)

    if sent_msg and len(dest_chats) > 1:
        for chat in dest_chats[1:]:
            try: await sent_msg.copy(chat); await asyncio.sleep(0.5)
            except: pass

    if not is_admin and sent_msg:
        batch_temp.USER_DOWNLOAD_COUNT[user_id] = batch_temp.USER_DOWNLOAD_COUNT.get(user_id, 0) + 1

    if os.path.exists(f'{message.id}upstatus.txt'): 
        os.remove(f'{message.id}upstatus.txt')
        os.remove(file)
    await client.delete_messages(message.chat.id,[smsg.id])

def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    for t in ["document", "video", "animation", "sticker", "voice", "audio", "photo", "text"]:
        if getattr(msg, t, None): return t.capitalize()
