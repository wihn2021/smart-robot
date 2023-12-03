import binascii
import serial
import os
import cv2
import logging
from typing import Union

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
    """
    Class representing the control of actions for a robot.
    """

    def __init__(self) -> None:
        self.logger = self.logger_init()

    def logger_init(self) -> logging.Logger:
        """
        Initialize the logger for logging actions.

        Returns:
            logging.Logger: The logger object.
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(f"{__name__}.log", mode='w')
        formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

    def head_capture(self):
        """
        Capture an image from the head camera.

        Returns:
            Union[MatLike, None]: The captured image if successful, None otherwise.
        """
        headCam = cv2.VideoCapture(0)
        ret, frame = headCam.read()
        headCam.release()
        if ret:
            return frame
        else:
            self.logger.error("cannot take a photo")
            return None
        
    def run_str(self, command: str) -> None:
        """
        Run a command and log the action.

        Args:
            command (str): The command to run.
        """
        self.logger.debug("run command %s"%(command, ))
        run_action(command)
        wait_req()
        self.logger.debug("command done")

    def basic_go_forward(self, d):
        """
        Move the robot forward by a certain distance.

        Args:
            d: The distance to move forward.
        """
        self.logger.info(f"go {d}")
        steps = (d + 8) // 20
        if steps >= 3:
            self.run_str('fastForward04')
            return
        if steps >= 1:
            self.run_str('Forwalk02')
        if steps == 2:
            self.run_str('Forwalk02')

    def basic_turn(self, shouldRotate:Union[int, float]):
        """
        Turn the robot by a certain angle.

        Args:
            shouldRotate (Union[int, float]): The angle to rotate.
        """
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

    def turn_head_left(self):
        self.run_str("HeadTurn180")

    def turn_head_back(self):
        self.run_str("HeadTurnMM")
        
    def turn_head_right(self):
        self.run_str("HeadTurn015")
     

    def run_back(self):
        self.run_str("Back2Run")