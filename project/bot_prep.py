from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import apiai, json
import photo_proc
import bot_self_check
updater = Updater(token='583031555:AAHXewUMQq9jL4MNmCuINdZb8iGsvubHTjM') # Токен API к Telegram
dispatcher = updater.dispatcher
# Обработка команд
# start
def startCommand(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Привет, давай пообщаемся? Или скинь мне свою фотку и узнаешь на кого ты похож!')

# обработка текста
def textMessage(bot, update):
    request = apiai.ApiAI('733a0aad1eb0479c88c862e1ec1a26e7').text_request() # Токен API к Dialogflow
    request.lang = 'ru' # На каком языке будет послан запрос
    request.session_id = 'Comparator3000' # ID Сессии диалога (нужно, чтобы потом учить бота)
    request.query = update.message.text # Посылаем запрос к ИИ с сообщением от юзера
    responseJson = json.loads(request.getresponse().read().decode('utf-8'))
    response = responseJson['result']['fulfillment']['speech'] # Разбираем JSON и вытаскиваем ответ
    # Если есть ответ от бота - присылаем юзеру, если нет - бот его не понял
    if response:
        bot.send_message(chat_id=update.message.chat_id, text=response)
    else:
        bot.send_message(chat_id=update.message.chat_id, text='Я Вас не совсем понял!')

# обработка фото
def photoMessage(bot, update):
	# уведомление о получении фото
	bot.send_message(chat_id=update.message.chat_id, text='Я получил твою фотку! Давай ее сравним..')
	# выгрузка фотографии
	request = bot.getFile(update.message.photo[-1].file_id)
	request.download('photo.jpg')
	path = '/photo.jpg'
	# обработка полученной фотографии
	response = photo_proc.class_detector(path)
	# отладочная печать
	#print('I am in photoMessage again')
	bot.send_message(chat_id=update.message.chat_id, text='Мне нужно подумать.. хм..')
	# если вернулась строка - неудача. На фото нет лица или еще что-то
	if  (type(response) is str):
		bot.send_message(chat_id=update.message.chat_id, text=response)
	else:
	# Удача, необходимо вернуть пользователю фотографию человека на которого он похож
	# и имя класса
		bot.send_message(chat_id=update.message.chat_id, text=response[0])
		bot.send_photo(chat_id=update.message.chat_id, photo=open(response[1], 'rb'))

# Хендлеры
start_command_handler = CommandHandler('start', startCommand)
text_message_handler = MessageHandler(Filters.text, textMessage)
photo_message_handler = MessageHandler(Filters.photo, photoMessage)
# Добавляем хендлеры в диспетчер
dispatcher.add_handler(start_command_handler)
dispatcher.add_handler(text_message_handler)
dispatcher.add_handler(photo_message_handler)
# Начинаем поиск обновлений
updater.start_polling(clean=True)
# Останавливаем бота, если были нажаты Ctrl + C
updater.idle()