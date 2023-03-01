import sqlite3
from py_scripts import utility
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
# ----------------------------------------------------------------------------------------
# Отлов мошейнических операций с паспортами
# ----------------------------------------------------------------------------------------
# создаем таблицу с данными не действующих клиентов

def not_valid_passport_clients():
    with sqlite3.connect('database.db') as conn: 
        cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE if not exists STG_CLIENT_NOT_VALID (
            client_id varchar(128),
            passport_num varchar(128),
            fio varchar(364),
            phone varchar(128),
            passport_valid_to date
        )
    ''')
    conn.commit()


def data_for_not_valid_passport():
    with sqlite3.connect('database.db') as conn: 
        cursor = conn.cursor()
    cursor.executescript('''
        INSERT INTO STG_CLIENT_NOT_VALID(
            client_id,
            passport_num,
            fio,
            phone,
            passport_valid_to
        ) 
        SELECT 
            client_id, 
            passport_num,
            last_name || ' ' || first_name || ' ' || patronymic as fio,
            phone,
            passport_valid_to
            FROM DWH_DIM_CLIENTS
            WHERE ? > passport_valid_to or passport_num in (
                SELECT 
                    passport_num 
                FROM DWH_FACT_PASSPORT_BLACKLIST
                );
    ''')
    conn.commit()


# Создаем представление которое покажет аккаунты по чёрным паспортам
def view_accounts_passport():
    with sqlite3.connect('database.db') as conn: 
        cursor = conn.cursor()
    cursor.executescript('''
        CREATE VIEW if not EXISTS STG_ACCOUNTS_NOT_VALID as
            SELECT
                t1.account_num,
                t2.passport_num,
                t2. fio,
                t2. phone
            FROM DWH_DIM_ACCOUNTS t1
            INNER JOIN STG_CLIENT_NOT_VALID t2
            on t1.client = t2.client_id;
    ''')
    conn.commit()

# создаем представление что бы увидеть номера карт по чёрным паспортам

def cards_passport():
    with sqlite3.connect('database.db') as conn: 
            cursor = conn.cursor()
    cursor.executescript('''
        CREATE VIEW if not EXISTS STG_CARDS_NOT_VALID as
            SELECT
                t1.card_num,
                t2.account_num,
                t2.passport_num,
                t2. fio,
                t2. phone
            FROM DWH_DIM_CARDS t1
            INNER JOIN STG_ACCOUNTS_NOT_VALID t2
            on t1.account_num = t2.account_num;
    ''')
    conn.commit()


# создаем представление что бы увидеть транзакции совершенные по паспортам в черном списке
def passport_fraud():
    with sqlite3.connect('database.db') as conn: 
            cursor = conn.cursor()
    cursor.executescript('''
        CREATE VIEW if not EXISTS STG_PASSPORT_FRAUD as
            SELECT
                t2. fio,
                t2. passport_num as passport,
                t2. phone,
                t1.trans_date as event_dt
            FROM DWH_FACT_TRANSACTIONS t1
            INNER JOIN STG_CARDS_NOT_VALID t2
            on t1.card_num = t2.card_num;
    ''')
    conn.commit()


def rep_fraud_passport():
    with sqlite3.connect('database.db') as conn: 
            cursor = conn.cursor()
    cursor.executescript('''
        INSERT INTO REP_FRAUD (
            event_dt,
            passport,
            fio,
            phone,
            event_type,
            report_dt
        )SELECT
            event_dt,
            passport,
            fio,
            phone,
            'Паспорт в чёрном списке',
            datetime('now')
        FROM STG_PASSPORT_FRAUD
        WHERE (event_dt, passport) in (
            SELECT
                MIN(event_dt),
                passport
            FROM STG_PASSPORT_FRAUD
            GROUP BY passport
        );
    ''')
    conn.commit()

# функция удаления данных из временных таблиц
def delete_stg_black_passport():
    with sqlite3.connect('database.db') as conn: 
        cursor = conn.cursor()
    cursor.executescript('''
        DROP TABLE if exists STG_CLIENT_NOT_VALID;
        DROP VIEW if exists STG_ACCOUNTS_NOT_VALID;
        DROP VIEW if exists STG_CARDS_NOT_VALID;
        DROP VIEW if exists STG_PASSPORT_FRAUD;
    ''')
    conn.commit()


def fraud_black_passpory():
    not_valid_passport_clients()
    data_for_not_valid_passport()
    view_accounts_passport()
    cards_passport()
    passport_fraud()
    print(bcolors.OKBLUE + 'Поиск операций с паспортами черном списке'+ bcolors.ENDC)
    # utility.show_data('STG_PASSPORT_FRAUD')
    print(bcolors.OKBLUE + 'ПОСТРОЕНИЕ ОТЧЁТА ВИТРИНЫ ДАННЫХ ПО ОПЕРАЦИЯМ С ПАСПОРТАМИ В ЧЁРНОМ СПИСКЕ'+ bcolors.ENDC)
    # utility.show_data('REP_FRAUD')
    rep_fraud_passport()
    delete_stg_black_passport()


# ----------------------------------------------------------------------------------------------------------
# ОТЛОВ НЕДЕЙСТВИТЕЛЬНЫХ ПАССПОРТОВ
# ----------------------------------------------------------------------------------------------------------
def over_passport_table():
    with sqlite3.connect('database.db') as conn: 
            cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS STG_OVER_PASSPORT as
            SELECT
                client_id,
                last_name||' '||first_name||' '||patronymic as fio,
                passport_num,
                phone,
                passport_valid_to	
            FROM DWH_DIM_CLIENTS
            WHERE passport_valid_to is not null and passport_num not in (
                SELECT 
                    passport_num
                FROM DWH_FACT_PASSPORT_BLACKLIST);
    ''')
    conn.commit()


