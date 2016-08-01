import datetime
import pymssql

server = '192.168.217.29:1433'
user = 'pi'
password = '123456'
database = 'owen_trm'


# table si8_value
def insert(id_si8, regName, value, now_date=datetime.datetime.now()):
    conn = pymssql.connect(server=server, user=user, password=password, database=database)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO si8_value (id_si8, regName, value, Date) VALUES ( %d, %s, %d, %s)",
                   (id_si8, regName, value, now_date))
    conn.commit()
    conn.close()


# table si8_log
def insert_log(title, message, now_date=datetime.datetime.now()):
    conn = pymssql.connect(server=server, user=user, password=password, database=database)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO si8_log (title, message, Date) VALUES ( %s, %s, %s)", (title, message, now_date))
    conn.commit()
    conn.close()


# table si8_device
def select_device():
    conn = pymssql.connect(server=server, user=user, password=password, database=database)
    cursor = conn.cursor()
    cursor.execute("SELECT id, addr, addLen, regName FROM si8_device WHERE (enable = 1)")
    sqlrow = cursor.fetchone()
    rows = []
    while sqlrow:
        # print("id=%d, addr=%d, addrLen=%d, regName=%s" % (row[0], row[1],row[2], row[3]))
        # sqlrow[3]='DCNT;DSTR'
        for regName in sqlrow[3].split(';'):
            lrow = (sqlrow[0], sqlrow[1], sqlrow[2], str(regName))
            rows.append(lrow)
            # print(lrow)
        sqlrow = cursor.fetchone()
    conn.close()
    # print (len(rows))
    # print('end')
    return rows


def main():
    # insert(1, 'DSPD', 12)
    # regName_to_list()
    select_device()
    # insert_log('ERR','10 in 152')
    # for row in rows:
    # print("id=%d, addr=%d, addrLen=%d, regName=%s" % (row[0], row[1],row[2], row[3]))


if __name__ == '__main__':
    main()
