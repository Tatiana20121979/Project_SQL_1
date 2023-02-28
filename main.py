import sqlite3
import os
import pandas as pd
import re
from datetime import datetime
import sys 
from py_scripts import utility, load_data, fact_table, fraud_passport, select_amount
import shutil
from pathlib import Path


def run_application():
    # создаем директорию для архива
    utility.make_dir_archive()
    # создаем загрузку базы данных из файлов
    load_data.init_load_data('database.db')
    # создание таблицы витрины данных
    load_data.build_showcase()
    # Делаем backup и перемещаем файлы
    utility.backup_rename_file()
    # Создаем и заполняем таблицу фактов DWH_FACT_TRANSACTIONS и DWH_FACT_PASSPORT_BLACKLIST
    fact_table.create_fact_table()
    # Создаем заполняем и отлавливаем клиентов с чёрными паспортами, вносим данные в витрину
    fraud_passport.fraud_black_passpory()
    # Создаем заполняем и отлавливаем клиентов с недействительными паспортами, вносим данные в витрину
    fraud_passport.fraud_over_passpory()
    # Создаем заполняем и отлавливаем клиентов с попыткой подбора суммы
    select_amount.amount()
    # Вывод в терминал витрины данных
    utility.show_data('REP_FRAUD')


run_application()
