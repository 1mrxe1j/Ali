import asyncio
import os
import sys
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import AuthKeyUnregisteredError, UserDeactivatedError

# --- الإعدادات ---
API_ID = 23032698
API_HASH = '99ad65a5fcd38203621cb20acd2aaba5'

STRING_SESSION = '1ApWapzMBu486tvhLawA4qyW6GGWFoBxLCwx4EkiIbSMD-DADUmF9r7laxvYi5n2TMHXTXSsslT7m8Io2IMIbzq4tK8esbGA5XbTD-LGfttwDJv9N36pfn7HVz2WSycAGPXghvZ9o4oxFc2lWZDhiCdq6I0azYy1v5oYmdyhdmvlzrnbK1IfWfSBm6N8KdLasNdV0UgheEyL31SU61viruBarkfeSfxUgxYhB1r0cItexjCU0dq5iKII0hKw9_7TO3rvON-w1uKH7bznmKeF1VSmGiKNj_4ofJG84pDsMW7l0BVjoN6d01W7hD78ikhFyRdyXhx1ckLwsDMbNQ5X54j-g3-q8RBA='
client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

SAVE_STATUS = False

# --- طباعة الرسائل الصادرة في الشاشة للتأكد من وصول الأحداث ---
@client.on(events.NewMessage(outgoing=True))
async def debug_listener(event):
    print(f"📩 تم التقاط رسالة صادرة: {event.text}")

# --- أمر فحص ---
@client.on(events.NewMessage(pattern=r'^\.فحص$', outgoing=True))
async def ping(event):
    await event.edit("🚀 **السكربت شغال ويستجيب بنجاح!**")

# --- أمر التحكم بالذاتية ---
@client.on(events.NewMessage(pattern=r'^\.الذاتية\s+(تشغيل|تعطيل)$', outgoing=True))
async def toggle_save(event):
    global SAVE_STATUS
    cmd = event.pattern_match.group(1)
    SAVE_STATUS = (cmd == "تشغيل")
    await event.edit(f"✅ تم **{cmd}** حفظ الذاتيات بنجاح.")

# --- أمر مساعدة ---
@client.on(events.NewMessage(pattern=r'^\.مساعدة$', outgoing=True))
async def help_command(event):
    help_text = """
**📋 قائمة الأوامر:**

1. `.دزه [آيدي/يوزر]` - إرسال الوسائط المردود عليها مع TTL 15 ثانية
2. `.دزه_جاهز [آيدي1, آيدي2]` - إرسال الوسائط لأكثر من جهة
3. `.الذاتية تشغيل` - تفعيل حفظ الذاتيات
4. `.الذاتية تعطيل` - تعطيل حفظ الذاتيات
5. `.فحص` - التأكد من استجابة السكربت
"""
    await event.edit(help_text)

# --- ميزة حفظ الذاتيات تلقائياً ---
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
            except Exception as e:
                print(f"خطأ أثناء حفظ الذاتية: {e}")

async def main():
    print("🔍 جاري التحقق من صحة كود السيشن...")
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("❌ خطأ: كود السيشن غير صالح!")
            return

        me = await client.get_me()
        print(f"✅ تم الاتصال بنجاح!")
        print(f"👤 الحساب المتصل: {me.first_name} (ID: {me.id})")
        print("🚀 السكربت يستمع للرسائل الآن...")
        await client.run_until_disconnected()

    except Exception as e:
        print(f"❌ حدث خطأ: {e}")

if __name__ == '__main__':
    asyncio.run(main())
      
