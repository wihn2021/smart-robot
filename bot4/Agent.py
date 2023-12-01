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
        formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s")
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
        self.logger.info(f"go {d}")
        steps = (d + 8) // 20
        if steps>=8:
            run_action('fastForward07')
            wait_req()
            return
        if steps>=3 and steps <=7:
            run_action('fastForward04')
            wait_req()
            return
        if steps >= 1:
            run_action('Forwalk02')
            wait_req()
        if steps == 2:
            run_action('Forwalk02')
            wait_req()
            return

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
        if shouldRotate > 0:
            run_action("turn001L")
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
        if shouldRotate <= 0:
            run_action("turn001R")
            wait_req()
            return

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
        if ang < -180:
            ang += 360
        if np.linalg.norm(self.pos[:2] - pos[:2]) > 30:
            self.logger.warn("Position error too much")
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
            if ang < -180:
                ang += 360
        self.pos = pos
        self.angle = ang
        self.logger.info(f"Current Position: {pos}, angle: {ang}")
        return pos, ang
        # return position and angle
        
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
        self.pathNodes = t[1:]
        self.logger.info(f"Path planned: {t}")

    def ContinueMyPath(self):
        nowPos, nowAng = self.getPosition()
        dist = np.linalg.norm(nowPos[:2] - self.pathNodes[0])
        self.logger.info(f"dist = {dist}")
        if dist < 20:
            self.pathNodes.pop(0)
        self.RotateToPos(self.pathNodes[0][0], self.pathNodes[0][1])
        dist = np.linalg.norm(self.pos[:2] - self.pathNodes[0])
        if dist < 20:
            self.pathNodes.pop(0)
            return
        self.BasicGoForward(dist)
        pass

    def RotateToPos(self, x,y):
        # 这个函数要改
        
        delta_x = x - self.pos[0]
        delta_y = y - self.pos[1]
        Should_rot = (np.arctan2(delta_y, delta_x) *180 /np.pi - self.angle)
        self.logger.info(f"destination: ({x}, {y}) dx: {delta_x} dy: {delta_y} should rotate to: {np.arctan2(delta_y, delta_x) *180 /np.pi} should rotate: {Should_rot}")
        if Should_rot > 180:
            Should_rot -= 360
        if Should_rot < -180:
            Should_rot += 360
        if np.abs(Should_rot) <= 15:
            return
        while np.abs(Should_rot) > 15: 
            self.BasicTurn(Should_rot)
            _ ,_ = self.getPosition()
            delta_x = x - self.pos[0]
            delta_y = y - self.pos[1]
            dist = np.linalg.norm(self.pos[:2] - self.pathNodes[0])
            if dist < 20:
                return
            Should_rot = (np.arctan2(delta_y, delta_x) *180 /np.pi - self.angle)
            if Should_rot > 180:
                Should_rot -= 360
            if Should_rot < -180:
                Should_rot += 360
            self.logger.info(f"destination: ({x}, {y}) dx: {delta_x} dy: {delta_y} should rotate to: {np.arctan2(delta_y, delta_x) *180 /np.pi} should rotate: {Should_rot}")
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

