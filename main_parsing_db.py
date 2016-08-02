r"""
01-08-16 v 0.1
Скрипт по выделению данных из файлов архива шестиреки и передачи в дазу данных MS SQL
Проверялся на python3.5.1
"""

import struct
import os
import mssql
import datetime,time

foldeder = 'real_data/'


def main():
    openfile()
    #for f in os.listdir(path=foldeder):
     #   openfile()
     #   if f.endswith('.SI8'):
     #       openfile()
      #      print("add file: %s" % f)


def openfile():
    # foldeder = 'data/'
    filename = '010716.SI8'
    with open(foldeder + filename, "rb") as f:
        count_line = 0;
        count_si8 = 1
        bufs = []
        while count_si8:
            count_si8 = int.from_bytes(f.read(1), byteorder='big')
            hour = int.from_bytes(f.read(1), byteorder='big')
            minute = int.from_bytes(f.read(1), byteorder='big')
            if minute >= 60:
                minute = 59
            # print("Счетчиков = %d, Время %d:%d" % (count_si8, hour, minute))
            for i in range(1, count_si8 + 1, 1):
                # addr = f.read(1)
                addr = int.from_bytes(f.read(1), byteorder='big')
                data = f.read(4)
                speed = struct.unpack('f', data)[0]
                #print("Счетчик = %d, Скорость=%.2f" % (addr, speed))
                d1 = datetime.datetime.strptime(filename[0:6], '%d%m%y')
                dstart = d1.replace(hour=7, minute=30)
                date = d1.replace(hour=hour, minute=minute)
                if date < dstart:
                    date = date.replace(day=date.day+1)
                if addr != 0:
                    try:
                        #print("Дата = %s, Счетчик = %d, Скорость=%.2f" % (date, addr, speed))
                        count_line += 1
                        buf = {'id_si8': addr,  'value': int(speed), 'now_date': date}
                        bufs.append(buf)

                        # time.sleep(1)
                    except Exception:
                        pass
                        print("Error - Дата = %s, Счетчик = %d, Скорость=%.2f" % (date, addr, speed))
                        #print("error")
    mssql.insert_all(bufs)
    print("Всего полей =  %s" % count_line)



if __name__ == '__main__':
    main()
