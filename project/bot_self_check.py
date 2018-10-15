import apiai, json
import photo_proc

txt_request = apiai.ApiAI('733a0aad1eb0479c88c862e1ec1a26e7').text_request() # Токен API к Dialogflow
txt_request.lang = 'ru' # На каком языке будет послан запрос
txt_request.session_id = 'Comparator3000' # ID Сессии диалога (нужно, чтобы потом учить бота)
txt_request.query = 'Ты здесь?' # Посылаем запрос к ИИ с сообщением от юзера
txt_responseJson = json.loads(txt_request.getresponse().read().decode('utf-8'))
txt_response = txt_responseJson['result']['fulfillment']['speech'] # Разбираем JSON и вытаскиваем ответ
# Если есть ответ от бота - присылаем юзеру, если нет - бот его не понял
print ('Проверяем работает ли бот; Спросим: Ты здесь?')
if txt_response:
    print('Бот готов; его ответ: ' + txt_response)
else:
   print('Подключение отсутствует, бот не отвечает')
   
photo_request = '/test_photo.jpg'
try:
	photo_response = photo_proc.class_detector(photo_request)
	print('Обработка фото функционирует нормально')
except:
	print('Что-то пошло не так при обработке фотографии')