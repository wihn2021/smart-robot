import cv2
import AprilLib
import pathLib
import mapSetup
import numpy as np
from basic import run_action, wait_req

class BotAgent:

    def __init__(self, tag_poses, intri, disto) -> None:
        self.cameraSetup()
        self.dec = AprilLib.TagDetect(tag_poses, intri, disto)
        self.pathNodes = []
        self.pos = (0,0,0)
        self.angle = 0

    def cameraSetup(self):
        self.headCam = cv2.VideoCapture(0)
        self.chestCam = cv2.VideoCapture(2)
        pass

    def cameraCleanUp(self):
        self.headCam.release()
        self.chestCam.release()
        pass

    def headCapture(self):
        ret, frame = self.headCam.read()
        if ret:
            return frame
        else:
            return None

    def chestCapture(self):
        ret, frame = self.chestCam.read()
        if ret:
            return frame
        else:
            return None

    def BasicGoForward(d):
        
        pass

    def BasicTurn(a):

        pass

    def getPosition(self):
        pic = self.headCapture()
        tags = self.dec.detect(pic)
        bias = 0
        if len(tags) == 0:
            self.BasicHeadTurn()
            pic = self.headCapture()
            tags = self.dec.detect(pic)
            bias = 180
        pos,ang = self.dec.solvePos(tags)
        ang += bias
        if ang > 180:
            ang -= 360
        self.pos = pos
        self.angle = ang
        return pos, ang
        # return position and angle
        pass
        
    def BasicHeadTurn(self):
        run_action("HeadTurn180")
        wait_req()

    def generatePathNodes(self,x,y,ang):
        nowPos, nowAng = self.getPosition()
        dep = mapSetup.pixel_2_grid(nowPos[0], nowPos[1])
        dst = mapSetup.pixel_2_grid(x, y)
        self.pathNodes = pathLib.get_corner_points(pathLib.a_star(dep, dst))
        t = []
        for n in self.pathNodes:
            t.append(mapSetup.grid_2_pixel(n))
        self.pathNodes = t

    def ContinueMyPath(self):
        nowPos, nowAng = self.getPosition()
        dist = np.linalg.norm(nowPos - self.pathNodes[0])
        if dist < 6:
            self.pathNodes.pop(0)
        self.RotateToPos(self.pathNodes[0].x, self.pathNodes[0].y)
        self.BasicGoForward()
        pass

    def RotateToPos(self, x,y):
        
        pass

    def CloseAgent(self):
        self.headCam.release()
        self.chestCam.release()