def over_passport_account_view():
    with sqlite3.connect('database.db') as conn: 
            cursor = conn.cursor()
    cursor.executescript('''
        CREATE VIEW if not EXISTS STG_OVER_ACCOUNTS as
            SELECT
                t1.account_num,
                t2.fio,
                t2.passport_num,
                t2.phone,
                t2.passport_valid_to
            FROM DWH_DIM_ACCOUNTS t1
            INNER JOIN STG_OVER_PASSPORT t2
            on t1.client=t2.client_id;
	''')
    conn.commit()



def over_passport_cards_view():
    with sqlite3.connect('database.db') as conn: 
            cursor = conn.cursor()
    cursor.executescript('''
        CREATE VIEW if not EXISTS STG_OVER_CARDS as
            SELECT
                t1.card_num,
                t2.fio,
                t2.account_num,
                t2.passport_num,
                t2.phone,
                t2.passport_valid_to
            FROM DWH_DIM_CARDS t1
            INNER JOIN STG_OVER_ACCOUNTS t2
            on t1.account_num=t2.account_num;
    ''')
    conn.commit()

def over_passport_fraud_view():
    with sqlite3.connect('database.db') as conn: 
            cursor = conn.cursor()
    cursor.executescript('''
        CREATE VIEW if not EXISTS STG_OVER_PASSPORT_FRAUD as
            SELECT
                t1.trans_date as event_dt,
                t2.fio,
                t2.card_num,
                t2.account_num,
                t2.passport_num as passport,
                t2.phone,
                t2.passport_valid_to
            FROM DWH_FACT_TRANSACTIONS t1
            INNER JOIN STG_OVER_CARDS t2
            on t1.card_num=t2.card_num
            WHERE t1.trans_date>t2.passport_valid_to;
    ''')
    conn.commit()



def rep_fraud_over_passport():
    with sqlite3.connect('database.db') as conn: 
            cursor = conn.cursor()
    cursor.executescript('''
        INSERT INTO REP_FRAUD (
            event_dt,
            passport,
            fio,
            phone,
            event_type,
            report_dt
        )SELECT
            event_dt,
            passport,
            fio,
            phone,
            'Паспорт просрочен',
            datetime('now')
        FROM STG_OVER_PASSPORT_FRAUD
        WHERE (event_dt, passport) in (
            SELECT
                MIN(event_dt),
                passport
            FROM STG_OVER_PASSPORT_FRAUD
            GROUP BY passport
        );
    ''')
    conn.commit()

# функция удаления данных из временных таблиц с недействительным пасспортом
def delete_stg_over_passport():
    with sqlite3.connect('database.db') as conn: 
        cursor = conn.cursor()
    cursor.executescript('''
        DROP TABLE if exists STG_OVER_PASSPORT;
        DROP VIEW if exists STG_OVER_ACCOUNTS;
        DROP VIEW if exists STG_OVER_CARDS;
        DROP VIEW if exists STG_OVER_PASSPORT_FRAUD;
    ''')
    conn.commit()


def fraud_over_passpory():
    over_passport_table()
    over_passport_account_view()
    over_passport_cards_view()
    over_passport_fraud_view()
    print(bcolors.OKBLUE + 'Поиск операций с просроченными паспортами'+ bcolors.ENDC)
    # print('Поиск операций с просроченными паспортами')
    # utility.show_data('STG_OVER_PASSPORT_FRAUD')
    print(bcolors.OKBLUE + 'ПОСТРОЕНИЕ ОТЧЁТА ВИТРИНЫ ДАННЫХ ПО ОПЕРАЦИЯМ С ПРОСРОЧЕННЫМИ ПАСПОРТАМИ'+ bcolors.ENDC)
    # utility.show_data('REP_FRAUD')
    rep_fraud_over_passport()
    delete_stg_over_passport()



