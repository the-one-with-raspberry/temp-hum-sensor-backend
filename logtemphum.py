import sht21
import sys, getopt

with sht21.SHT21(1) as sht21:
    print (round(float(sht21.read_temperature()), 1))
    print (round(float(sht21.read_humidity()), 1))
