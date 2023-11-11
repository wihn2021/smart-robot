import apriltag
import cv2
import numpy as np

class TagDetect:
    def __init__(self,tag_poses, intri, disto) -> None:
        self.options = apriltag.DetectorOptions(families="tag36h11")
        self.detector = apriltag.Detector(self.options)
        self.intrinsic = intri
        self.distortion = disto
        self.tagStandard = tag_poses

    def detect(self, BGRimg):
        gray = cv2.cvtColor(BGRimg, cv2.COLOR_BGR2GRAY)
        tags = self.detector.detect(gray)
        return tags
    
    def solvePos(self,tags):
        pos_solutions = []
        ang_solutions = []
        for tag in tags:
            _, rvec, tvec = cv2.solvePnP(self.tagStandard[str(tag.tag_id)], tag.corners, self.intrinsic, self.distortion)
            rotation_matrix, _ = cv2.Rodrigues(rvec)
            worldPos = np.matmul(-np.linalg.inv(rotation_matrix),tvec)
            euAng = np.degrees(np.arctan2(rotation_matrix[1,0],rotation_matrix[0,0]))
            pos_solutions.append(worldPos)
            ang_solutions.append(euAng)
        avgPos = np.mean(pos_solutions)
        avgAng = np.mean(ang_solutions)
        return avgPos, avgAng