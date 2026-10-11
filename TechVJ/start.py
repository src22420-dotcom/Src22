# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio 
import time
import re
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
# TEMPORARY MEMORY & STATES
# ==========================================
class batch_temp(object):
    IS_BATCH = {}
    USER_DESTINATIONS = {}
    USER_DOWNLOAD_COUNT = {} 
    FORCE_SUB_CHANNELS = [] 
    USER_STATE = {} 
    BATCH_DATA = {} 

class ServerStats:
    downloaded_bytes = 0
    uploaded_bytes = 0

async def progress(current, total, client, message, start_time, base_text):
    now = time.time()
    if (now - start_time[0]) > 2.5: 
        start_time[0] = now
        percent = current * 100 / total
        status = f"{base_text}\n\n🚀 𝗟𝗶𝘃𝗲 𝗣𝗿𝗼𝗴𝗿𝗲𝘀𝘀: {percent:.1f}%\n💾 𝗦𝗶𝘇𝗲: {get_size(current)} / {get_size(total)}"
        try: await client.edit_message_text(message.chat.id, message.id, status)
        except: pass

def get_size(bytes_size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0: return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0

def get_file_size(msg: Message):
    for t in ["document", "video", "audio", "animation", "voice", "photo"]:
        if getattr(msg, t, None): return getattr(msg, t).file_size
    return 0

def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    for t in ["document", "video", "animation", "sticker", "voice", "audio", "photo", "text"]:
        if getattr(msg, t, None): return t.capitalize()

# ==========================================
# 🛑 FORCE SUB SYSTEM
# ==========================================
async def check_fsub(client, user_id):
    if user_id in ADMIN_IDS: return True
    if not batch_temp.FORCE_SUB_CHANNELS: return True
    not_joined = []
    for chat_id in batch_temp.FORCE_SUB_CHANNELS:
        try:
            member = await client.get_chat_member(chat_id, user_id)
            if member.status in [enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.LEFT]: not_joined.append(chat_id)
        except UserNotParticipant: not_joined.append(chat_id)
        except Exception: pass 
    
    if not_joined:
        buttons = []
        for chat_id in not_joined:
            try:
                chat = await client.get_chat(chat_id)
                link = chat.invite_link if chat.invite_link else await client.export_chat_invite_link(chat_id)
                buttons.append([InlineKeyboardButton(f"🔗 Join {chat.title}", url=link)])
            except: pass
        if buttons: return buttons
    return True

# ==========================================
# 🧠 AUTO CAPTION EXTRACTOR (AI PARSER)
# ==========================================
def parse_pro_caption(raw_text):
    if not raw_text or ("Title:" not in raw_text and "VIDEO ID:" not in raw_text and "FILE ID:" not in raw_text):
        return raw_text # Agar original text naye wale setup jaisa nahi hai to waisa hi chhod do
        
    try:
        # Extract ID
        id_match = re.search(r'(?:VIDEO|FILE) ID:\s*(\d+)', raw_text, re.IGNORECASE)
        vid_id = id_match.group(1) if id_match else "N/A"
        
        # Extract Raw Fields
        title_match = re.search(r'📄 Title:\s*(.*)', raw_text)
        raw_title = title_match.group(1).strip() if title_match else ""
        
        batch_match = re.search(r'🎓 Batch Name\s*:\s*(.*)', raw_text)
        batch = batch_match.group(1).strip() if batch_match else "N/A"
        
        subject_match = re.search(r'📚 Subject Name\s*:\s*(.*)', raw_text)
        raw_subject = subject_match.group(1).strip() if subject_match else "N/A"
        
        # Parse logic for Title/Topic
        topic_match = re.search(r'^\((.*?)\)', raw_title)
        topic = topic_match.group(1).strip() if topic_match else "N/A"
        topic = topic.strip("- ")
        
        # Extract Teacher
        teacher = "N/A"
        teacher_match = re.search(r'By\s+(.*?)\s+(?:[A-Za-z\u0900-\u097F]+|\[)', raw_title)
        if teacher_match:
            teacher = teacher_match.group(1).strip()
        else:
            t_match = re.search(r'\((.*?सर.*?\vert{}.*?Mam.*?\vert{}.*?Sir.*?)\)', raw_subject)
            if t_match: teacher = t_match.group(1).strip()
            
        # Clean Subject
        subject = re.sub(r'\(.*?\)', '', raw_subject).strip()
        
        # Extract Quality & Extension
        q_match = re.search(r'(\d+x\d+)', raw_title)
        quality = f"{q_match.group(1)} HD" if q_match else "N/A"
        ext = raw_title.split('.')[-1].upper() if '.' in raw_title else "N/A"
        
        # Build PRO Format Output
        is_pdf = ext in ['PDF', 'DOC', 'DOCX', 'ZIP', 'PPT', 'TXT']
        
        if is_pdf:
            cap = "╭━━━ 📁 FILE DETAILS ━━━╮\n"
            cap += f"🆔 File ID: {vid_id}\n"
            cap += f"📄 Title: {topic}\n"
            cap += f"📚 Batch Name: {batch}\n"
            cap += f"📖 Subject: {subject}\n"
            if teacher != "N/A": cap += f"👨‍🏫 Teacher: {teacher}\n"
            cap += f"📁 Format: {ext}\n"
            cap += f"📥 Downloaded By: 𝕮𝖍𝖆𝖚𝖉𝖍𝖆𝖗𝖄\n"
            cap += f"╰━━━━━━━━━━━━━━━━━━╯"
        else:
            cap = "╭━━━ 🎬 VIDEO DETAILS ━━━╮\n"
            cap += f"🆔 Video ID: {vid_id}\n"
            cap += f"🎥 Title: {topic}\n"
            cap += f"📚 Batch Name: {batch}\n"
            cap += f"📖 Subject: {subject}\n"
            if teacher != "N/A": cap += f"👩‍🏫 Teacher: {teacher}\n"
            if quality != "N/A": cap += f"🎞️ Quality: {quality}\n"
            cap += f"📁 Format: {ext}\n"
            cap += f"📥 Downloaded By: 𝕮𝖍𝖆𝖚𝖉𝖍𝖆𝖗𝖄\n"
            cap += f"╰━━━━━━━━━━━━━━━━━━╯"
        return cap
    except Exception as e:
        return raw_text # Any failure will safely return original text

# ==========================================
# PRO UI & TEXT VARIABLES
# ==========================================
DEMO_OVER_TEXT = "<b>🚫 Arey Bhai! Demo Limit Over! 😂</b>\n\n<i>(Limit: Max 5 Files ya 50MB Size).</i>\n\n💎 <b>Apna PRO Bot Banwayein!</b>\nBina kisi limit ke apna khud ka powerful bot banwane ke liye Admin se contact karein 👇"
BUY_PRO_BUTTON = InlineKeyboardMarkup([[InlineKeyboardButton("👑 Buy PRO Code / Contact Admin", url="https://t.me/kingvj01")]])
HELP_TEXT = "╭━━━ 🛠 𝗛𝗢𝗪 𝗧𝗢 𝗨𝗦𝗘 𝗕𝗢𝗧 🛠 ━━━╮\n\n💡 𝗦𝗧𝗘𝗣𝗦:\n𝟭. `/login` se apna account connect karein.\n𝟮. Apne target channel ka msg forward karein taaki Auto-Upload set ho.\n𝟯. Restricted link bhejein.\n𝟰. <b>Edit Menu</b> khulega jahan aap Replace, Delete aur Link set kar sakte hain.\n𝟱. 'Start Batch' dabayein!\n\n╰━━━ ⚙️ 𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬 𝗣𝗥𝗢 Jaat ⚙️ ━━━╯"

def get_welcome_text(first_name):
    return f"╭━━━ ⚡ 𝗥𝗘𝗦 𝗖𝗢𝗡𝗧𝗘𝗡𝗧 𝗦𝗔𝗩𝗘𝗥 ⚡ ━━━╮\n\n👋 𝗪𝗘𝗟𝗖𝗢𝗠𝗘, {first_name}!\n\n🤖 𝗬𝗢𝗨𝗥 𝗔𝗟𝗟-𝗜𝗡-𝗢𝗡𝗘 𝗖𝗢𝗡𝗧𝗘𝗡𝗧 𝗧𝗢𝗢𝗟 🚀\n\n┏━━━━━━━━━━━━━━━━━━━━┓\n┃ 💎 𝗣𝗥𝗢 𝗕𝗢𝗧 𝗙𝗘𝗔𝗧𝗨𝗥𝗘𝗦\n┣━━━━━━━━━━━━━━━━━━━━┫\n┃ 🔑 Secure Login\n┃ 📡 Multiple Auto-Channels\n┃ 🧠 Auto Content Parser (AI)\n┃ 🔗 Smart Link Replacer\n┃ 🔄 Retry Failed Links\n┗━━━━━━━━━━━━━━━━━━━━┛\n\n👇 𝗚𝗘𝗧 𝗦𝗧𝗔𝗥𝗧𝗘𝗗 𝗡𝗢𝗪 👇\n╰━━━ ⚙️ 𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬 𝗣𝗥𝗢 Jaat ⚙️ ━━━╯"

def get_home_buttons():
    return [
        [InlineKeyboardButton("🔑 𝗟𝗼𝗴𝗶𝗻", callback_data="start_login"), InlineKeyboardButton("📊 𝗦𝘁𝗮𝘁𝘀 (Admin)", callback_data="show_stats")],
        [InlineKeyboardButton("❣️ Dᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/kingvj01"), InlineKeyboardButton("❓ 𝗛𝗲𝗹𝗽", callback_data="show_help")]
    ]

# ==========================================
# COMMANDS & ADMIN F-SUB LOGIC
# ==========================================
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    fsub_check = await check_fsub(client, message.from_user.id)
    if fsub_check is not True and len(fsub_check) > 0:
        return await message.reply("❌ **Pehle in channels ko Join karo, fir /start bhejna:**", reply_markup=InlineKeyboardMarkup(fsub_check))

    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    
    try:
        cmds = [BotCommand("start", "🚀 Start"), BotCommand("login", "🔑 Login"), BotCommand("logout", "🚪 Logout"), BotCommand("help", "❓ Help"), BotCommand("clear", "🗑 Clear Channels"), BotCommand("cancel", "🛑 Cancel Task")]
        if message.from_user.id in ADMIN_IDS:
            cmds.extend([BotCommand("stats", "📊 Stats"), BotCommand("addfsub", "➕ Add FSub"), BotCommand("fsublist", "📋 FSub List"), BotCommand("delfsub", "🗑 Del FSub")])
        await client.set_bot_commands(cmds)
    except: pass 

    await client.send_message(chat_id=message.chat.id, text=get_welcome_text(message.from_user.first_name or "User"), reply_markup=InlineKeyboardMarkup(get_home_buttons()), reply_to_message_id=message.id)

@Client.on_message(filters.command(["addfsub", "fsublist", "delfsub", "stats", "help", "clear", "cancel"]) & filters.private)
async def admin_commands(client, message):
    cmd = message.command[0]
    user_id = message.from_user.id
    if cmd == "help": return await message.reply(HELP_TEXT)
    if cmd == "cancel": 
        batch_temp.IS_BATCH[user_id] = True
        return await message.reply("**🛑 Task Cancelled.**")
    if cmd == "clear":
        batch_temp.USER_DESTINATIONS[user_id] = []
        return await message.reply("🗑️ **Auto-Upload Channels Cleared!**")
    
    if user_id not in ADMIN_IDS: return
    if cmd == "stats":
        total = await db.total_users_count()
        return await message.reply(f"📊 **STATS:**\n👥 Users: {total}\n⬇️ Download: {get_size(ServerStats.downloaded_bytes)}\n⬆️ Upload: {get_size(ServerStats.uploaded_bytes)}")
    if cmd == "addfsub":
        if message.reply_to_message and message.reply_to_message.forward_from_chat:
            cid = message.reply_to_message.forward_from_chat.id
            if cid not in batch_temp.FORCE_SUB_CHANNELS: batch_temp.FORCE_SUB_CHANNELS.append(cid)
            return await message.reply(f"✅ Added {cid} to F-Sub!")
    if cmd == "fsublist":
        return await message.reply("📋 **F-Sub:**\n" + "\n".join(str(x) for x in batch_temp.FORCE_SUB_CHANNELS))
    if cmd == "delfsub":
        try: batch_temp.FORCE_SUB_CHANNELS.remove(int(message.text.split()[1]))
        except: pass
        return await message.reply("✅ Channel removed.")

@Client.on_message(filters.forwarded & filters.private)
async def add_target_channel(client: Client, message: Message):
    if message.forward_from_chat and message.forward_from_chat.type == enums.ChatType.CHANNEL:
        if message.reply_to_message: return
        chat_id = message.forward_from_chat.id
        user_id = message.from_user.id
        if user_id not in batch_temp.USER_DESTINATIONS: batch_temp.USER_DESTINATIONS[user_id] = []
        if chat_id not in batch_temp.USER_DESTINATIONS[user_id]:
            batch_temp.USER_DESTINATIONS[user_id].append(chat_id)
            await message.reply_text(f"✅ **Auto-Upload Set:** {message.forward_from_chat.title}")

# ==========================================
# 🛑 PRO EDIT MENU & STATE MANAGER
# ==========================================
async def show_edit_menu(client, message, user_id):
    data = batch_temp.BATCH_DATA[user_id]
    
    r_len = len(data['replace'])
    d_len = len(data['delete'])
    l_text = f"{data['link_replace']['name']}" if data['link_replace'] else "None"
    
    text = f"🛠 **𝗣𝗥𝗢 𝗕𝗔𝗧𝗖𝗛 𝗖𝗢𝗡𝗙𝗜𝗚𝗨𝗥𝗔𝗧𝗜𝗢𝗡**\n\n"
    text += f"🔗 **Link Replace:** `{l_text}`\n"
    text += f"🔄 **Replace Words:** `{r_len} pairs`\n"
    text += f"🗑 **Delete Words:** `{d_len} words`\n"
    text += f"🤖 **Auto Parser:** `Active ✅ (Automatically designs caption)`\n\n"
    text += "👇 *Select options below to edit or Start processing:*"
    
    buttons = [
        [InlineKeyboardButton("🔗 Edit Links", callback_data="edit_link"), InlineKeyboardButton("🔄 Replace Text", callback_data="edit_replace")],
        [InlineKeyboardButton("🗑 Delete Words", callback_data="edit_delete")],
        [InlineKeyboardButton("▶️ 𝗦𝗧𝗔𝗥𝗧 𝗕𝗔𝗧𝗖𝗛", callback_data="start_processing")]
    ]
    if 'menu_msg' in data:
        try: await data['menu_msg'].edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
        except: pass
    else:
        msg = await client.send_message(message.chat.id, text, reply_markup=InlineKeyboardMarkup(buttons))
        batch_temp.BATCH_DATA[user_id]['menu_msg'] = msg

@Client.on_message(filters.text & filters.private)
async def handle_text_and_links(client: Client, message: Message):
    user_id = message.from_user.id
    if message.text.startswith("/"): return

    # --- STATE MANAGER FOR EDITING ---
    state = batch_temp.USER_STATE.get(user_id)
    if state:
        data = batch_temp.BATCH_DATA.get(user_id)
        if not data: return
        
        if message.text.lower() == "cancel":
            batch_temp.USER_STATE[user_id] = None
            await message.reply("❌ Edit cancelled.")
            return await show_edit_menu(client, message, user_id)

        # LINK 2-STEP SETUP
        if state == "WAIT_LINK_NAME":
            data['temp_link_name'] = message.text.strip()
            batch_temp.USER_STATE[user_id] = "WAIT_LINK_URL"
            await message.reply(f"🔗 Name saved: **{data['temp_link_name']}**\n\nAb us link ki **Target URL** bhejein (Jaise: `https://t.me/projaat`)\n\n*(Type 'cancel' to abort)*")
            return

        elif state == "WAIT_LINK_URL":
            if not message.text.startswith("http"):
                return await message.reply("❌ Invalid URL! Hamesha 'http' se start hone wali link bhejein.\nTry Again ya 'cancel' bhejein.")
            
            name = data.pop('temp_link_name')
            url = message.text.strip()
            data['link_replace'] = {'name': name, 'url': url}
            
        elif state == "WAIT_REPLACE":
            try:
                pairs = message.text.split(",")
                for p in pairs:
                    old, new = p.split(":")
                    data['replace'][old.strip()] = new.strip()
            except: return await message.reply("❌ Invalid format! Use `Old:New, Old2:New2`")
            
        elif state == "WAIT_DELETE":
            words = message.text.split(",")
            for w in words: data['delete'].append(w.strip())
            
        batch_temp.USER_STATE[user_id] = None
        await message.delete() 
        return await show_edit_menu(client, message, user_id)

    # --- MAIN LINK INTERCEPTOR ---
    if "https://t.me/" in message.text:
        fsub_check = await check_fsub(client, message.from_user.id)
        if fsub_check is not True and len(fsub_check) > 0:
            return await message.reply("❌ **Pehle in channels ko join karo!**", reply_markup=InlineKeyboardMarkup(fsub_check))

        if batch_temp.IS_BATCH.get(user_id) == False:
            return await message.reply_text("**⏳ Ek task pehle se chal raha hai... wait karein ya /cancel karein.**")
        
        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        try: toID = int(temp[1].strip())
        except: toID = fromID

        chat_or_user = datas[4] if "t.me/c/" in message.text or "t.me/b/" in message.text else datas[3]
        is_private = True if "t.me/c/" in message.text else False
        if is_private: chat_or_user = int("-100" + str(chat_or_user))

        links_list = list(range(fromID, toID + 1))

        batch_temp.BATCH_DATA[user_id] = {
            'target': chat_or_user,
            'links': links_list,
            'link_replace': None, 
            'replace': {},
            'delete': [],
            'failed_links': []
        }
        await show_edit_menu(client, message, user_id)

# ==========================================
# CALLBACK HANDLERS
# ==========================================
@Client.on_callback_query()
async def callback_handler(client: Client, query):
    data = query.data
    user_id = query.from_user.id
    
    if data == "start_login":
        await query.answer("Starting Login Process...")
        from TechVJ.generate import main as login_process
        mock_msg = query.message
        mock_msg.from_user = query.from_user
        mock_msg.text = "/login"
        await query.message.delete()
        await login_process(client, mock_msg)
    
    elif data == "show_help":
        await query.message.edit_text(HELP_TEXT, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="back_start")]]))
    elif data == "back_start":
        await query.message.edit_text(get_welcome_text(query.from_user.first_name), reply_markup=InlineKeyboardMarkup(get_home_buttons()))
    
    elif data.startswith("edit_"):
        action = data.split("_")[1]
        
        if action == "link":
            batch_temp.USER_STATE[user_id] = "WAIT_LINK_NAME"
            await query.message.reply("🔗 **Custom Link Setup (Step 1 of 2)**\n\nSabse pehle mujhe us link ka **NAAM** bhejein (Jaise: `Join PRO Jaat`).\n\n*(Type 'cancel' to abort)*")
        elif action == "replace":
            batch_temp.USER_STATE[user_id] = "WAIT_REPLACE"
            await query.message.reply("🔄 **Send Words to Replace:**\nFormat: `OldWord:NewWord, BadWord:GoodWord`\n\n*(Type 'cancel' to abort)*")
        elif action == "delete":
            batch_temp.USER_STATE[user_id] = "WAIT_DELETE"
            await query.message.reply("🗑 **Send Words to Delete:**\nFormat: `Word1, Word2, Link.com`\n\n*(Type 'cancel' to abort)*")
        await query.answer()

    elif data == "start_processing":
        await query.message.delete()
        await process_batch(client, query.message, user_id, batch_temp.BATCH_DATA[user_id]['links'])

    elif data == "retry_failed":
        failed_links = batch_temp.BATCH_DATA[user_id].get('failed_links', [])
        if not failed_links: return await query.answer("No failed links!", show_alert=True)
        await query.message.delete()
        batch_temp.BATCH_DATA[user_id]['failed_links'] = [] 
        await process_batch(client, query.message, user_id, failed_links)

