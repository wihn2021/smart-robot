from cv2 import solvePnP, Rodrigues, getPerspectiveTransform, warpPerspective, projectPoints, cvtColor, COLOR_BGR2RGB
import numpy as np
from typing import Tuple, Union, Any
MatLike = Any

def pnp_rodrigues(
        corners3d: MatLike, corners2d: MatLike, intrinsic: MatLike, distortion: MatLike
        ) -> Tuple[MatLike, MatLike]:
    """
    Solve the Perspective-n-Point (PnP) problem using Rodrigues rotation formula.

    Args:
        corners3d (MatLike): 3D coordinates of object corners.
        corners2d (MatLike): 2D coordinates of object corners in the image.
        intrinsic (MatLike): Intrinsic camera matrix.
        distortion (MatLike): Distortion coefficients.

    Returns:
        Tuple[MatLike, MatLike]: Rotation matrix, translation vector.
    """
    _, rvec, tvec = solvePnP(corners3d, corners2d, intrinsic, distortion)
    R, _ = Rodrigues(rvec)
    return R, tvec

def solve_position(
        rotation_matrix: MatLike, tvec: MatLike
        ) -> Tuple[MatLike, Union[int, float]]:
    """
    Calculate the world position and Euler angle of a given rotation matrix and translation vector.

    Args:
        rotation_matrix (MatLike): The rotation matrix.
        tvec (MatLike): The translation vector.

    Returns:
        Tuple[MatLike, Union[int, float]]: A tuple containing the world position and Euler angle.
        Euler angle is in [0, 360].
    """
    rot_camera_to_world = rotation_matrix.T
    world_pos = np.matmul(-rotation_matrix.T, tvec)
    head_direction_camera = np.array([0, 0, 1]).reshape((3, 1))
    direction_vector = rot_camera_to_world @ head_direction_camera
    robot_direction = np.arctan2(direction_vector[1], direction_vector[0]) * 180 / np.pi
    eu_angle = (robot_direction + 360) % 360
    return world_pos, eu_angle

def cut_image(
        img: MatLike, screen_corners3d: MatLike, rotation_matrix: MatLike, tvec: MatLike, intrinsic: MatLike, distortion: MatLike
        ) -> MatLike:
    """
    Cuts and transforms an image based on screen corners and camera parameters.

    Args:
        img (MatLike): The input image.
        screen_corners3d (MatLike): The 3D coordinates of the screen corners.
        rotation_matrix (MatLike): The rotation matrix.
        tvec (MatLike): The translation vector.
        intrinsic (MatLike): The intrinsic camera matrix.
        distortion (MatLike): The distortion coefficients.

    Returns:
        MatLike: The transformed image.
    """
    point2d, _ = projectPoints(screen_corners3d, rotation_matrix, tvec, intrinsic, distortion)
    pts1 = point2d.astype(np.float32)
    pts2 = np.array([[0, 0], [27, 0], [27, 27], [0, 27]], dtype=np.float32)
    M = getPerspectiveTransform(pts1, pts2)
    result = warpPerspective(img, M, (28, 28))
    result = cvtColor(result, COLOR_BGR2RGB)
    return result