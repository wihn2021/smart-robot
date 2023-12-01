// 检查节点是否在开放列表中，并返回其索引
int findNodeIndex(const std::vector<Node*>& nodes, const Node* node) {
    for (size_t i = 0; i < nodes.size(); ++i) {
        if (nodes[i]->x == node->x && nodes[i]->y == node->y) {
            return static_cast<int>(i);
        }
    }
    return -1;
}

// A*算法实现
std::vector<Node*> findPath(const std::vector<std::vector<int>>& grid, const Node& start, const Node& end) {
    std::vector<Node*> openList;   // 开放列表
    std::vector<Node*> closedList; // 关闭列表

    // 创建起点节点
    Node* startNode = new Node(start.x, start.y);
    startNode->h = startNode->manhattanDistance(end);
    openList.push_back(startNode);

    while (!openList.empty()) {
        // 在开放列表中找到具有最小总代价的节点
        Node* currentNode = openList[0];
        int currentIndex = 0;
        for (size_t i = 1; i < openList.size(); ++i) {
            if (openList[i]->getCost() < currentNode->getCost()) {
                currentNode = openList[i];
                currentIndex = static_cast<int>(i);
            }
        }

        // 将当前节点从开放列表移至关闭列表
        openList.erase(openList.begin() + currentIndex);
        closedList.push_back(currentNode);

        // 如果当前节点为目标节点，已找到最短路径
        if (currentNode->x == end.x && currentNode->y == end.y) {
            std::vector<Node*> path;
            Node* node = currentNode;
            while (node != nullptr) {
                path.push_back(node);
                node = node->parent;
            }
            return path;
        }

        // 获取当前节点相邻的有效节点
        std::vector<Node*> neighbors;
        for (int x = -1; x <= 1; ++x) {
            for (int y = -1; y <= 1; ++y) {
                if (x == 0 && y == 0) {
                    continue;
                }
                int neighborX = currentNode->x + x;
                int neighborY = currentNode->y + y;
                if (neighborX >= 0 && neighborX < grid.size() && neighborY >= 0 && neighborY < grid[0].size() && grid[neighborX][neighborY] != 1) {
                    Node* neighborNode = new Node(neighborX, neighborY);
                    neighbors.push_back(neighborNode);
                }
            }
        }

        for (Node* neighbor : neighbors) {
            // 如果邻居节点已在关闭列表中，跳过
            if (findNodeIndex(closedList, neighbor) >= 0) {
                delete neighbor;
                continue;
            }

            // 计算邻居节点的g值
            int gScore = currentNode->g + 1;

            // 检查邻居节点是否已在开放列表中
            int neighborIndex = findNodeIndex(openList, neighbor);
            if (neighborIndex < 0) {
                // 邻居节点不在开放列表中，将其添加并计算h值
                neighbor->g = gScore;
                neighbor->h = neighbor->manhattanDistance(end);
                neighbor->parent = currentNode;
                openList.push_back(neighbor);
            } else {
                // 邻居节点已在开放列表中，比较新的g值与原有g值
                if (gScore < openList[neighborIndex]->g) {
                    // 更新邻居节点的g值和父节点
                    openList[neighborIndex]->g = gScore;
                    openList[neighborIndex]->parent = currentNode;
                }
                delete neighbor;
            }
        }
    }

    // 无法找到路径
    return std::vector<Node*>();
}

// 打印路径
void printPath(const std::vector<Node*>& path) {
    for (int i = static_cast<int>(path.size()) - 1; i >= 0; --i) {
        std::cout << "(" << path[i]->x << ", " << path[i]->y << ")";
        if (i > 0) {
            std::cout << " -> ";
        }
    }
    std::cout << std::endl;
}

int main() {
    // 创建一个简单的网格
    std::vector<std::vector<int>> grid = {
        {0, 0, 0, 0, 0},
        {0, 1, 0, 1, 0},
        {0, 0, 0, 0, 0},
        {0, 1, 0, 1, 0},
        {0, 0, 0, 0, 0}
    };

    // 定义起点和目标节点
    Node start(0, 0);
    Node end(4, 4);

    // 查找最短路径
    std::vector<Node*> path = findPath(grid, start, end);

    // 打印路径
    if (!path.empty()) {
        std::cout << "找到最短路径：" << std::endl;
        printPath(path);
    } else {
        std::cout << "无法找到路径。" << std::endl;
    }

    // 释放内存
    for (Node* node : path) {
        delete node;
    }

    return 0;
}