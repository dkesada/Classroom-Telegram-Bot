#-*. coding: utf-8 -*-
import time
import os.path
import telepot
import threading 
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from Queue import Queue


# Esta lista guarda los chat_id de los que entran como alumnos al bot
users = []
# Aquí guardo el chat_id del administrador cuando este acceda por primera vez al bot
# En la segunda posicion hay un 0 si no está creando una encuesta o a 1 en caso contrario
admin = [0,0]
# La clave que pide el bot si entras como administrador o como usuario
claveAdmin = '1720'
claveUser = '3411'
# Lista con los usuarios que están enviando un mensaje
senders = []
buzon = []
# Datos para las encuestas
enc = []
opciones = []
res = []
cont = []

# Si había una copia de seguridad se cargan los datos del admin y los users
if os.path.exists('copiaSeg'):
 leerCopiaSeg()


# Los diferentes teclados que va a usar el bot

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

# Función que crea un teclado personalizado para realizar una encuesta a los integrantes del 
# grupo. El primer parámetro es el texto del mensaje que se enviará con la encuesta, el segundo
# argumento son las opciones a elegir en la encuesta separados por comas
def encuesta(opciones):
 listado = opciones.split(';') # Opciones separadas por punto y coma
 texto = listado.pop(0)
 botones = []
 n = 0
 res = []
 
 for i in listado:
  res.append(0)
  if i[0] == ' ':
   i = i[1:]
  botones.append([InlineKeyboardButton(text=i, callback_data='opcion' + str(n))])
  opciones.append(i)
  n = n+1;
 
 enc = [texto, InlineKeyboardMarkup(inline_keyboard = botones)]
 
 botones.append([InlineKeyboardButton(text='(Aspecto correcto, crear encuesta.)', callback_data='enviarEnc')])
 botones.append([InlineKeyboardButton(text='(Aspecto incorrecto, rehacer encuesta.)', callback_data='encuesta')])
 botones.append([InlineKeyboardButton(text='(Cancelar)', callback_data='cancelar')])
  
 return [texto, InlineKeyboardMarkup(inline_keyboard = botones)]

# Bot que organiza interacciones entre un administrador y los usuarios que se añadan.
# Estas interacciones serán: hacer llegar a los usuarios los mensajes que ponga el administrador
# a través del bot, hacer llegar encuestas que pueda crear el administrador con el bot y 
# hacer llegar sugerencias de manera anónima de los alumnos a un buzón que podrá ver el administrador
 
def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)   
    
    if content_type == 'text':
     if msg['text'] == '/start':
      bot.sendMessage(chat_id, 'Bienvenido al bot de ELP. ¿Eres un alumno o el profesor?', reply_markup=keyboardLogin)
     if msg['text'] == '/mostrar' and chat_id in users:
      bot.sendMessage(chat_id, 'Puede enviar un mensaje al profesor pulsando el boton de abajo.', reply_markup=keyboardUser)
     elif msg['text'] == claveAdmin and admin[0] == 0:
      admin[0] = chat_id
      if not os.path.exists('copiaSeg'):
       crearCopiaSeg()
      bot.sendMessage(chat_id,"", reply_markup=ReplyKeyboardRemove(True))
      menuAdmin()
     elif msg['text'] == claveUser and not chat_id in users:
      bot.sendMessage(chat_id, 'Clave correcta. Bienvenido al bot de ELP. Cuando el profesor envíe algo yo te lo haré llegar. Si tienes algún mensaje para el profesor o alguna sugerencia, puedo hacérselo llegar si pulsas el botón de abajo.', reply_markup=keyboardUser)
      anadirACopiaSeg(chat_id)
     elif chat_id in senders:
      senders.remove(a)
      buzon.append(msg['text'])
      bot.sendMessage(chat_id, 'Mensaje enviado.', reply_markup=keyboardUser)
     elif chat_id == admin[0] and admin[1] == 1 and msg['text'] == '/finEncuesta':
      admin[1] = 0
      enviarResultados()
     elif chat_id == admin[0] and admin[1] == 1:
      res = encuesta(msg['text'])
      bot.sendMessage(chat_id, res[0], reply_markup=res[1])
     
      

# Las pulsaciones en los botones del bot se gestionan en esta función
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
    elif query_data == 'cancelar':
      if from_id == admin[0] and admin[1] == 1: # El admin cancela la encuesta
       admin[1] = 0
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
     bot.sendMenssage(from_id, 'Encuesta comenzada. Cuando contesten todos los alumnos o cuando introduzca /finEncuesta le llegarán los resultados.')
     menuAdmin()
    elif len(query_data) == 7 and query_data[0:6] == 'opcion' and (not from_id in cont) and admin[1] == 1:
     respuestaEncuesta(from_id, query_data)
      
    
    

# Envia el menu principal del bot al admin
def menuAdmin():
 if len(buzon) == 0: # Si no tiene mensajes
  bot.sendMessage(admin[0], 'No tiene mensajes en el buzón. ¿Qué desea hacer?', reply_markup=keyboardAdminSinMsg)
 else:
  n = len(buzon)
  bot.sendMessage(admin[0], txtMensajes(n) + '¿Qué desea hacer?', reply_markup=keyboardAdminMsg)

# Para diferenciar el texto que muestro
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
	cont = []
	for i in users:
		bot.sendMessage(i, 'Comienza un nueva encuesta:')
		bot.sendMessage(i, enc[0], reply_markup=enc[1])
		
def respuestaEncuesta(from_id, query_data):
	cont.append(from_id)
	res[query_data[6]] = res[query_data[6]] + 1
	bot.sendMenssage(from_id, 'Tu respuesta ha sido enviada.')
	
	if(len(users) == sum(res)):
		admin[1] = 0
		enviarResultados()
     
def enviarResultados():
	msg = 'Resultados de la encuesta: '
	for i in range(len(opciones)):
		msg = msg + opciones[i] + ' -> ' + str(res[i]) + ' \n'
	bot.sendMessage(admin[0], msg, reply_markup=keyboardLeyendo)

def leerCopiaSeg():
	cop = open('copiaSeg','r')
	admin[0] = cop.read()
	for u in cop:
		users.append(u)
	cop.close()

def crearCopiaSeg():
	cop = open('copiaSeg','w')
	cop.write(str(admin[0]) + '\n')
	cop.close()

def anadirACopiaSeg(chat_id):
	cop = open('copiaSeg','a')
	cop.write(str(chat_id) + '\n')
	cop.close()

# Token del bot devuelto por botFather
TOKEN = '326265110:AAGuXzJHR0JAwnnHX6LtB6yRQtHpmgIMabU'

bot = telepot.Bot(TOKEN)
# Definir así el message_loop hace que redirija los mensajes de texto a on_chat_message y
# los callback_query generados por el teclado del bot a on_callback_query
bot.message_loop({'chat': on_chat_message, 'callback_query': on_callback_query})
print ('Listening ...')

# Tiempo de espera para comprobar nuevos mensajes
while 1:
    time.sleep(5)
