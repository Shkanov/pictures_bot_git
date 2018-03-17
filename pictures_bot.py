# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 14:20:12 2018

@author: Bulat
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 00:21:32 2017

@author: Bulat
"""


# -*- coding: utf-8 -*-

import telebot
from telebot import types
import pictures_config as config
import dbworker
import numpy as np
#import cv2
import os
#from IPython.display import display, Image
#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg

import requests


bot = telebot.TeleBot(config.token)
path=os.getcwd()

# Начало диалога
s3 = boto3.resource('s3')
bucket = s3.Bucket('ec2-18-218-210-1.us-east-2.compute.amazonaws.com')
    

@bot.message_handler(commands=["start"], content_types=['text'])
def cmd_start(message):
    state = dbworker.get_current_state(message.chat.id)
    if state == config.States.S_ENTER_NAME.value:
        bot.send_message(message.chat.id, "Кажется, кто-то обещал отправить своё имя, но так и не сделал этого :( Жду...")
    elif state == config.States.S_SEND_PIC.value:
        bot.send_message(message.chat.id, "Кажется, кто-то хотел загрузить картинку, но так и не сделал этого :( Жду...")
    else:  # Под "остальным" понимаем состояние "0" - начало диалога
        bot.send_message(message.chat.id, "Привет! Как я могу к тебе обращаться?")
        dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)




# По команде /reset будем сбрасывать состояния, возвращаясь к началу диалога
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Что ж, начнём по-новой. Как тебя зовут?")
    dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_NAME.value)
def user_entering_name(message):
    # В случае с именем не будем ничего проверять, пусть хоть "25671", хоть Евкакий
    bot.send_message(message.chat.id, "Отличное имя, запомню! Загружай картинку!")
    dbworker.set_state(message.chat.id, config.States.S_SEND_PIC.value)



    
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_SEND_PIC.value, content_types=['photo'])
def user_picture(message):
    # В 67случае с именем не будем ничего проверять, пусть хоть "25671", хоть Евкакий
    bot.send_message(message.chat.id, "Загрузил! Давай ещё картинки!")
    print ('user full name =', message.from_user.first_name,message.from_user.last_name)
    user_id=message.from_user.id
   
    #print ('message.photo =', message.photo)
    fileID = message.photo[-1].file_id
    
    print ('fileID =', fileID)
    file = bot.get_file(fileID)
    print ('file.file_path =', file.file_path)
    telegram_api='http://api.telegram.org/file/bot497478839:AAFSeEOPFU2PGgBMYm_zSoZz8ez7s6-mWiE/photos/'
    long_url=os.path.join(telegram_api, file.file_path.rsplit('/',1)[-1])
    print(long_url)
    #image = urllib.URLopener()
    #image.retrieve(long_url,"00000001.jpg")
    with open(file.file_path.rsplit('/', 1)[-1], 'wb') as handle:
        response = requests.get(long_url, stream=True)

        if not response.ok:
            print (response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)




    """img = cv2.imread(long_url,0)
    cv2.imshow('image',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()"""
    
    

    #plt.imshow(mpimg.imread(long_url))
    #display(Image(filename=long_url))
    
    
    
    #cv2.imwrite(os.path.join(path , 'waka.jpg'), message)
    #cv2.waitKey(0)

    dbworker.set_state(message.chat.id, config.States.S_SEND_PIC.value)
"""

@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_KOFE.value)
def user_entering_coffee(message):
    # А вот тут сделаем проверку
    # На данном этапе мы уверены, что message.text можно преобразовать в число, поэтому ничем не рискуем
    if str(message.text) not in ('раф','американо','эспрессо','мокко','латте','Раф','Американо','Эспрессо','Мокко','Латте'):
        bot.send_message(message.chat.id, "Какой-то странный кофе. В нашем меню такого пока нет! Пожалуйста, выбери из списка: раф, латте, эспрессо, мокко, американо")
        return
    else:
        # Возраст введён корректно, можно идти дальше
        bot.send_message(message.chat.id, "Отлично, твой кофе уже готовится! Твой кофе стоит 100 рублей. Твой заказ №"+ str(np.random.randint(1, 10000 + 1)) + "! Ты можешь оплатить наличными либо переводом через Сбербанк Онлайн. Выбери способ оплаты")
        dbworker.set_state(message.chat.id, config.States.S_SET_PAYMENT.value)
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_SET_PAYMENT.value)
       
def user_entering_payment(message):
    # А вот тут сделаем проверку
    # На данном этапе мы уверены, что message.text можно преобразовать в число, поэтому ничем не рискуем
    if str(message.text) not in ('наличными','переводом','наличные','перевод', 'Наличными','Переводом','Наличные','Перевод'):
        bot.send_message(message.chat.id, "Я принимаю платежи пока только либо наличными, либо переводом. Пожалуйста, выбери способ еще раз")
        return
    elif str(message.text) in ('наличными','наличные', 'Наличными','Наличные'):
        bot.send_message(message.chat.id, "Отлично, запомни номер своего заказа! Я тебе напишу, когда кофе будет готов! Если захочешь ещё кофе - отправь команду /kofe.")
        dbworker.set_state(message.chat.id, config.States.S_START.value)

    elif str(message.text) in ('переводом','перевод', 'Переводом','Перевод'):
        bot.send_message(message.chat.id, "Отлично, номер карты для перевода 5555 5555 5555 5555!При оплате переводом ОБЯЗАТЕЛЬНО напиши в комментариях к переводу номер своего заказа! Я тебе напишу, когда кофе будет готов! Если захочешь ещё кофе - отправь команду /kofe.")
        dbworker.set_state(message.chat.id, config.States.S_START.value)


    
"""
"""
# Простейший инлайн-хэндлер для ненулевых запросов
@bot.inline_handler(lambda query: len(query.query) > 0)
def query_text(query):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text="Нажми меня", callback_data="test"))
    results = []
    # Обратите внимание: вместо текста - объект input_message_content c текстом!
    single_msg = types.InlineQueryResultArticle(
        id="1", title="Press me",
        input_message_content=types.InputTextMessageContent(message_text="Я – сообщение из инлайн-режима"),
        reply_markup=kb
    )
    results.append(single_msg)
    bot.answer_inline_query(query.id, results)
"""

if __name__ == '__main__':
    bot.polling(none_stop=True)