# ==========================================
# MAIN CORE PROCESSING
# ==========================================
async def process_batch(client, message, user_id, links_list):
    b_data = batch_temp.BATCH_DATA[user_id]
    target_chat = b_data['target']
    total = len(links_list)
    
    dash_text = f"📦 **𝗕𝗮𝘁𝗰𝗵 𝗦𝘁𝗮𝗿𝘁𝗲𝗱**\n🔢 **𝗧𝗼𝘁𝗮𝗹 𝗟𝗶𝗻𝗸𝘀:** {total}\n✅ **𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱𝗲𝗱:** 0\n⏳ **𝗥𝗲𝗺𝗮𝗶𝗻𝗶𝗻𝗴:** {total}\n❌ **𝗙𝗮𝗶𝗹𝗲𝗱:** 0\n\n🚀 𝗦𝘁𝗮𝘁𝘂𝘀: Connecting..."
    dash_msg = await client.send_message(message.chat.id, dash_text)

    if LOGIN_SYSTEM:
        user_data = await db.get_session(user_id)
        if not user_data: return await message.reply("**Login Required! Use /login**")
        api_id = int(await db.get_api_id(user_id))
        api_hash = await db.get_api_hash(user_id)
        acc = Client("saverestricted", session_string=user_data, api_hash=api_hash, api_id=api_id)
        await acc.connect()
    else: acc = TechVJUser

    batch_temp.IS_BATCH[user_id] = False
    success = 0
    failed = 0

    for msgid in links_list:
        if batch_temp.IS_BATCH.get(user_id): break
        
        remaining = total - success - failed
        base_status = f"📦 **𝗕𝗮𝘁𝗰𝗵 𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴**\n🔢 **𝗧𝗼𝘁𝗮𝗹 𝗟𝗶𝗻𝗸𝘀:** {total}\n✅ **𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱𝗲𝗱:** {success}\n⏳ **𝗥𝗲𝗺𝗮𝗶𝗻𝗶𝗻𝗴:** {remaining}\n❌ **𝗙𝗮𝗶𝗹𝗲𝗱:** {failed}"
        await dash_msg.edit_text(f"{base_status}\n\n🚀 𝗦𝘁𝗮𝘁𝘂𝘀: Extracting Message ID {msgid}...")

        try:
            res = await handle_file_transfer(client, acc, message, user_id, target_chat, msgid, b_data, dash_msg, base_status)
            if res: success += 1
            else: 
                failed += 1
                b_data['failed_links'].append(msgid)
        except:
            failed += 1
            b_data['failed_links'].append(msgid)

        await asyncio.sleep(WAITING_TIME)

    if LOGIN_SYSTEM:
        try: await acc.disconnect()
        except: pass
    
    batch_temp.IS_BATCH[user_id] = True
    
    final_text = f"🏁 **𝗕𝗔𝗧𝗖𝗛 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗** 🏁\n\n✅ **𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹:** {success}\n❌ **𝗙𝗮𝗶𝗹𝗲𝗱:** {failed}"
    buttons = []
    if failed > 0: buttons.append([InlineKeyboardButton("🔄 Retry Failed Links", callback_data="retry_failed")])
    await dash_msg.edit_text(final_text, reply_markup=InlineKeyboardMarkup(buttons) if buttons else None)


