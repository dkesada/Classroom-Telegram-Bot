#-*. coding: utf-8 -*-
import time
import os.path
import telepot
import threading 
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from Queue import Queue


# This list saves the chat_id of the alumns who enter the bot
users = []
# Here I save the chat_id of the administrator when he first enters the bot
# In the second position there's a 0 if we are not in a poll, 1 in other case
admin = [0,0,0]
# The passwords that the bot asks from a user or an admin
claveAdmin = '1720'
claveUser = '3411'

senders = []
buzon = []
# Data for the polls
enc = []
opciones = []
res = []
cont = []

def leerCopiaSeg():
    cop = open('copiaSeg','r')
    admin[0] = int(cop.readline())
    for u in cop:
        users.append(int(u))
    cop.close()

# If there was a copy of the data, we load the previous admin and users
if os.path.exists('copiaSeg'):
 leerCopiaSeg()


# The different keyboards that the bot will use

keyboardLogin = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='Alumno', callback_data='alumno'),
                   InlineKeyboardButton(text='Profesor', callback_data='profesor')],
               ])
keyboardUser = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='Enviar mensaje al profesor.', callback_data='msg_user')],
               ])

keyboardAdminMsg = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='Enviar mensaje al grupo.', callback_data='difusion')],
                   [InlineKeyboardButton(text='Hacer una encuesta.', callback_data='encuesta')],
                   [InlineKeyboardButton(text='Ver siguiente mensaje del buzón.', callback_data='msg_buzon')],
               ])
keyboardAdminSinMsg = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='Enviar mensaje al grupo.', callback_data='difusion')],
                   [InlineKeyboardButton(text='Hacer una encuesta.', callback_data='encuesta')],
               ])
keyboardMensaje = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='Cancelar', callback_data='cancelar')],
               ])
keyboardLeyendo = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='Volver', callback_data='volver')],
               ])

# Function that creates a custom keyboard for the poll.
# The first param is the text of the mail, the next ones are the poll options separeted with semicolons
def encuesta(op):
 listado = op.split(';') # Options separated with semicolons
 texto = listado.pop(0)
 botones = []
 n = 0
 
 for i in listado:
  res.append(0)
  if i[0] == ' ':
   i = i[1:]
  botones.append([InlineKeyboardButton(text=i, callback_data='opcion' + str(n))])
  opciones.append(i)
  n = n+1;
 
 enc.append(texto)
 enc.append(InlineKeyboardMarkup(inline_keyboard = botones))
 
 botones.append([InlineKeyboardButton(text='(Aspecto correcto, crear encuesta.)', callback_data='enviarEnc')])
 botones.append([InlineKeyboardButton(text='(Aspecto incorrecto, rehacer encuesta.)', callback_data='encuesta')])
 botones.append([InlineKeyboardButton(text='(Cancelar)', callback_data='cancelar')])
  
 return [texto, InlineKeyboardMarkup(inline_keyboard = botones)]


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)   
    
    if content_type == 'text':
     if msg['text'] == '/start':
      bot.sendMessage(chat_id, 'Bienvenido al bot de ELP. ¿Eres un alumno o el profesor?', reply_markup=keyboardLogin)
     if msg['text'] == '/mostrar' and chat_id in users:
      bot.sendMessage(chat_id, 'Puede enviar un mensaje al profesor pulsando el boton de abajo.', reply_markup=keyboardUser)
     if msg['text'] == '/mostrar' and chat_id == admin[0]:
      menuAdmin()
     elif msg['text'] == claveAdmin and admin[0] == 0:
      admin[0] = chat_id
      if not os.path.exists('copiaSeg'):
       crearCopiaSeg()
      menuAdmin()
     elif msg['text'] == claveUser and not chat_id in users:
      bot.sendMessage(chat_id, 'Clave correcta. Bienvenido al bot de ELP. Cuando el profesor envíe algo yo te lo haré llegar. Si tienes algún mensaje para el profesor o alguna sugerencia, puedo hacérselo llegar si pulsas el botón de abajo.', reply_markup=keyboardUser)
      users.append(chat_id)
      anadirACopiaSeg(chat_id)
     elif chat_id in senders:
      senders.remove(chat_id)
      buzon.append(msg['text'])
      bot.sendMessage(chat_id, 'Mensaje enviado.', reply_markup=keyboardUser)
     elif chat_id == admin[0] and admin[1] == 1 and msg['text'] == '/finEncuesta':
      admin[1] = 0
      enviarResultados()
     elif chat_id == admin[0] and admin[1] == 1:
      res = encuesta(msg['text'])
      bot.sendMessage(chat_id, res[0], reply_markup=res[1])
     elif chat_id == admin[0] and admin[2] == 1:
      difusion(msg['text'])
      bot.sendMessage(chat_id, "Mensaje enviado al grupo.")
      menuAdmin()
     
      

