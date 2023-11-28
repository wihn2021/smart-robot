from envSetup import load_tag_pos
from mapSetup import create_grid_map, draw_grid, plot_path_on_map
import pathLib
import numpy as np
#from Agent import BotAgent

intrinsic = np.array(([207.3099,0,314.3843],[0,205.0819,239.2206],[0,0,1]),dtype=np.double)

distortion = np.array([0.1912,-0.0889,0,0],dtype=np.double)

tag_poses, obstacle_centers = load_tag_pos()
#agent = BotAgent(tag_poses, intrinsic, distortion)

#print(agent.getPosition())

#obstacles = group_obstacles(tag_poses)
grid_map = create_grid_map(obstacle_centers)
#print(tag_poses)
#plot_map(tag_poses)
draw_grid(grid_map)
path = pathLib.a_star(grid_map, (2,2), (49,15))
path2 = pathLib.get_corner_points(path)
plot_path_on_map(grid_map, path)
plot_path_on_map(grid_map, path2)
