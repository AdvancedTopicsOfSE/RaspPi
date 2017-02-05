import sqlite3
from datetime import datetime


def purge_data(cursor):
    del_query = ("delete from attendance\n"
                 "where julianday('now')-julianday(scan_time) > 30\n"
                 "and sync_flg = 1")
    cursor.execute(del_query)

def check_data(cursor, qr_code):
    check_query = ("select count(*) from attendance\n"
                   "where id = ?;")
    count = cursor.execute(check_query, (qr_code,)).fetchone()[0]
    return count

def insert_attendance(cursor, qr_code, present_flg):
    insert_query = ("insert into attendance\n"
                    "      (id, scan_time, present_flg, sync_flg)\n"
                    "VALUES (?, ?, ?, ?);")
    data = (qr_code, str(datetime.now())[0:19], present_flg, 0,)
    cursor.execute(insert_query, data)

def update_presentation(cursor, qr_code):
    update_query = ("update attendance set present_flg = 1, sync_flg = 0\n"
                    "where id = ?;")
    cursor.execute(update_query, (qr_code,))

def save_data_offline(cursor, scan_mode, qr_code):
    if scan_mode == 'Attendance':
        present_flg = 0
    else:
        present_flg = 1
    code_exists = check_data(cursor, qr_code)
    if code_exists == 0:
        insert_attendance(cursor, qr_code, present_flg)
        return 1
    elif present_flg == 1:
        update_presentation(cursor, qr_code)
        return 1
    else:
        return 0

def get_offline_data(cursor):
    get_query = ("select id, scan_time, present_flg\n"
                 "from attendance\n"
                 "where sync_flg = 0;")
    attendance = {'attendance':[]}
    cursor.execute(get_query)
    for (id, scan_time, present_flg) in cursor:
        record = {}
        record['id'] = id
        record['scan_time'] = scan_time
        record['present_flg'] = present_flg
        attendance['attendance'].append(record)
    return attendance

def update_sync_records(cursor):
    update_sync_query = ("update attendance set sync_flg = 1;")
    cursor.execute(update_sync_query)
