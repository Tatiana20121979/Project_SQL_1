
import os
import datetime
from datetime import datetime
import shutil
from pathlib import Path
import os.path
import sqlite3
# -------------------------------------------------------------------------------------------
# УТИЛИТА ВЫВОДА НА ЭКРАН ДАННЫХ
# --------------------------------------------------------------------------------------------
def show_data(table_name):
    print('_-'*40)
    print(table_name)
    print('_-'*40)
    with sqlite3.connect('database.db') as conn: 
        cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table_name}')
    for row in cursor.fetchall():
        print(row)
    print('_-'*40)

# --------------------------------------------------------------------------------------------
# ФУНКЦИЯ BACKUP
# --------------------------------------------------------------------------------------------
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def make_dir_archive():
    if not os.path.isdir('archive'):
        os.makedirs('archive')
    
def move_to_archive():
    for root, dirs, files in os.walk("./data", topdown=False):
        for name in files:
            if name.endswith('.txt'):
                shutil.move((root + '/' + name), 'archive')
            elif name.startswith('terminals_'):
                shutil.move((root + '/' + name), 'archive')
            elif name.startswith('passport_blacklist_'):
                shutil.move((root + '/' + name), 'archive')

# shutil.move - перемещает
# shutil.copy - копирует

def rename_backup_file():
    for root, dirs, files in os.walk("./archive", topdown=False):
        for name in files:
            if name.endswith('.txt'):
                filename = Path(root + '/' + name)
                filename_new = filename.with_suffix(".backup")
                filename.rename(filename_new)
                print(bcolors.OKGREEN + 'Файл ' + name +' переименован и добавлен в архив'+ bcolors.ENDC)              
            elif name.startswith('terminals_'):
                filename2 = Path(root + '/' + name)
                filename_news = filename2.with_suffix(".xlsx.backup")
                filename2.rename(filename_news)
                print(bcolors.OKGREEN + 'Файл ' + name +' переименован и добавлен в архив'+ bcolors.ENDC)  
            elif name.startswith('passport_blacklist_'):
                filename2 = Path(root + '/' + name)
                filename_news = filename2.with_suffix(".xlsx.backup")
                filename2.rename(filename_news)
                print(bcolors.OKGREEN + 'Файл ' + name +' переименован и добавлен в архив'+ bcolors.ENDC)  



def backup_rename_file():
    move_to_archive()
    rename_backup_file()
# --------------------------------------------------------------------------------------------
# ФУНКЦИИ ИЗВЛЕЧЕНИЯ ДАТЫ ИЗ НАЗВАНИЯ ФАЙЛА
# --------------------------------------------------------------------------------------------
# Функция извлечения даты из названия файла для транзакций 
def get_date_transactions():
    lst = os.listdir('./data')
    for fname in lst:
        if fname.startswith('transactions'):
            date = datetime.strptime((fname.split("_",1)[1].split(".",1)[0]),"%d%m%Y")
            # метод .date() от переменной data возвращает формат только даты без времени
            return date.date()
# Функция извлечения даты из названия файла для черных паспортов 
def get_date_passport_blacklist():
    lst = os.listdir('./data')
    for fname in lst:
        if fname.startswith('passport_blacklist'):
            date = datetime.strptime((fname.split("st_",1)[1].split(".",1)[0]), "%d%m%Y")
            # метод .date() от переменной data возвращает формат только даты без времени
            return date.date()
# Функция извлечения даты из названия файла для терминалов 
def get_date_terminals():
    lst = os.listdir('./data')
    for fname in lst:
        if fname.startswith('terminals'):
            date = datetime.strptime((fname.split("_",1)[1].split(".",1)[0]), "%d%m%Y")
            # метод .date() от переменной data возвращает формат только даты без времени
            return date.date()

# --------------------------------------------------------------------------------------------
# ФУНКЦИИ ИЗВЛЕЧЕНИЯ ДАТЫ ИЗ НАЗВАНИЯ ФАЙЛА
# --------------------------------------------------------------------------------------------
# Функция извлечения даты из названия файла для транзакций 
def get_date_transactions_1():
    lst = os.listdir('./data')
    for fname in lst:
        if fname.startswith('transactions'):
            date = datetime.strptime((fname.split("_",1)[1].split(".",1)[0]),"%d%m%Y")
            # метод .date() от переменной data возвращает формат только даты без времени
            # return date.date()
# Функция извлечения даты из названия файла для черных паспортов 
def get_date_passport_blacklist_1():
    lst = os.listdir('./data')
    for fname in lst:
        if fname.startswith('passport_blacklist'):
            date = datetime.strptime((fname.split("st_",1)[1].split(".",1)[0]), "%d%m%Y")
            # метод .date() от переменной data возвращает формат только даты без времени
            # return date.date()
# Функция извлечения даты из названия файла для терминалов 
def get_date_terminals_1():
    lst = os.listdir('./data')
    for fname in lst:
        if fname.startswith('terminals'):
            date = datetime.strptime((fname.split("_",1)[1].split(".",1)[0]), "%d%m%Y")
            # метод .date() от переменной data возвращает формат только даты без времени
            # return date.date()
# --------------------------------------------------------------------------------------------
