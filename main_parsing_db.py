r"""
01-08-16 v 0.1
Скрипт по выделению данных из файлов архива шестиреки и передачи в дазу данных MS SQL
Проверялся на python3.5.1
"""

import struct
import os
# import mssql
import datetime

foldeder = 'data/'


def main():
    for f in os.listdir(path=foldeder):
        if f.endswith('.SI8'):
            openfile(f)


def openfile(filename):
    # foldeder = 'data/'
    # filename = '310716.SI8'
    with open(foldeder + filename, "rb") as f:
        count_si8 = 1
        while count_si8:
            count_si8 = int.from_bytes(f.read(1), byteorder='big')
            hour = int.from_bytes(f.read(1), byteorder='big')
            minute = int.from_bytes(f.read(1), byteorder='big')
            print("Счетчиков = %d, Время %d:%d" % (count_si8, hour, minute))
            for i in range(1, count_si8 + 1, 1):
                # addr = f.read(1)
                addr = int.from_bytes(f.read(1), byteorder='big')
                data = f.read(4)
                speed = struct.unpack('f', data)[0]
                print("Счетчик = %d, Скорость=%.2f" % (addr, speed))
                d1 = datetime.datetime.strptime(filename[0:6], '%d%m%y')
                date = d1.replace(hour=hour, minute=minute)
                # mssql.insert(id_si8=addr, regName='DSPD', value=speed, now_date=date)
                pass


if __name__ == '__main__':
    main()
