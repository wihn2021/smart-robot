import logging
from communication import Channel
from action import ActionControl
from map2 import load_tag_pos
from classifier import Classifier
from camera_algorithm import pnp_rodrigues, solve_position, cut_image
from april import BotDetect
from constants import tag_poses, obstacle_centers, screens, tag_ori, intrinsic, distortion
from numpy import mean, ndarray, rad2deg, arctan2, linalg
from typing import Tuple, Union
import time
class Agent:
    """
    The Agent class represents a robot agent that interacts with the environment.

    Attributes:
        logger (logging.Logger): The logger object for logging debug information.
        ch (Channel): The channel object for communication with the server.
        action (ActionControl): The action control object for controlling the robot's actions.
        classifier (Classifier): The classifier object for classifying flowers.
        detect (BotDetect): The bot detect object for detecting tags in the environment.
        my_flower (str): The type of flower that the agent represents.
        position (Tuple[float, float, float]): The current position of the agent in 3D space.
        angle (float): The current angle of the agent.
        screen_record (List[Union[str, None]]): The record of flower classifications for each screen.
        game_start_time (float): The time when the game started.
        score (int): The current score of the agent.

    Methods:
        get_game_continue_time() -> float:
            Returns the duration of the game in seconds since it started.
        logger_init() -> logging.Logger:
            Initializes the logger object and returns it.
        observe_single(bias) -> Tuple[int, Union[ndarray, None], Union[float, int, None]]:
            Observes the environment in a single direction, detects tags, classifies flowers, and updates position.
        rotate_to_position():
            Rotates the agent to a specific position.
    """
    def __init__(self) -> None:
        self.logger = self.logger_init()
        self.ch = Channel("192.168.1.254", "team16", "stupidrobot")
        self.action = ActionControl()
        self.classifier = Classifier("../overlay/enhanced.bit")
        self.detect = BotDetect()
        self.my_flower = self.ch.initialize_team()
        self.position = None
        self.angle = None
        self.screen_record = [None] * 36
        self.game_start_time = time.time()
        self.score = 0
        self.destinations = []
        self.destination_iterator = 0

    def get_current_destination(self):
        return self.destinations[self.destination_iterator]

    def get_game_continue_time(self) -> float:
        """
        Returns the duration of the game in seconds since it started.

        Returns:
            float: The duration of the game in seconds.
        """
        return time.time() - self.game_start_time

    def logger_init(self) -> logging.Logger:
        """
        Initializes the logger object and returns it.

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
    
    def observe_single(self, bias) -> Tuple[int, Union[ndarray, None], Union[float, int, None]]:
        """
        Observes the environment in a single direction, detects tags to classify flowers, and updates position.

        Args:
            bias: The bias value.

        Returns:
            Tuple[int, Union[ndarray, None], Union[float, int, None]]: A tuple containing the number of tags detected,
                the average position of the tags, and the average angle of the tags.
        """
        image = self.action.head_capture()
        tags = self.detect.detect(image)
        if tags == None:
            return 0
        else:
            position_solutions = []
            angle_solutions = []
            for tag in tags:
                rotation_matrix, tvec = pnp_rodrigues(tag_poses[tag.tag_id], tag.corners, intrinsic, distortion)
                position, angle = solve_position(rotation_matrix, tvec)
                position_solutions.append(position)
                angle_solutions.append(angle)

                if tag.tag_id < 37:
                    average_angle = mean(angle_solutions)
                    thres = 30
                    if abs(average_angle - tag_ori[tag.tag_id]) % 180 < (90 + thres) and  abs(average_angle - tag_ori[tag.tag_id]) % 180 > (90 - thres) :
                        continue
                    image_28x28 = cut_image(image, screens[tag.tag_id], rotation_matrix, tvec, intrinsic, distortion)
                    classify_result = self.classifier.wrap_classify(image_28x28)
                    if classify_result == None:
                        pass
                    else:
                        self.screen_record[tag.tag_id] = classify_result
                        if classify_result != self.my_flower and (
                            self.ch.request_count[tag.tag_id] < 4 or self.get_game_continue_time() > 480
                            ):
                            change_result = self.ch.change_flower(tag.tag_id, classify_result, self.my_flower)
                            if change_result != None:
                                self.score = change_result

            average_position = mean(position_solutions, axis=0).flatten()
            average_angle = mean(angle_solutions)
            average_angle = (average_angle + bias) % 360 - 180
            return len(tags), average_position, average_angle

    def action_frame(self):
        tag_num, position, angle = self.observe_single(0)
        if tag_num == 0:
            self.action.turn_head_left()
            tag_num, position, angle = self.observe_single(90)
            self.action.turn_head_back()
            if tag_num == 0:
                self.action.basic_turn(90)
                return
        current_destination = self.get_current_destination()
        delta_x = current_destination[0] - position[0]
        delta_y = current_destination[1] - position[1]
        while linalg.norm([delta_x, delta_y]) < 15:
            self.update_destination()
            current_destination = self.get_current_destination()
            delta_x = current_destination[0] - position[0]
            delta_y = current_destination[1] - position[1]
        should_rotate = rad2deg(arctan2(delta_y, delta_x)) - angle
        should_rotate = should_rotate % 360 - 180
        if abs(should_rotate) > 15:
            self.action.basic_turn(should_rotate)
        else:
            self.action.basic_go_forward(linalg.norm([delta_x, delta_y]))
    
    def update_destination(self):
        if self.destination_iterator == len(self.destinations) - 1:
            self.destination_iterator = 0
        else:
            self.destination_iterator += 1

    def main(self):
        while 1:
            self.action_frame()