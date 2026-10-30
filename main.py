import asyncio
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- الإعدادات ---
API_ID = 23032698
API_HASH = '99ad65a5fcd38203621cb20acd2aaba5'

# --- تغيير ملف حفظ الجلسة ---
# الطريقة 1: استخدام ملف جلسة باسم مخصص (اختر أي اسم تحبه)
SESSION_NAME = 'my_telegram_session'  # غيّر هذا الاسم كما تريد
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# --- أو إذا تريد استخدام String Session بدلاً من الملف ---
# STRING_SESSION = '1BJWap1sBu75fZCxfw8EiaRJASH4UbGooQSohpqcQ3P2je9os_xxvtCF--ovg-pMoSEFa_du34RsvZSRxLaHHg_HEYFcAIvgNu35ntQRLCC9kw15MP7BUr7ZX3ZXLUptclakk-RF6JbVpHfukUNW9R0EnxhOOjkbH_kstLimbyCDvwfzMb99nLhgczoddsUeA_FNhAgyEotfEIpr86mg2eIPfpEbkkUQjob8LQG6QTopJiWlyTUOG5EkaLUhk1a66uiMF7uAOAzw92NcD8LsYf9iGJr5ZJrCLNOYg27ZAF6LrPQ662fmI-Q99zkDXMb2TQpAxEHzrlLd6AIvUPP5d0QStStUK1AQ='
# client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

# --- يمكنك أيضاً وضع مسار مختلف لحفظ الملف ---
# SESSION_NAME = 'sessions/my_session'  # سيتم حفظه في مجلد sessions
# os.makedirs('sessions', exist_ok=True)  # ينشئ المجلد إذا لم يكن موجوداً
# client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# --- إعدادات المتغيرات ---
SAVE_STATUS = False
AUTO_FORWARD_GROUPS = []

# --- ميزة الدز المطور ---
@client.on(events.NewMessage(pattern=r'\.دزه (.*)', outgoing=True))
async def send_clean_media(event):
    input_target = event.pattern_match.group(1).strip()
    if not event.is_reply:
        await event.delete()
        return 
    try:
        target = int(input_target) if input_target.isdigit() else input_target
        reply_msg = await event.get_reply_message()
        if reply_msg and reply_msg.media:
            path = await reply_msg.download_media()
            await client.send_file(target, path, ttl=15, force_document=False)
            await event.delete()
            if os.path.exists(path): os.remove(path)
        else:
            await event.delete()
    except Exception:
        await event.delete()

# --- ميزة دزه جاهز ---
@client.on(events.NewMessage(pattern=r'\.دزه_جاهز (.*)', outgoing=True))
async def send_ready_media(event):
    targets_input = event.pattern_match.group(1).strip()
    if not event.is_reply:
        await event.edit("⚠️ **يجب الرد على الوسائط**")
        await asyncio.sleep(2)
        await event.delete()
        return
    
    targets_list = [t.strip() for t in targets_input.replace('،', ',').split(',')]
    reply_msg = await event.get_reply_message()
    if not reply_msg or not reply_msg.media:
        await event.edit("⚠️ **الرسالة المدعومة يجب أن تحتوي على وسائط**")
        await asyncio.sleep(2)
        await event.delete()
        return
    
    parsed_targets = []
    for target in targets_list:
        try:
            parsed_targets.append(int(target) if target.isdigit() else target)
        except:
            continue
    
    if not parsed_targets:
        await event.edit("⚠️ **لم يتم التعرف على أي أهداف صحيحة**")
        await asyncio.sleep(2)
        await event.delete()
        return
    
    path = await reply_msg.download_media()
    success_count = 0
    
    for target in parsed_targets:
        try:
            await client.send_file(target, path, ttl=15, force_document=False)
            success_count += 1
            await asyncio.sleep(1)
        except Exception as e:
            print(f"خطأ في الإرسال إلى {target}: {e}")
    
    if os.path.exists(path):
        os.remove(path)
    
    await event.edit(f"✅ **تم إرسال الدزة الجاهزة إلى {success_count} من {len(parsed_targets)} جهة**")
    await asyncio.sleep(3)
    await event.delete()

# --- ميزة حفظ الذاتيات ---
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_save(event):
    global SAVE_STATUS
    if SAVE_STATUS and event.media:
        has_ttl = getattr(event.media, 'ttl_seconds', None)
        if has_ttl:
            try:
                media_file = await event.download_media()
                await client.send_file("me", media_file, caption=f"📥 تم سحب ذاتية من: `{event.sender_id}`")
                if os.path.exists(media_file): os.remove(media_file)
            except: pass

# --- أوامر التحكم ---
@client.on(events.NewMessage(pattern=r'\.الذاتية (تشغيل|تعطيل)', outgoing=True))
async def toggle_save(event):
    global SAVE_STATUS
    cmd = event.pattern_match.group(1)
    SAVE_STATUS = (cmd == "تشغيل")
    await event.edit(f"✅ تم **{cmd}** حفظ الذاتيات.")
    await asyncio.sleep(2)
    await event.delete()

@client.on(events.NewMessage(pattern=r'\.فحص', outgoing=True))
async def ping(event):
    await event.edit("**🚀 السكربت شغال وجاهز!**")
    await asyncio.sleep(2)
    await event.delete()

# --- أمر مساعدة ---
@client.on(events.NewMessage(pattern=r'\.مساعدة', outgoing=True))
async def help_command(event):
    help_text = """
**📋 قائمة الأوامر:**

1. `.دزه [آيدي/يوزر]` - إرسال الوسائط المردود عليها مع TTL 15 ثانية
2. `.دزه_جاهز [آيدي1, آيدي2, يوزر1, ...]` - إرسال الوسائط لأكثر من جهة دفعة واحدة
3. `.الذاتية تشغيل` - تفعيل حفظ الذاتيات
4. `.الذاتية تعطيل` - تعطيل حفظ الذاتيات
5. `.فحص` - التأكد من أن السكربت يعمل
6. `.مساعدة` - عرض هذه القائمة
"""
    await event.edit(help_text)
    await asyncio.sleep(10)
    await event.delete()

async def main():
    print("🔍 جاري الاتصال بتيليجرام...")
    print(f"📁 سيتم حفظ الجلسة في ملف: {SESSION_NAME}.session")
    await client.start()
    print("✅ السكربت شغال الآن!")
    print("📌 استخدم .مساعدة لعرض قائمة الأوامر")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
