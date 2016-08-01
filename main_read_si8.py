#!/usr/bin/env python
r"""
Скрипт опроса Si8 по RS485
Работает под python2.7.
01-08-16 проерялся на работоспособность на windows машине
"""

import serial
import time
import owen

# c = owen.ReadSI8(1, 8, 0, 'DSPD')
# print(c)
c = owen.ReadSI8(1, 8, 0, 'DCNT')
print(c)
