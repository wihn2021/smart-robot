import apriltag
import cv2
import logging
import numpy as np

class TagDetect:
    def __init__(self,tag_poses, intri, disto) -> None:

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler("april.log")
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

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
            #euAng = cv2.RQDecomp3x3(rotation_matrix)[0]
            rot_camera_to_world = rotation_matrix.T
            worldPos = np.matmul(-rotation_matrix.T,tvec)
            #euAng = np.degrees(np.arctan2(rotation_matrix[1,0],rotation_matrix[0,0]))
            pos_solutions.append(worldPos)
            head_direction_camera = np.array([0, 0, 1]).reshape((3, 1))
            direction_vector = rot_camera_to_world @ head_direction_camera
            robot_direction = np.arctan2(direction_vector[1], direction_vector[0]) * 180 / np.pi
            euAng = (robot_direction + 360) % 360
            ang_solutions.append(euAng)
            self.logger.debug(f"tag{tag.tag_id} position: {worldPos} angle: {euAng}")
        avgPos = np.mean(pos_solutions,axis=0).flatten()
        avgAng = np.mean(ang_solutions)
        if avgAng > 180:
            avgAng -= 360
        return avgPos, avgAng
    
if __name__ == "__main__":
    from envSetup import load_tag_pos
    intrinsic = np.array(([207.3099,0,314.3843],[0,205.0819,239.2206],[0,0,1]),dtype=np.double)
    distortion = np.array([0.1912,-0.0889,0,0],dtype=np.double)
    tag_poses, obstacle_centers = load_tag_pos()
    img = cv2.imread('./bot4/sample/3as.jpg')
    td = TagDetect(tag_poses, intrinsic, distortion)
    print(td.detect(img))