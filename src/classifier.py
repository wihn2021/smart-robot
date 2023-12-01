from pynq import Overlay
from pynq import Xlnk
import numpy as np
from numpy.typing import ArrayLike
from PIL import Image
from typing import Union
import logging
from cv2.typing import MatLike
class Classifier:
    """
    
    """
    def __init__(self, overlay_path: str) -> None:
        self.overlay = Overlay(overlay_path)
        self.xlnk = Xlnk()
        self.x = self.xlnk.cma_array(shape=(3,28,28), dtype=np.float32)
        self.y = self.xlnk.cma_array(shape=(12), dtype=np.float32)
        self.input_ch = self.overlay.axi_dma_0.sendchannel
        self.output_ch = self.overlay.axi_dma_0.recvchannel
        self.logger = self.logger_init()

    def logger_init(self) -> logging.Logger:
        pass

    def core_classify(self, img_data: np.ndarray[np.float32]) -> np.ndarray:
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
    
    def wrap_classify(self, img: Union[ArrayLike, MatLike, Image.Image]) -> Union[int, None]:
        im_data = np.array(img).astype(np.float32)
        im_data = im_data.reshape(3,28,28).transpose(2,0,1)
        for i in range(im_data.shape[0]):
            im_data[i,:,:] = (im_data[i,:,:] - np.mean(im_data[i,:,:])) / np.std(im_data[i,:,:])
        res = self.core_classify(im_data)
        if res[0] == 0:
            # classification fail
            return None
        else:
            return res.argmax()
        