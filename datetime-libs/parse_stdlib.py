from datetime import datetime

d1 = datetime.strptime('31/01/22 23:59:59.999999', '%d/%m/%y %H:%M:%S.%f')
print(d1)
d2 = datetime.strptime('2022-01-31 23:59:59', '%d/%m/%y %H:%M:%S.%f')
print(d2)
