import pandas as pd
from py_scripts import utility


# ------------------------------------------------------------------------------------------------------------------------------------
def init_db(conn, db_script_filename):
    cursor = conn.cursor()
    with open(db_script_filename, 'r', encoding='UTF8') as f:
        db_script = f.read()
        cursor.executescript(db_script)
        conn.commit()


# функция загрузки данных в таблицу транзакций
def load_transations_file(conn, transactions_filename):
    colnames = ['trans_id', 'trans_date', 'amt', 'card_num', 'oper_type', 'oper_result', 'terminal']
    data = pd.read_csv(transactions_filename, names=colnames, header=0, sep=';', dtype={'transaction_id': str})
    data.to_sql('STG_TRANSACTIONS', conn, if_exists='replace', index=False)
#   if_exists='append' заменить на if_exists='replace'


# функция загрузки данных в таблицу терминалов
def load_terminals_file(conn, terminals_filename):
    colnames = ['terminal_id', 'terminal_type', 'terminal_city', 'terminal_address']
    data = pd.read_excel(terminals_filename, names=colnames, header=0)
    data.to_sql('STG_TERMINALS', conn, if_exists='replace', index=False)
#   if_exists='append' заменить на if_exists='replace'


# функция загрузки данных в таблицу чёрных паспартов
def load_black_passport_file(conn, terminals_filename):
    colnames = ['entry_dt', 'passport_num']
    data = pd.read_excel(terminals_filename, names=colnames, header=0)
    data.to_sql('STG_PASSPORT_BLACKLIST', conn, if_exists='replace', index=False)
#   if_exists='append' заменить на if_exists='replace'


# функция загрузки в базу данных исходные данные
def init_load_data(conn):
    print('База данных успешно создана')
    init_db(conn, "sql_scripts/init.sql")
    # создаем таблицу с транзакциями считывая файл transations.sql
    init_db(conn, "sql_scripts/transactions.sql")
    # создаем таблицу с транзакциями считывая файл terminals.sql
    init_db(conn, "sql_scripts/terminals.sql")
    # создаем таблицу с транзакциями считывая файл black_pasport.sql
    init_db(conn, "sql_scripts/black_pasport.sql")


# ? try except сделать для отсутсвия файлов с данными
# инициализация базы данных исходными данными
def load_operational_data(conn, date_slice):
    print(utility.bcolors.OKBLUE + date_slice + utility.bcolors.ENDC)
    load_transations_file(conn, "./data/transactions_%s.txt" % date_slice)
    print(utility.bcolors.OKBLUE, 'Загружен файл с транзациями на текущую дату ', date_slice, utility.bcolors.ENDC)
    # print('Загружен файл с транзациями на текущую дату ', utility.get_date_transactions())
    load_terminals_file(conn, "./data/terminals_%s.xlsx" % date_slice)
    print(utility.bcolors.OKBLUE, 'Загружен файл с терминалами на текущую дату ', date_slice, utility.bcolors.ENDC)
    # print('Загружен файл с терминалами на текущую дату ', utility.get_date_terminals())
    load_black_passport_file(conn, "./data/passport_blacklist_%s.xlsx" % date_slice)
    print(utility.bcolors.OKBLUE, 'Загружен файл с паспортами в чёрном списке ', date_slice, utility.bcolors.ENDC)
    # print('Загружен файл с чёрными пасспортами на текущую дату ', utility.get_date_passport_blacklist())


# создание таблицы витрины данных
def build_showcase(conn):
    print('Витрина данных подготовленна к построению отчёта')
    init_db(conn, "sql_scripts/fraud.sql")
