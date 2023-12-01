import binascii
import serial
import os
import cv2
import logging
from typing import Union
from cv2.typing import MatLike

os.system('echo "xilinx" | sudo -S  systemctl stop serial-getty@ttyPS0.service')
os.system('sleep 2')
os.system('echo "xilinx" | sudo -S  systemctl disable serial-getty@ttyPS0.service')

def run_action(cmd):
    ser = serial.Serial("/dev/ttyPS0", 9600, timeout=5)
    cnt_err = 0
    while 1:
        test_read = ser.read()
        #print('test_read', test_read)
        cnt_err += 1
        if test_read== b'\xa3' or cnt_err == 50:
            break
    
    if cnt_err == 50:
        print('can not get REQ')
    else:
        #print('read REQ finished!')
        ser.write(cmd2data(cmd))
        #print('send action ok!')
    ser.close()

def crc_calculate(package):
    crc = 0
    for hex_data in package:

        b2 = hex_data.to_bytes(1, byteorder='little')
        crc = binascii.crc_hqx(b2, crc)

    return [(crc >> 8), (crc & 255)]    # 校验位两位

def cmd2data(cmd):
    cnt=0
    cmd_list=[]
    for i in cmd:
        cnt+=1
        cmd_list+=[ord(i)]
    cmd_list=[0xff,0xff]+[(cnt+5)>>8,(cnt+5)&255]+[0x01,(cnt+1)&255,0x03]+cmd_list
    cmd_list=cmd_list+crc_calculate(cmd_list)
    return cmd_list

def wait_req():
    ser = serial.Serial("/dev/ttyPS0", 9600, timeout=5)
    while 1:
        test_read=ser.read()
        if test_read== b'\xa3' :
            #print('read REQ finished!') 
            break
        
class ActionControl:
    
    def __init__(self) -> None:
        self.logger = self.logger_init()


    def logger_init(self) -> logging.Logger:
        pass


    def head_capture(self) -> Union[MatLike, None]:
        headCam = cv2.VideoCapture(0)
        ret, frame = headCam.read()
        headCam.release()
        if ret:
            return frame
        else:
            self.logger.error("cannot take a photo")
            return None
        
    def run_str(self, command: str) -> None:
        self.logger.info("run command %s"%(command, ))
        run_action(command)
        wait_req()
        self.logger.info("command done")

    def basic_go_forward(self, d):
        self.logger.info(f"go {d}")
        steps = (d + 8) // 20
        if steps >= 8:
            self.run_str('fastForward07')
            return
        if 3 <= steps <= 7:
            self.run_str('fastForward04')
            return
        if steps >= 1:
            self.run_str('Forwalk02')
        if steps == 2:
            self.run_str('Forwalk02')

    def basic_turn(self, shouldRotate:Union[int, float]):
        self.logger.info(f"turn {shouldRotate}")
        if shouldRotate >= 50:
            # 左转
            self.run_str("turn010L")
            return
        if shouldRotate >= 25:
            self.run_str("turn005L")
            return
        if shouldRotate >= 15:
            self.run_str("turn003L")
            return
        if shouldRotate > 0:
            self.run_str("turn001L")
        if shouldRotate <= -50:
            # 右转
            self.run_str("turn010R")
            return
        if shouldRotate <= -25:
            self.run_str("turn005R")
            return
        if shouldRotate <= -15:
            self.run_str("turn003R")
            return
        if shouldRotate <= 0:
            self.run_str("turn001R")