async def handle_file_transfer(client, acc, message, user_id, chatid, msgid, b_data, dash_msg, base_status):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty: return False
    msg_type = get_message_type(msg)
    if not msg_type: return False
    
    is_admin = user_id in ADMIN_IDS

    if not is_admin:
        if batch_temp.USER_DOWNLOAD_COUNT.get(user_id, 0) >= 5:
            await client.send_message(message.chat.id, DEMO_OVER_TEXT, reply_markup=BUY_PRO_BUTTON, parse_mode=enums.ParseMode.HTML)
            return False
        if get_file_size(msg) > (50 * 1024 * 1024):
            await client.send_message(message.chat.id, DEMO_OVER_TEXT, reply_markup=BUY_PRO_BUTTON, parse_mode=enums.ParseMode.HTML)
            return False

    dest_chats = batch_temp.USER_DESTINATIONS.get(user_id, [])
    if not dest_chats: dest_chats = [int(CHANNEL_ID)] if CHANNEL_ID else [message.chat.id]
    primary_chat = dest_chats[0]

    # ==========================================
    # 🧠 PRO SMART CAPTION ENGINE 
    # ==========================================
    raw_caption = msg.caption.html if msg.caption else (msg.text.html if msg.text else "")
    if not raw_caption and msg.caption: raw_caption = msg.caption 
    
    if raw_caption:
        # MAGIC: AI Parser will auto-format the caption
        text_data = parse_pro_caption(raw_caption)
        
        # --- Apply Delete ---
        for word in b_data['delete']: text_data = text_data.replace(word, "")
            
        # --- Apply Replace ---
        for old, new in b_data['replace'].items(): text_data = text_data.replace(old, new)
            
        # --- Apply Link Replacer ---
        if b_data['link_replace']:
            name = b_data['link_replace']['name']
            url = b_data['link_replace']['url']
            custom_hyperlink = f"<a href='{url}'>{name}</a>"
            text_data = re.sub(r'<a href="[^"]+">[^<]+</a>', custom_hyperlink, text_data)
            text_data = re.sub(r'(?<!["\'])(https?://\S+)', custom_hyperlink, text_data)
        
        if msg.caption: caption = text_data
        else: msg.text = text_data
    else: 
        caption = None

    if "Text" == msg_type:
        try:
            sent = await client.send_message(primary_chat, msg.text, parse_mode=enums.ParseMode.HTML)
            for c in dest_chats[1:]: await sent.copy(c)
            return True
        except: return False

    start_time = [time.time()]
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[client, dash_msg, start_time, base_status + "\n\n📥 **Status:** Downloading..."])
        if file and os.path.exists(file): ServerStats.downloaded_bytes += os.path.getsize(file)
    except: return False

    sent_msg = None
    start_time = [time.time()]
    up_status = base_status + "\n\n📤 **Status:** Uploading..."
    
    try:
        if "Document" == msg_type:
            ph = await acc.download_media(msg.document.thumbs[0].file_id) if getattr(msg.document, 'thumbs', None) else None
            sent_msg = await client.send_document(primary_chat, file, thumb=ph, caption=caption, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[client, dash_msg, start_time, up_status])
            if ph: os.remove(ph)
        elif "Video" == msg_type:
            ph = await acc.download_media(msg.video.thumbs[0].file_id) if getattr(msg.video, 'thumbs', None) else None
            sent_msg = await client.send_video(primary_chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph, caption=caption, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[client, dash_msg, start_time, up_status])
            if ph: os.remove(ph)
        elif "Audio" == msg_type:
            ph = await acc.download_media(msg.audio.thumbs[0].file_id) if getattr(msg.audio, 'thumbs', None) else None
            sent_msg = await client.send_audio(primary_chat, file, thumb=ph, caption=caption, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[client, dash_msg, start_time, up_status])   
            if ph: os.remove(ph)
        elif "Photo" == msg_type:
            sent_msg = await client.send_photo(primary_chat, file, caption=caption, parse_mode=enums.ParseMode.HTML)
        else:
            func = getattr(client, f"send_{msg_type.lower()}")
            sent_msg = await func(primary_chat, file, caption=caption, parse_mode=enums.ParseMode.HTML) if msg_type not in ["Sticker"] else await func(primary_chat, file)
    except:
        pass

    if sent_msg and os.path.exists(file): ServerStats.uploaded_bytes += os.path.getsize(file)

    if sent_msg and len(dest_chats) > 1:
        for chat in dest_chats[1:]:
            try: await sent_msg.copy(chat); await asyncio.sleep(0.5)
            except: pass

    if os.path.exists(file): os.remove(file)
    
    if sent_msg:
        if not is_admin: batch_temp.USER_DOWNLOAD_COUNT[user_id] = batch_temp.USER_DOWNLOAD_COUNT.get(user_id, 0) + 1
        return True
    return False
