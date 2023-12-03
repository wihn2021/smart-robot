from pynq import Overlay
from pynq import Xlnk
from typing import Union, Any
import numpy as np
ArrayLike = Any
from PIL import Image

import logging
MatLike = Any
from constants import FLOWER_CLASSES
class Classifier:
    """
    A class that represents a classifier.

    Attributes:
        overlay (Overlay): The overlay object.
        xlnk (Xlnk): The Xlnk object.
        x (np.ndarray): The input array.
        y (np.ndarray): The output array.
        input_ch (Channel): The input channel.
        output_ch (Channel): The output channel.
        logger (logging.Logger): The logger object.

    Methods:
        __init__(self, overlay_path: str) -> None: Initializes the Classifier object.
        logger_init(self) -> logging.Logger: Initializes the logger object.
        core_classify(self, img_data: np.ndarray[np.float32]) -> np.ndarray: Performs the core classification.
        wrap_classify(self, img: Union[ArrayLike, MatLike, Image.Image]) -> Union[int, None]: Wraps the classification process.

    """

    def __init__(self, overlay_path: str) -> None:
        """
        Initializes the Classifier object.

        Args:
            overlay_path (str): The path to the overlay.

        Returns:
            None

        """
        self.path = overlay_path
        self.logger = self.logger_init()

    def logger_init(self) -> logging.Logger:
        """
        Initializes the logger object.

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
    
    def overlay_init(self):
        self.overlay = Overlay(self.path)
        self.xlnk = Xlnk()
        self.x = self.xlnk.cma_array(shape=(3,28,28), dtype=np.float32)
        self.y = self.xlnk.cma_array(shape=(12), dtype=np.float32)
        self.input_ch = self.overlay.axi_dma_0.sendchannel
        self.output_ch = self.overlay.axi_dma_0.recvchannel

    def core_classify(self, img_data: np.ndarray) -> np.ndarray:
        """
        Performs the core classification.

        Args:
            img_data (np.ndarray[np.float32]): The input image data.

        Returns:
            np.ndarray: The classification result.

        """
        for i in range(3):
            for j in range(28):
                for k in range(28):
                    self.x[i][j][k] = img_data[i][j][k]
        self.input_ch.transfer(self.x)
        self.output_ch.transfer(self.y)
        self.output_ch.wait()
        result = self.y.copy()  # Make a copy of the result
        self.y[:] = 0  # Reset the y array to zeros
        return result
    
    def wrap_classify(self, img: Union[ArrayLike, MatLike, Image.Image]) -> Union[str, None]:
        """
        Wraps the classification process.

        Args:
            img (Union[ArrayLike, MatLike, Image.Image]): The input image.

        Returns:
            Union[str, None]: The classification result.

        """
        self.overlay_init()
        im_data = np.array(img).astype(np.float32)
        im_data = im_data.transpose(2,0,1)
        for i in range(im_data.shape[0]):
            im_data[i,:,:] = (im_data[i,:,:] - np.mean(im_data[i,:,:])) / np.std(im_data[i,:,:])
        res = self.core_classify(im_data)
        if res[0] == 0:
            # classification fail
            self.logger.warn("Classification failed")
            return None
        else:
            self.logger.info(f"{res}")
            return FLOWER_CLASSES[res.argmax()]
        