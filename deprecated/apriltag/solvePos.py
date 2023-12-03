import numpy as np
import cv2

def solvePositionAndRotation(tag_pos, corners, intri, disto):
    # tag_size = 0.05  # AprilTag的实际尺寸（米）
    '''
    object_points = np.array([[-tag_size / 2, tag_size / 2, 0],
                             [tag_size / 2, tag_size / 2, 0],
                             [tag_size / 2, -tag_size / 2, 0],
                             [-tag_size / 2, tag_size / 2, 0]], dtype=np.float32)
    
    object_points = object_points + tag_pos
    '''

    # AprilTag的像素坐标
    '''
    image_points = np.array([[corners[0,0], corners[0,1]],
                             [corners[1,0], corners[1,1]],
                             [corners[2,0], corners[2,1]],
                             [corners[3,0], corners[3,1]]], dtype=np.float32)
    '''
    # PnP姿态解算
    _, rvec, tvec = cv2.solvePnP(tag_pos, corners, intri, disto)

    # 将旋转向量转换为旋转矩阵
    rotation_matrix, _ = cv2.Rodrigues(rvec)
    worldPos = np.matmul(-np.linalg.inv(rotation_matrix),tvec)
    euAng = np.degrees(np.arctan2(rotation_matrix[1,0],rotation_matrix[0,0]))
    return worldPos, euAng

def getShouldRotAngle(realPos, ang):
    shouldRotate = np.degrees(np.arctan2(realPos[0],-realPos[1])) - ang
    if shouldRotate > 180:
        shouldRotate -= 360
    if shouldRotate < 180:
        shouldRotate += 360
    return shouldRotate