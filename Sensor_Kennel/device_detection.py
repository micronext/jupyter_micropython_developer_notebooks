import time

def IdentifyI2CDevice(i2c):
    res = [ ]
    ads = i2c.scan()
    if 0x29 in ads:
        revid = i2c.readfrom_mem(0x29, 0xc2, 1)[0]
        devid = i2c.readfrom_mem(0x29, 0xc0, 1)[0]
        print("Revision ID:", hex(revid), "Device ID:", hex(devid))
        if devid == 0xee:
            res.append("VL53L0X lidar")
            
    if 0x40 in ads:
        i2c.writeto(0x40, b'\xFC\xC9')
        if i2c.readfrom(0x40, 1)[0] == 21:
            res.append("SI7021 humidity")
            
    if 0x39 in ads:
        chip_id = i2c.readfrom_mem(0x39, 0x80 | 0x0A, 1)[0]
        partno = (chip_id >> 4) & 0x0f  # should be 5
        if partno == 5:
            res.append("TSL561 luminous")
            
    if 0x48 in ads:
        res.append("TMP102 temp")
        
    if 0x6B in ads and 0x1E in ads:
        res.append("SDOF GyAccMag")

    if 0x77 in ads:
        if i2c.readfrom_mem(0x77, 0xD0, 1)[0] == 0x60:
            res.append("BME280 barhumid")
            
    if not res:
        desc = " ".join("%02x"%c  for c in ads  if c != 0x3c)
        if desc:
            res.append("unknown %s" % desc)
        
    return res

# UART(1, baudrate=9600, rx=13, tx=12)
def IdentifyUARTDevice(uart):
    res = [ ]
    uart.init(baudrate=115200)
    for i in range(3):
        uart.read()
        uart.write(b"\xAA\x01\x00\x06")  # request chip_id and firmware version
        time.sleep_ms(20)
        r = uart.read()
        if r is not None and len(r) == 8 and r[:3] == b'\xbb\x06\xa0':
            swversion = "%d.%d" % (r[6], r[7])  # 8.3
            res.append("BNO055 orient")
            break
        time.sleep(0.2)
            
    # next have a look for the GPS module if plugged in
    return res
    
    