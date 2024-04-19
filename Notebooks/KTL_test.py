
from KeckLFC.Hardware.USB2408 import USB2408

daq1 = USB2408(addr=0)
daq2 = USB2408(addr=1)
daq1.connect()
daq2.connect()

temp1 = daq1.get_temp_all()
temp2 = daq2.get_temp_all()

print(temp1)
print(temp2)

daq1.disconnect()
daq2.disconnect()