# Here we deal with keyboard input from our custom keyboards
def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    
    if(query_data != 'alumno' and query_data != 'profesor'):
     bot.answerCallbackQuery(query_id)
    
    if query_data == 'alumno':
      bot.answerCallbackQuery(query_id, text='Introduzca el código de los alumnos.')
    elif query_data == 'profesor':
      bot.answerCallbackQuery(query_id, text='Introduzca el código del profesor.')
    elif query_data == 'msg_user':     
      senders.append(from_id)
      bot.sendMessage(from_id, "Escriba el mensaje que quiere enviar.", reply_markup=keyboardMensaje)
    elif query_data == 'encuesta':
      admin[1] = 1
      bot.sendMessage(from_id, "Escriba el texto del mensaje primero y las opciones a elegir de la encuesta separadas por punto y coma. Ej: Texto del mensaje; Opcion 1; Opcion 2; ...", reply_markup=keyboardMensaje)
    elif query_data == 'difusion':
      admin[2] = 1
      bot.sendMessage(from_id, "Escriba el mensaje que quiere enviar.", reply_markup=keyboardMensaje)
    elif query_data == 'cancelar':
      if from_id == admin[0] and admin[1] == 1: # El admin cancela la encuesta
       admin[1] = 0
       menuAdmin()
      elif from_id == admin[0] and admin[2] == 1: # El admin cancela la encuesta
       admin[2] = 0
       menuAdmin()
      elif from_id in senders: # Un usuario cancela el envio de un mensaje
       senders.remove(from_id)
       bot.sendMessage(from_id, 'Mensaje no enviado.', reply_markup=keyboardUser)
    elif query_data == 'msg_buzon':
     sacarMesajeBuzon()
    elif query_data == 'volver':
     menuAdmin()
    elif query_data == 'enviarEnc':
     comenzarEncuesta()
     bot.sendMessage(from_id, 'Encuesta comenzada. Cuando contesten todos los alumnos o cuando introduzca /finEncuesta le llegarán los resultados.')
     menuAdmin()
    elif len(query_data) == 7 and query_data[0:6] == 'opcion' and (not from_id in cont) and admin[1] == 1:
     respuestaEncuesta(from_id, int(query_data[6]))
      
    
    


def menuAdmin():
 if len(buzon) == 0: # Si no tiene mensajes
  bot.sendMessage(admin[0], 'No tiene mensajes en el buzón. ¿Qué desea hacer?', reply_markup=keyboardAdminSinMsg)
 else:
  n = len(buzon)
  bot.sendMessage(admin[0], txtMensajes(n) + '¿Qué desea hacer?', reply_markup=keyboardAdminMsg)


def txtMensajes(n):
	if n == 1:
		txt = 'Tiene un mensaje. '
	else:
		txt = 'Tiene ' + str(n) + ' mensajes. '
	return txt

def sacarMesajeBuzon():
	if len(buzon) > 0:
		msg = buzon.pop(0)
		bot.sendMessage(admin[0], msg, reply_markup=keyboardLeyendo)

def comenzarEncuesta():
    del cont[:]
    for i in users:
        bot.sendMessage(i, 'Comienza un nueva encuesta:')
        bot.sendMessage(i, enc[0], reply_markup=enc[1])
		
def respuestaEncuesta(from_id, query_data):
    cont.append(from_id)
    res[query_data] = res[query_data] + 1
    bot.sendMessage(from_id, 'Tu respuesta ha sido enviada.')
    
    if(len(users) == sum(res)):
        admin[1] = 0
        enviarResultados()
     
def enviarResultados():
    msg = 'Resultados de la encuesta: '
    for i in range(len(opciones)):
        msg = msg + opciones[i] + ' -> ' + str(res[i]) + ' \n'
    bot.sendMessage(admin[0], msg, reply_markup=keyboardLeyendo)
    del res[:]
    del opciones[:]
    del enc[:]
    
def difusion(msg):
    for i in users:
        bot.sendMessage(i, msg)

def crearCopiaSeg():
	cop = open('copiaSeg','w')
	cop.write(str(admin[0]) + '\n')
	cop.close()

def anadirACopiaSeg(chat_id):
	cop = open('copiaSeg','a')
	cop.write(str(chat_id) + '\n')
	cop.close()

# Token of the bot given by botFather. Here you should put the token of your own bot.
TOKEN = '326265110:AAGuXzJHR0JAwnnHX6LtB6yRQtHpmgIMabU'

bot = telepot.Bot(TOKEN)
# Defining the message_loop like this makes it redirect all text messages to on_chat_message and
# the callback_query generated by the custom keyboards to on_callback_query
bot.message_loop({'chat': on_chat_message, 'callback_query': on_callback_query})
print ('Listening ...')

# Time wait for checking for new messages
while 1:
    time.sleep(5)
