# Project for Intelligent Robots Design and Implementation of EE, Tsinghua University

<img src="https://avatars.githubusercontent.com/u/88038740?s=64&v=4" alt="Avatar" style="width: 30px; height: 30px; border-radius: 50%;" class="avatar mr-2 d-none d-md-block avatar-user">[@wihn2021](https://github.com/wihn2021)
<img src="https://avatars.githubusercontent.com/u/88665344?s=64&v=4" alt="Avatar" style="width: 30px; height: 30px; border-radius: 50%;" class="avatar mr-2 d-none d-md-block avatar-user">[@Spade14SS](https://github.com/Spade14SS) 
<img src="https://avatars.githubusercontent.com/u/150015579?s=64&v=4" alt="Avatar" style="width: 30px; height: 30px; border-radius: 50%;" class="avatar mr-2 d-none d-md-block avatar-user">[@Men-yuan](https://github.com/Men-yuan)

-----

## 目录说明

- deprecated 未经整理的代码，包括几次实验的代码（不全）

- src 决赛使用的代码，符合代码规范，由deprecated整理扩展得到

- storage 决赛后从机器人存储中拷贝下来的代码，是src因地制宜的改动版

- tools 神经网络模块

-----
## 本文目录

- [Agent](#agent)
- [ActionControl](#actioncontrol)
- [camera_algorithm](#camera_algorithm)
  - [定位](#定位)
  - [截图](#截图)
- [Classifier](#classifier)
- [Channel](#channel)
- [data augmentation](#data-augmentation)

## Agent
```python
    def main(self):
        while 1:
            self.action_frame()
```
机器人的总控制器。每次在action frame中做出决策，执行一个行为。

```python
    def action_frame(self):
        try:
            self.action.turn_head_left()
            self.observe_single(90)
            self.action.turn_head_right()
            self.observe_single(-75)
            self.action.turn_head_back()
            
            ...

        should_rotate = rad2deg(arctan2(delta_y, delta_x)) - angle
        should_rotate = should_rotate % 360 - 180
        if abs(should_rotate) > 15:
            self.action.basic_turn(should_rotate)
        else:
            self.action.basic_go_forward(linalg.norm([delta_x, delta_y]))
```
每次左右张望，识别视野里屏幕上的花朵（实际比赛降低了张望频率），然后定位（xyz坐标，相机朝向），根据定位和当前目标点，决定肢体动作

```python
    def observe_single(self, bias) -> Tuple[int, Union[ndarray, None], Union[float, int, None]]:

        ...

        image = self.action.head_capture()
        tags = self.detect.detect(image)
        if tags == None:
            return 0
        else:
            position_solutions = []
            angle_solutions = []
            for tag in tags:
                rotation_matrix, tvec = pnp_rodrigues(tag_poses[tag.tag_id], tag.corners, intrinsic, distortion)

...

            average_position = mean(position_solutions, axis=0).flatten()
            average_angle = mean(angle_solutions)
            average_angle = (average_angle + bias) % 360 - 180
            return len(tags), average_position, average_angle
```
observe_single是观察整个视野，找到1~36号tag（因为这些tag每个对应着一块屏幕），识别屏幕上的花，如果和属于本机的花不相同，就向上位机申请更换。
```python
        self.destinations = [(205,227),(128,236),(125,66),(220,75)]
        self.destination_iterator = 0

        ...

            def update_destination(self):
        if self.destination_iterator == len(self.destinations) - 1:
            self.destination_iterator = 0
        else:
            self.destination_iterator += 1

```
我们采取了固定路线的方案，抓住主要矛盾，只要把这条线路周围所有的屏幕都占据，就能获得很高的收益。

## ActionControl

具体定义了机器人的各种行动，包括前进，转向，转头等。

## camera_algorithm

### 定位

```python
def pnp_rodrigues(
        corners3d: MatLike, corners2d: MatLike, intrinsic: MatLike, distortion: MatLike
        ) -> Tuple[MatLike, MatLike]:
    _, rvec, tvec = solvePnP(corners3d, corners2d, intrinsic, distortion)
    R, _ = Rodrigues(rvec)
    return R, tvec

def solve_position(
        rotation_matrix: MatLike, tvec: MatLike
        ) -> Tuple[MatLike, Union[int, float]]:
    rot_camera_to_world = rotation_matrix.T
    world_pos = np.matmul(-rotation_matrix.T, tvec)
    head_direction_camera = np.array([0, 0, 1]).reshape((3, 1))
    direction_vector = rot_camera_to_world @ head_direction_camera
    robot_direction = np.arctan2(direction_vector[1], direction_vector[0]) * 180 / np.pi
    eu_angle = (robot_direction + 360) % 360
    return world_pos, eu_angle
```
用了cv2的solvePnP，已知tag的四角在3维世界的位置，已知tag的四角在拍到的照片中的像素位置，加上相机参数，即可解得相机位姿。

### 截图

```python
def cut_image(
        img: MatLike, screen_corners3d: MatLike, rotation_matrix: MatLike, tvec: MatLike, intrinsic: MatLike, distortion: MatLike
        ) -> MatLike:
    point2d, _ = projectPoints(screen_corners3d, rotation_matrix, tvec, intrinsic, distortion)
    pts1 = point2d.astype(np.float32)
    pts2 = np.array([[0, 0], [27, 0], [27, 27], [0, 27]], dtype=np.float32)
    M = getPerspectiveTransform(pts1, pts2)
    result = warpPerspective(img, M, (28, 28))
    result = cvtColor(result, COLOR_BGR2RGB)
    return result
```
相反地，已知一个四边形在三维世界的四角坐标，已知相机位姿，加上相机参数，即可解得这个四边形在拍到的照片中的四角位置，然后用透视变换，把这个四边形压缩成28x28的正方形，输入神经网络进行预测。要注意图像的RGB顺序！

![效果图](/deprecated/bot4/test.jpg)

## Classifier

```python
class Classifier:
    def __init__(self, overlay_path: str) -> None:
        self.overlay = Overlay(overlay_path)
        self.xlnk = Xlnk()
        self.x = self.xlnk.cma_array(shape=(3,28,28), dtype=np.float32)
        self.y = self.xlnk.cma_array(shape=(12), dtype=np.float32)
        self.input_ch = self.overlay.axi_dma_0.sendchannel
        self.output_ch = self.overlay.axi_dma_0.recvchannel
        self.logger = self.logger_init()

    def core_classify(self, img_data: np.ndarray) -> np.ndarray:
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
    
    def wrap_classify(self, img: Union[Any, Image.Image]) -> Union[str, None]:
        im_data = np.array(img).astype(np.float32)
        im_data = im_data.reshape(3,28,28).transpose(2,0,1)
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
```
注意，每次想要预测新的图片，最好重新加载一下网络，不然网络有概率输出上次的预测结果。

## Channel

```python
class Channel:
    def __init__(self, ip_addr: str, username:str, password:str) -> None:
        self.host_computer_ip = ip_addr
        self.username = username
        self.password = password
        self.logger = self.logger_init()
        self.request_count = [0] * 60

    def initialize_team(self) -> str:
        response = requests.get(f"http://{self.host_computer_ip}/initTeam/{self.username}/{self.password}", timeout=10)
        dct = response.json()
        return dct["target"]

    def practice_restart(self) -> None:
        requests.get(f"http://{self.host_computer_ip}/practiceRestart", timeout=10)

    def change_flower(self, tag_id:int, from_flower: str, to_flower: str) -> Union[int, None]:
        self.logger.info(f"change {tag_id} from {from_flower} to {to_flower}")
        response = requests.get(f"http://{self.host_computer_ip}/change/{self.username}/{self.password}/at/{tag_id}/from/{from_flower}/to/{to_flower}",
                                 timeout=3)
        ret, score_text = response.text.split()
        if ret == "Wrong":
            return None
        if ret == "Error":
            self.request_count[tag_id] += 1
        return int(score_text)
```
比较平凡的上位机通信模块，注意记录每个屏幕的错误更换次数。

## data augmentation

> 怎么用7张图片的训练集训练出70张图片的效果？

在比赛情景下，比较可能出现的干扰因素是定位不精确导致给屏幕截图不完整

![](/storage/final16/meiguihua159.jpg)
![](/storage/final16/zijinghua228.jpg)
![](/storage/final16/yuanweihua103.jpg)

```python
def add_noise(image, mean, std_dev):
...
def shift_image_black(image, shift_x, shift_y):
...
def shift_image_white(image, shift_x, shift_y):
...
def rotate_image(image, angle):
...
```
我写了4个函数用于数据增强，分别是加噪声、平移和旋转。

```python
import random
import cv2
import os
random.seed(2023)
for c in Classes:
    for root, dirs, files in os.walk(f"./data/train/{c}"):
        imglist = []
        for file in files:
            base = Image.open(f"./data/train/{c}/{file}")

            ...

        random.shuffle(imglist)
        if not os.path.exists(f"./data/enhanced_train/{c}"):
            os.mkdir(f"./data/enhanced_train/{c}")
        for ii, gg in enumerate(imglist):
            gg_bgr = cv2.cvtColor(gg, cv2.COLOR_RGB2BGR)
            cv2.imwrite(f"./data/enhanced_train/{c}/{ii}.jpg", gg_bgr)
```
分别使用这些函数对训练集进行变换，得到了10倍的图片，训练出的神经网络在比赛中发挥了重大作用。
