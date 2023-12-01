import logging
from communication import Channel
from action import ActionControl
from map2 import load_tag_pos
from classifier import Classifier
class Agent:

    def __init__(self) -> None:
        self.logger = self.logger_init()
        self.ch = Channel("192.168.1.254", "team16", "stupidrobot")
        self.action = ActionControl()
        self.classifier = Classifier("./overlay/enhanced.bit")

    def logger_init(self) -> logging.Logger:
        pass