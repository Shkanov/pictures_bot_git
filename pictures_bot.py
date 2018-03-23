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
import boto
import boto.s3.connection
from boto.s3.key import Key
import numpy as np
#import cv2
import os
import pandas as pd
import pymysql
#from IPython.display import display, Image
#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg

import requests
import boto3
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from logging import Logger






bot = telebot.TeleBot(config.token)
path=os.getcwd()

# Начало диалога

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
    user_name=message.from_user.first_name+message.from_user.last_name
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
#DOWLOADING THE FILE INTO CURRENT DIRECTORY
    with open(file.file_path.rsplit('/', 1)[-1], 'wb') as handle:
        response = requests.get(long_url, stream=True)





        if not response.ok:
            print (response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)
#OR DOWNLOADING FILE DIRECTLY TO S3 WITHOUT SAVING ON DISK

    # Uses the creds in ~/.aws/credentials
    s3 = boto3.resource('s3',
                        aws_access_key_id='AKIAJNHVITVJFCOAZ4MA',
                        aws_secret_access_key='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')
    bucket_name_to_upload_image_to = 'ec2-18-218-210-1.us-east-2.compute.amazonaws.com'
    s3_image_filename = file.file_path.rsplit('/',1)[-1]

    # Do this as a quick and easy check to make sure your S3 access is OK
    for bucket in s3.buckets.all():
        if bucket.name == bucket_name_to_upload_image_to:
            print('Good to go. Found the bucket to upload the image into.')
            good_to_go = True

    if not good_to_go:
        print('Not seeing your s3 bucket, might want to double check permissions in IAM')

    # Given an Internet-accessible URL, download the image and upload it to S3,
    # without needing to persist the image to disk locally
    req_for_image = requests.get(long_url, stream=True)
    file_object_from_req = req_for_image.raw
    req_data = file_object_from_req.read()

    # Do the actual upload to s3
    s3.Bucket(bucket_name_to_upload_image_to).put_object(Key=s3_image_filename, Body=req_data)


#UPLOADING THE FILE FROM DISK TO S3

    """s3 = boto3.resource('s3',
                        aws_access_key_id='AKIAJNHVITVJFCOAZ4MA',
                        aws_secret_access_key='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',
                        )
    BUCKET = "ec2-18-218-210-1.us-east-2.compute.amazonaws.com"
    print(os.path.join(os.getcwd(), 'file_49.jpg'))
    s3.Bucket(BUCKET).upload_file(os.path.join(os.getcwd(), 'file_49.jpg'), "1.jpg")"""
#WRITING INFO INTO SQL TABLE
    host = "picturesbot.c6bnfewxkhhw.us-east-1.rds.amazonaws.com"
    port = 3306
    dbname = "picturesbot"
    user = "shkanov"
    password = "Steel2033102"
    conn = pymysql.connect(host, user=user, port=port,
                           passwd=password, db=dbname, autocommit=True)
    cur=conn.cursor()
    #cur.execute('drop table pictures_bot_info;')
    #cur.execute('create table pictures_bot_info '
    #            '(filename VARCHAR(100), '
    #            'username VARCHAR(100));')
    add_data = ("INSERT INTO {table} "
                "(filename, username) "
                "VALUES (%s, %s)")
    atable = 'pictures_bot_info'
    data_word = (file.file_path.rsplit('/',1)[-1], user_name)
    cur.execute(add_data.format(table=atable), data_word)


    print(pd.read_sql('select * from pictures_bot_info;', con=conn))

#WRITING TO GOOGLE SPREADSHEETS
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client-server.json', scope)
    client = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("pictures_bot").sheet1

    index = 1
    # Extract and print all of the values
    index+=1

    row = [file.file_path.rsplit('/',1)[-1],  user_name]

    sheet.insert_row(row, index)
    list_of_hashes = sheet.get_all_records()
    print(list_of_hashes)
    print(sheet.row_count)
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
    try:

        bot.polling(none_stop=True)

        # ConnectionError and ReadTimeout because of possible timout of the requests library

        # TypeError for moviepy errors

        # maybe there are others, therefore Exception

    except Exception as e:

        print(e)

        time.sleep(30)