#####################################################################
# Sensirion SFA30 python driver 
# by Jonathan Chan, ECE, HKUST
# Datasheet: https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/14_Formaldehyde_Sensors/Datasheets/Sensirion_Formaldehyde_Sensors_SFA30_Datasheet.pdf
# Shut the fuck up and use this library
#####################################################################
import serial
#####################################################################
cmd_starMeas = b'\x7E\x00\x00\x01\x00\xFE\x7E' # 7
cmd_StopMeas = b'\x7E\x00\x01\x00\xFE\x7E'     # 7
cmd_readMeas = b'\x7E\x00\x03\x01\x02\xF9\x7E' # 14
cmd_getDevIf = b'\x7E\x00\xD0\x01\x06\x28\x7E' # 25
cmd_devicRst = b'\x7E\x00\xD3\x00\x2C\x7E'     # 7
specialByteDict = {b'\x7D\x5E':b'\x7E', b'\x7D\x5D':b'\x7D', b'\x7D\x31':b'\x11', b'\x7D\x33':b'\x13'}
class sfa30:
    def __init__(self, serial):
        self.serial = serial
        self.hcho = 0
        self.temp = 0
        self.rh = 0
        self.start()

    def s16(self, value):
        return -(value & 0x8000) | (value & 0x7fff)
    
    def reset(self):
        self.serial.write(cmd_starMeas)
        self.serial.readline()

    def start(self):
        self.serial.write(cmd_starMeas)
        return self.serial.readline()

    def read(self):
        self.serial.write(cmd_readMeas)
        rxMsg = self.serial.readline()
        try:
            for key in specialByteDict.keys():
                rxMsg = rxMsg.replace(key, specialByteDict[key])
            self.hcho, self.rh, self.temp = (self.s16(rxMsg[5])*256+self.s16(rxMsg[6]))/5.0, (self.s16(rxMsg[7])*256+self.s16(rxMsg[8]))/100.0, (self.s16(rxMsg[9])*256+self.s16(rxMsg[10]))/200.0
            return self.hcho, self.temp, self.rh
        except:
            print('incorrect Msg =', rxMsg)

    def stop(self):
        self.serial.write(cmd_StopMeas)
        return self.serial.readline()

    def getInfo(self):
        self.serial.write(cmd_readMeas)
        rxMsg = self.serial.readline()
        for key in specialByteDict.keys():
                rxMsg = rxMsg.replace(key, specialByteDict[key])
        return rxMsg

#####################################################################
# Main function for __main__ or Example
def write_csv(fileName,data):
    with open(fileName, 'a') as outfile:
        writer = csv.writer(outfile,  lineterminator='\n')
        writer.writerow(data)

def loopTask():
    timestr = time.strftime("%Y%m%d")
    hcho, temp, rh = mySfa.read()
    timestampStr = '{:.2f}'.format(time.time())
    rawData = [timestampStr, hcho, temp, rh]
    print(rawData)
    write_csv('data/'+timestr+'_sfa30.csv', rawData)
    udpMsg=','.join([str(item) for item in rawData])
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.sendto(udpMsg.encode(), (UDP_IP, UDP_PORT))
    threading.Timer(1,loopTask).start() #Call itself

#Run forever
if __name__ == "__main__":
    import os, time, threading, socket, argparse, csv
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("comPort", default=0)
    args = parser.parse_args()
    if os.name == 'nt':
        myCOM = 'COM'+str(args.comPort)
    else:
        myCOM = '/dev/ttyUSB'+str(args.comPort)
    print('#####################################################################')
    print("Sensirion SFA30 Formaldehyde Sensor Module Python API\nBy FANLAB, ECE, HKUST")
    print('COM port\t=', myCOM)
    UDP_IP, UDP_PORT = "127.0.0.2", 9900+int(args.comPort)
    
    print("Experiment Date\t=", time.strftime("%Y/%m/%d"), '@', time.strftime("%H:%M"))
    print("UDP channel\t=", UDP_IP, UDP_PORT)
    Path('data').mkdir(parents=True, exist_ok=True)
    timestr = time.strftime("%Y%m%d")
    print('File created\t=','data/'+timestr+'_sfa30.csv')
    print('#####################################################################')
    mySfa = sfa30(serial.Serial(myCOM, baudrate=115200, timeout=0.01))
    time.sleep(0.1)
    loopTask()