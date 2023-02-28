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
# СОВЕРШЕНИЕ ОПЕРАЦИЙ ПРИ НЕДЕЙСТВУЮЩЕМ ДОГОВОРЕ
# ----------------------------------------------------------------------------------------
def contract_not_valid():
    with sqlite3.connect('database.db') as conn: 
        cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE if not exists STG_CONTRACT_ACCOUNT_NOT_VALID as
	        SELECT
                t1.account_num,
                t1.valid_to,
                t2.passport_num, 
                t2.phone,
                t2.last_name || ' ' || t2.first_name || ' ' || t2.patronymic as fio	
            FROM DWH_DIM_ACCOUNTS t1
            LEFT JOIN DWH_DIM_CLIENTS t2 
            on t1.client = t2.client_id;
    ''')
    conn.commit()


def contract_cards_not_valid():
    with sqlite3.connect('database.db') as conn: 
        cursor = conn.cursor()
    cursor.execute('''
        CREATE VIEW if not EXISTS STG_CONTRACT_CARDS_NOT_VALID as
            SELECT
                t1. card_num,
                t2.account_num,
                t2.valid_to,
                t2.passport_num,
                t2. phone,
                t2.fio
            FROM DWH_DIM_CARDS t1
            LEFT JOIN STG_CONTRACT_ACCOUNT_NOT_VALID t2
            on t1. account_num=t2.account_num;
    ''')
    conn.commit()


def contract_fraud_view():
    with sqlite3.connect('database.db') as conn: 
        cursor = conn.cursor()
    cursor.execute('''
        CREATE VIEW if not EXISTS STG_CONTRACT_TRANSACTIONS_FRAUD as
            SELECT
                t1.trans_date as event_dt,
                t2.card_num,
                t2.valid_to,
                t2.passport_num as passport,
                t2.phone,
                t2.fio
            FROM DWH_FACT_TRANSACTIONS t1
            LEFT JOIN STG_CONTRACT_CARDS_NOT_VALID t2
            on t1.card_num=t2.card_num
            WHERE t1.trans_date>t2.valid_to;
    ''')


def rep_fraud_contract():
    with sqlite3.connect('database.db') as conn: 
        cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO REP_FRAUD (
            event_dt,
            passport,
            fio,
            phone,
            event_type,
            report_dt
        ) SELECT
            event_dt,
            passport,
            fio,
            phone,
            'Недействующий договор',
            datetime('now')
    FROM STG_CONTRACT_TRANSACTIONS_FRAUD
    WHERE (event_dt, passport) in (
        SELECT
            MIN(event_dt),
            passport
        FROM STG_CONTRACT_TRANSACTIONS_FRAUD
        GROUP BY passport
);
    ''')
    conn.commit()

def delete_stg_fraud_account():
    with sqlite3.connect('database.db') as conn: 
        cursor = conn.cursor()
    cursor.executescript('''
        DROP TABLE if exists STG_CONTRACT_ACCOUNT_NOT_VALID;
        DROP VIEW if exists STG_CONTRACT_CARDS_NOT_VALID;
        DROP VIEW if exists STG_CONTRACT_TRANSACTIONS_FRAUD;
    ''')
    conn.commit()



def fraud_account():
    contract_not_valid()
    contract_cards_not_valid()
    contract_fraud_view()
    # print(bcolors.OKCYAN + 'Поиск операций с не действующими договорами'+ bcolors.ENDC)
    # utility.show_data('STG_CONTRACT_TRANSACTIONS_FRAUD')
    print(bcolors.OKBLUE + 'ПОСТРОЕНИЕ ОТЧЁТА ВИТРИНЫ ДАННЫХ ПО ОПЕРАЦИЯМ С НЕ ДЕЙСТВУЮЩИМИ ДОГОВОРАМИ'+ bcolors.ENDC)
    rep_fraud_contract()
    # utility.show_data('STG_CONTRACT_TRANSACTIONS_FRAUD')
    delete_stg_fraud_account()