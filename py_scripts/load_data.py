import sqlite3
import os
import pandas as pd
from datetime import datetime
from py_scripts import utility
import os.path
from pathlib import Path

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
# ------------------------------------------------------------------------------------------------------------------------------------
def init_db (db_filename, db_script_filename):
    with sqlite3.connect(db_filename) as conn: 
        cursor = conn.cursor()
        with open(db_script_filename, 'r', encoding='UTF8') as f:
            db_script = f.read()
            cursor.executescript(db_script)
            conn.commit()

# db_filename = 'database.db'

# функция загрузки данных в таблицу транзакций
def load_transations_file(db_filename, transactions_filename):
    colnames = ['trans_id', 'trans_date', 'amt', 'card_num', 'oper_type', 'oper_result', 'terminal']
    data = pd.read_csv(transactions_filename, names=colnames, header=0, sep =';', dtype={'transaction_id': str})
    with sqlite3.connect(db_filename) as conn:  
        data.to_sql('STG_TRANSACTIONS', conn, if_exists='replace', index=False)
#   if_exists='append' заменить на if_exists='replace' 

# функция загрузки данных в таблицу терминалов
def load_terminals_file(db_filename, terminals_filename):
    colnames = ['terminal_id', 'terminal_type', 'terminal_city', 'terminal_address'] 
    data = pd.read_excel(terminals_filename, names=colnames, header = 0)
    with sqlite3.connect(db_filename) as conn:  
        data.to_sql('STG_TERMINALS', conn, if_exists='replace', index=False)
#   if_exists='append' заменить на if_exists='replace' 

# функция загрузки данных в таблицу чёрных паспартов
def load_black_passport_file(db_filename, terminals_filename):
    colnames = ['entry_dt', 'passport_num'] 
    data = pd.read_excel(terminals_filename, names=colnames, header = 0)
    with sqlite3.connect(db_filename) as conn:  
        data.to_sql('STG_PASSPORT_BLACKLIST', conn, if_exists='replace', index=False)
#   if_exists='append' заменить на if_exists='replace' 

# функция загрузки в базу данных исходные данные
def init_load_data(db_filename):
    print('База данных успешно создана')
    init_db(db_filename, "sql_scripts\init.sql")
    # создаем таблицу с транзакциями считывая файл transations.sql
    init_db(db_filename, r"sql_scripts\transactions.sql")
    # создаем таблицу с транзакциями считывая файл terminals.sql
    init_db(db_filename, r"sql_scripts\terminals.sql")
    # создаем таблицу с транзакциями считывая файл black_pasport.sql
    init_db(db_filename, r"sql_scripts\black_pasport.sql")
    for root, dirs, files in os.walk("./data", topdown=False):
        for name in files:
            print(bcolors.OKBLUE + name+ bcolors.ENDC)
            if name.endswith('.txt'):
                load_transations_file(db_filename, root + '/' + name)
                print(bcolors.OKBLUE, 'Загружен файл с транзациями на текущую дату ', utility.get_date_transactions(), bcolors.ENDC)
                # print('Загружен файл с транзациями на текущую дату ', utility.get_date_transactions())
            elif name.startswith('terminals_'):
                load_terminals_file(db_filename, root + '/' + name)
                print(bcolors.OKBLUE, 'Загружен файл с терминалами на текущую дату ', utility.get_date_terminals(), bcolors.ENDC)
                # print('Загружен файл с терминалами на текущую дату ', utility.get_date_terminals())
            elif name.startswith('passport_blacklist_'):
                load_black_passport_file(db_filename, root + '/' + name)
                print(bcolors.OKBLUE, 'Загружен файл с паспортами в чёрном списке ', utility.get_date_passport_blacklist(), bcolors.ENDC)
                # print('Загружен файл с чёрными пасспортами на текущую дату ', utility.get_date_passport_blacklist())
    
# ? try except сделать для отсутсвия файлов с данными

# инициализация базы данных исходными данными

# создание таблицы витрины данных
def build_showcase():
    print('Витрина данных подготовленна к построению отчёта')
    init_db('database.db', r"sql_scripts\fraud.sql")


# Делаем backup и перемещаем файлы
