import sqlite3
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
# Попытка подбора суммы. В течение 20 минут проходит более 3х операций
# со следующим шаблоном – каждая последующая меньше предыдущей, при этом отклонены все кроме 
# последней. Последняя операция (успешная) в такой цепочке считается мошеннической.
# ----------------------------------------------------------------------------------------
def select_amount_view():
    with sqlite3.connect('database.db') as conn: 
        cursor = conn.cursor()
    cursor.executescript('''
        CREATE VIEW if not EXISTS STG_SEL_AMOUNT as
            SELECT
                card_num,
                trans_date,
                oper_result,
                oper_type,
                LAG(oper_result, 1) over (PARTITION BY card_num ORDER BY trans_date) as result_1,
                LAG(oper_result, 2) over (PARTITION BY card_num ORDER BY trans_date) as result_2,
                LAG(oper_result, 3) over (PARTITION BY card_num ORDER BY trans_date) as result_3,
                LAG(trans_date, 3) over (PARTITION BY card_num ORDER BY trans_date) as date_3
            FROM DWH_FACT_TRANSACTIONS;
    ''')
    conn.commit()

def select_amount_data_view():
    print('Идет поиск мошейнических операций с подбором сумм')
    with sqlite3.connect('database.db') as conn: 
        cursor = conn.cursor()
    cursor.executescript('''
        CREATE VIEW if not EXISTS STG_SEL_AMOUNT_DATA as
            SELECT
                card_num,
                trans_date,
                oper_type,
                oper_result,
                result_1,
                result_2,
                result_3,
                CAST((julianday(trans_date) - julianday(date_3))*24*60 as integer) as different_min
            FROM STG_SEL_AMOUNT
            WHERE oper_result = 'SUCCESS' and result_1='REJECT' 
            and result_2='REJECT' and result_3='REJECT'
            and CAST((julianday(trans_date) - julianday(date_3))*24*60 as integer)<20;
    ''')
    conn.commit()
    # select_amount_data_view()

def select_amount_report_view():
    with sqlite3.connect('database.db') as conn: 
        cursor = conn.cursor()
    cursor.executescript('''
        CREATE VIEW if not EXISTS STG_SET_AMOUNT_REPORT_ACC as
            SELECT
                t1.trans_date as event_dt,
                t4.passport_num as passport,
                t4.last_name||' '||t4.first_name||' '||t4.patronymic as fio,
                t4.phone
            FROM STG_SEL_AMOUNT_DATA t1
            LEFT JOIN DWH_DIM_CARDS t2
            on t1.card_num=t2.card_num
            LEFT JOIN DWH_DIM_ACCOUNTS t3
            on t2.account_num=t3.account_num
            LEFT JOIN DWH_DIM_CLIENTS t4
            on t3.client=t4.client_id;
    ''')
    conn.commit()

def rep_fraud_select_amount_():
    print('Построение отчета витрины данных по операциям с подбором сумм')
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
        ) SELECT
            event_dt,
            passport,
            fio,
            phone,
            'Подбор суммы',
            datetime('now')
        FROM STG_SET_AMOUNT_REPORT_ACC;
    ''')
    conn.commit()

# rep_fraud_select_amount_()


# *********************************************************************************************************
# Очистка временных таблиц по подбору сумм
# *********************************************************************************************************

def delet_select_amount_():
    with sqlite3.connect('database.db') as conn: 
        cursor = conn.cursor()
    cursor.executescript('''
        DROP VIEW if exists STG_SEL_AMOUNT;
        DROP VIEW if exists STG_SEL_AMOUNT_DATA;
        DROP VIEW if exists STG_SET_AMOUNT_REPORT_ACC;
    ''')
    conn.commit()

def amount():
    select_amount_view()
    select_amount_data_view()
    select_amount_report_view()
    print(bcolors.OKBLUE + 'ПОСТРОЕНИЕ ОТЧЁТА ВИТРИНЫ ДАННЫХ ПО ОПЕРАЦИЯМ С ПОПЫТКОЙ ПОДБОРА СУММ'+ bcolors.ENDC)
    rep_fraud_select_amount_()
    delet_select_amount_()

