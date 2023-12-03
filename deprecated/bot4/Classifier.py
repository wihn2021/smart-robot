from pynq import Overlay
from pynq import Xlnk
import pynq.lib.dma
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def my_transform(img):
    img = img.resize((28,28))
    im_data = np.array(img).astype(np.float32)
    im_data = im_data.transpose(2,0,1)
    for i in range(im_data.shape[0]):
        im_data[i,:,:] = (im_data[i,:,:] - np.mean(im_data[i,:,:])) / np.std(im_data[i,:,:])
    return im_data

class Classifier:
    def __init__(self, overlay_path) -> None:
        self.overlay = Overlay(overlay_path)
        self.xlnk = Xlnk()
        self.x = self.xlnk.cma_array(shape=(3,28,28), dtype=np.float32)
        self.y = self.xlnk.cma_array(shape=(12), dtype=np.float32)
        self.input_ch = self.overlay.axi_dma_0.sendchannel
        self.output_ch = self.overlay.axi_dma_0.recvchannel

    def judge(self, img):
        data = my_transform(img)
        for i in range(3):
            for j in range(28):
                for k in range(28):
                    self.x[i][j][k] = data[i][j][k]
        self.input_ch.transfer(self.x)
        self.output_ch.transfer(self.y)
        self.output_ch.wait()
        return self.y