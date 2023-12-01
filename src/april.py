from typing import Any, Union
import apriltag
import logging
from numpy import dtype, ndarray
from cv2.typing import MatLike
import cv2

class BotDetect:

    def __init__(self) -> None:
        self.logger = self.logger_init()
        self.detector = apriltag.Detector(apriltag.DetectorOptions(families="tag36h11"))

    def logger_init(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(f"{__name__}.log", mode='w')
        formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

    def detect(self, img:MatLike) -> Union[tuple[list, ndarray[Any, dtype[Any]]], list]:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return self.detector.detect(gray)
