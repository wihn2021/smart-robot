import heapq

def a_star(grid_map, start, goal):
    open_set = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            next_node = (current[0] + dx, current[1] + dy)
            if 0 <= next_node[0] < 50 and 0 <= next_node[1] < 50 and grid_map[next_node[0], next_node[1]] == 1:
                new_cost = cost_so_far[current] + 1
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + abs(goal[0] - next_node[0]) + abs(goal[1] - next_node[1])
                    heapq.heappush(open_set, (priority, next_node))
                    came_from[next_node] = current

    return None  # no path found

def is_clear_path(grid_map, start, end):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    for t in range(max(abs(dx), abs(dy)) + 1):
        x = start[0] + t * dx
        y = start[1] + t * dy
        ix, iy = int(round(x)), int(round(y))
        if ix < 0 or ix >= 50 or iy < 0 or iy >= 50 or grid_map[ix, iy] == 0:
            return False
    return True

def get_corner_points(path):
    corner_points = [path[0]]
    for i in range(1, len(path)-2):
        prev_node = path[i-1]
        current_node = path[i]
        next_node = path[i+1]
        if prev_node[0] - current_node[0] != current_node[0] - next_node[0] or prev_node[1] - current_node[1] != current_node[1] - next_node[1]:
            corner_points.append(current_node)
    corner_points.append(path[-1])
    return corner_points