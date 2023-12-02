from enum import Enum
from map2 import load_tag_pos
import numpy as np

FLOWER_CLASSES = ['bailianhua',
 'chuju',
 'hehua',
 'juhua',
 'lamei',
 'lanhua',
 'meiguihua',
 'shuixianhua',
 'taohua',
 'yinghua',
 'yuanweihua',
 'zijinghua']

tag_poses, obstacle_centers, screens = load_tag_pos()

intrinsic = np.array(([207.9138,0,315.9991],[0,206.5876,242.7096],[0,0,1]),dtype=np.double)

distortion = np.array([0.2345,-0.1114,0,0],dtype=np.double)

class BotState(Enum):
    BEGIN = 1
    WALK = 2