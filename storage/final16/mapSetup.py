import matplotlib.pyplot as plt
import numpy as np

GridSize = 6

def plot_map(tag_poses):
    fig, ax = plt.subplots()

    for i in range(1, 10):
        obstacle_coords = [tag_poses[str((i-1)*4 + j + 1)] for j in range(4)]
        obstacle_coords[1], obstacle_coords[3] = obstacle_coords[3], obstacle_coords[1]
        obstacle_coords.append(obstacle_coords[0])  # close the polygon
        obstacle_coords = np.array(obstacle_coords)
        ax.plot(obstacle_coords[:, 0], obstacle_coords[:, 1], color='red')  # obstacle

    for i in range(37, 54):
        ax.scatter(*tag_poses[str(i)][0], color='blue')  # ground marker

    plt.show()


def create_grid_map(obstacles):
    grid_map = np.ones((50, 50))
    for ob in obstacles:
        obx = int(ob[0]/6+0.5)
        oby = int(ob[1]/6+0.5)
        #grid_map[obx,oby] = 0
        for i in range(obx - 5, obx + 6):
            for j in range(oby - 5, oby + 6):
                if i >= 0 and i < 50 and j >= 0 and j < 50:
                    grid_map[i, j] = 0
    return grid_map

def group_obstacles(tag_poses):
    obstacles = {}
    for i in range(1, 10):
        start_key = (i-1)*4 + 1
        end_key = i*4
        obstacles[i] = {str(k): v for k, v in tag_poses.items() if start_key <= int(k) <= end_key}
    return obstacles

def draw_grid(grid):
    plt.figure()
    plt.imshow(grid, cmap='gray', origin='lower')
    plt.show()

def plot_path_on_map(grid_map, path):
    grid_map_with_path = grid_map.copy()
    for node in path:
        grid_map_with_path[node[0], node[1]] = 2

    plt.figure()
    plt.imshow(grid_map_with_path, cmap='viridis', origin='lower')
    plt.show()

def grid_2_pixel(x,y):
    return x*6+3,y*6+3

def pixel_2_grid(x,y):
    return int(x/6+0.5), int(y/6+0.5)