# ----------------------------------------------------------------------------------------------------
# СОЗДАЕМ ТАБЛИЦУ ФАКТОВ ТРАНЗАКЦИЙ (ДЛЯ ЗАГРУЗКИ НАКОПИТЕЛЬНЫМ ИТОГОМ ИЗ ТАБЛИЦЫ STG_TRANSACTIONS)
# ----------------------------------------------------------------------------------------------------
def create_transactions_fact_table(conn):
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE if not exists DWH_FACT_TRANSACTIONS(
            trans_id varchar(128),
            trans_date date,
            amt decimal(10,2),
            card_num varchar(128),
            oper_type varchar(128),
            oper_result varchar(128),
            terminal varchar(128),
            foreign key (card_num) references DWH_DIM_CARDS (card_num),
            foreign key (terminal) references DWH_DIM_TERMINALS_HIST (terminal_id)
        );
    ''')
    conn.commit()


# создаем функцию выгрузки данных по транзакциям из временной таблицы (за день) STG_TRANSACTIONS
# в таблицу фактов DWH_FACT_TRANSACTIONS
def transactions_to_fact(conn):
    cursor = conn.cursor()
    cursor.executescript('''
        INSERT INTO DWH_FACT_TRANSACTIONS(
            trans_id,
            trans_date,
            amt,
            card_num,
            oper_type,
            oper_result,
            terminal
        )
        SELECT
            trans_id,
            trans_date,
            amt,
            card_num,
            oper_type,
            oper_result,
            terminal
        FROM STG_TRANSACTIONS;
    ''')
    cursor.execute('''
        DROP TABLE if exists STG_TRANSACTIONS;
    ''')
    conn.commit()


# СОЗДАЕМ ТАБЛИЦУ ФАКТОВ ЧЕРНЫХ ПАССПОРТОВ (ДЛЯ ЗАГРУЗКИ НАКОПИТЕЛЬНЫМ ИТОГОМ ИЗ ТАБЛИЦЫ STG_PASSPORT_BLACKLIST)
def create_black_pasport_fact_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE if not exists DWH_FACT_PASSPORT_BLACKLIST(
            entry_dt timestamp,
            passport_num varchar(128)
        );
    ''')
    conn.commit()


# создаем функцию выгрузки данных по транзакциям из временной таблицы (за день) STG_PASSPORT_BLACKLIST
# в таблицу фактов DWH_FACT_PASSPORT_BLACKLIST
def black_pasport_to_fact(conn):
    cursor = conn.cursor()
    cursor.executescript('''
        INSERT INTO DWH_FACT_PASSPORT_BLACKLIST(
            entry_dt,
            passport_num
        )
        SELECT
            entry_dt,
            passport_num
        FROM STG_PASSPORT_BLACKLIST;
    ''')
    cursor.execute('''
         DROP TABLE if exists STG_PASSPORT_BLACKLIST;
    ''')
    conn.commit()


# Функция создания и заполнения фактических таблиц и очистки временных STG
def create_fact_table(conn):
    create_transactions_fact_table(conn)
    transactions_to_fact(conn)
    create_black_pasport_fact_table(conn)
    black_pasport_to_fact(conn)
