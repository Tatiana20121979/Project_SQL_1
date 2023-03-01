import sqlite3
from py_scripts import utility
from py_scripts import load_data
from py_scripts import fact_table
from py_scripts import fraud_passport
from py_scripts import select_amount


def run_application(db_filename):
    # создаем директорию для архива
    utility.make_dir_archive()
    with sqlite3.connect(db_filename) as conn:
        # создание всех таблиц
        load_data.init_load_data(conn)

        # создание таблицы витрины данных
        load_data.build_showcase(conn)
        for date_slice in utility.read_date_slice('./data'):
            # создаем загрузку базы данных из файлов
            load_data.load_operational_data(conn, date_slice)
            # Делаем backup и перемещаем файлы
            utility.backup_rename_file(date_slice)
            # Создаем и заполняем таблицу фактов
            # DWH_FACT_TRANSACTIONS и DWH_FACT_PASSPORT_BLACKLIST
            fact_table.create_fact_table(conn)
            # Создаем заполняем и отлавливаем клиентов
            # с чёрными паспортами, вносим данные в витрину
            fraud_passport.fraud_black_passpory(conn)
            # Создаем заполняем и отлавливаем клиентов
            # с недействительными паспортами, вносим данные в витрину
            fraud_passport.fraud_over_passpory(conn)
            # Создаем заполняем и отлавливаем клиентов с попыткой подбора суммы
            select_amount.amount(conn)
        # Вывод в терминал витрины данных
        utility.show_data(db_filename, 'REP_FRAUD')


run_application('database.db')
