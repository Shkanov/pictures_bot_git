# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 14:23:14 2018

@author: Bulat
"""


# -*- coding: utf-8 -*-
# Этот токен невалидный, можете даже не пробовать :)
import telebot


from enum import Enum

token = '497478839:AAFSeEOPFU2PGgBMYm_zSoZz8ez7s6-mWiE'
db_file = "pictures.vdb"



class States(Enum):
    """
    Мы используем БД Vedis, в которой хранимые значения всегда строки,
    поэтому и тут будем использовать тоже строки (str)
    """
    S_START = "0"  # Начало нового диалога
    S_ENTER_NAME = "1"
    S_SEND_PIC = "2"