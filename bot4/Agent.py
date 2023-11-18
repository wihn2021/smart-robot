import cv2
import AprilLib
import pathLib
import mapSetup
import numpy as np
import logging
from basic import run_action, wait_req

class BotAgent:

    def __init__(self, tag_poses,gridmap, intri, disto) -> None:

        # 下面是日志设置
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler("bot.log")
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.dec = AprilLib.TagDetect(tag_poses, intri, disto)
        self.pathNodes = []
        self.pos = (0,0,0)
        self.angle = 0
        self.gridmap = gridmap

    def headCapture(self):
        headCam = cv2.VideoCapture(0)
        ret, frame = headCam.read()
        headCam.release()
        if ret:
            return frame
        else:
            self.logger.error("cannot take a photo")
            return None

    def chestCapture(self):
        chestCam = cv2.VideoCapture(2)
        ret, frame = chestCam.read()
        chestCam.release()
        if ret:
            return frame
        else:
            return None

    def BasicGoForward(self,d):
        steps = (d + 4) // 8
        while steps>=8:
            run_action(f'fastForward0{4}')
            wait_req()
            steps -= 4
        if steps>=3 and steps <=7:
            run_action(f'fastForward0{steps}')
            wait_req()
            return
        if steps >= 1:
            run_action('Forwalk02')
            wait_req()
            return
        if steps == 2:
            run_action('Forwalk02')
            wait_req()
            return
        pass

    def BasicTurn(self,shouldRotate):
        self.logger.info(f"turn {shouldRotate}")
        if shouldRotate >= 50:
        #左转
            run_action("turn010L")
            wait_req()
            return
        if shouldRotate >= 25:
            run_action("turn005L")
            wait_req()
            return
        if shouldRotate >= 15:
            run_action("turn003L")
            wait_req()
            return
        if shouldRotate <= -50:
            #右转
            run_action("turn010R")
            wait_req()
            return
        if shouldRotate <= -25:
            run_action("turn005R")
            wait_req()
            return
        if shouldRotate <= -15:
            run_action("turn003R")
            wait_req()
            return
        pass

    def getPosition(self):
        pic = self.headCapture()
        tags = self.dec.detect(pic)
        bias = 0
        if len(tags) == 0:
            self.BasicHeadTurn()
            pic = self.headCapture()
            self.HeadTurnBack()
            tags = self.dec.detect(pic)
            bias = -90
        pos,ang = self.dec.solvePos(tags)
        ang += bias
        if ang > 180:
            ang -= 360
        self.pos = pos
        self.angle = ang
        self.logger.info(f"Current Position: {pos}, angle: {ang}")
        return pos, ang
        # return position and angle
        pass
        
    def BasicHeadTurn(self):
        run_action("HeadTurn180")
        wait_req()

    def HeadTurnBack(self):
        run_action("HeadTurnMM")
        wait_req()

    def generatePathNodes(self,x,y,ang):
        nowPos, nowAng = self.getPosition()
        dep = mapSetup.pixel_2_grid(nowPos[0], nowPos[1])
        dst = mapSetup.pixel_2_grid(x, y)
        self.pathNodes = pathLib.get_corner_points(pathLib.a_star(self.gridmap,dep, dst))
        t = []
        for n in self.pathNodes:
            t.append(mapSetup.grid_2_pixel(n[0],n[1]))
        self.pathNodes = t
        self.logger.info(f"Path planned: {t}")

    def ContinueMyPath(self):
        nowPos, nowAng = self.getPosition()
        dist = np.linalg.norm(nowPos[:2] - self.pathNodes[0])
        if dist < 14:
            self.pathNodes.pop(0)
        self.RotateToPos(self.pathNodes[0][0], self.pathNodes[0][1])
        self.BasicGoForward(dist)
        pass

    def RotateToPos(self, x,y):
        # 这个函数要改
        
        delta_x = x - self.pos[0]
        delta_y = y - self.pos[1]
        Should_rot = (-np.arctan2(delta_x, delta_y) *180 /np.pi - self.angle)
        self.logger.info(f"destination: ({x}, {y}) dx: {delta_x} dy: {delta_y} should rotate: {Should_rot}")
        if Should_rot > 180:
            Should_rot -= 360
        if Should_rot < -180:
            Should_rot += 360
        while np.abs(Should_rot) > 10: 
            self.BasicTurn(Should_rot)
            _ ,_ = self.getPosition()
            Should_rot = (-np.arctan2(delta_x, delta_y) *180 /np.pi - self.angle)
            if Should_rot > 180:
                Should_rot -= 360
            if Should_rot < -180:
                Should_rot += 360
        pass


    def Main(self, des_x,des_y,des_ang):
        self.generatePathNodes(des_x,des_y,des_ang)
        while len(self.pathNodes) > 0:
            self.ContinueMyPath()
        self.getPosition()
        Should_rot = (des_ang - self.angle)
        if Should_rot > 180:
            Should_rot -= 360
        if Should_rot < -180:
            Should_rot += 360