#include <iostream>
#include <vector>
#include <queue>
#include <cmath>

struct Node {
    int x, y;  // 坐标
    int g, h;  // g: 从起点到当前节点的代价，h: 从当前节点到目标节点的估计代价
    Node* parent;  // 父节点

    Node(int _x, int _y) : x(_x), y(_y), g(0), h(0), parent(nullptr) {}

    // 计算当前节点到目标节点的曼哈顿距离
    int manhattanDistance(const Node& other) const {
        return std::abs(x - other.x) + std::abs(y - other.y);
    }

    // 计算当前节点的总代价 f = g + h
    int getCost() const {
        return g + h;
    }
};

int findNodeIndex(const std::vector<Node*>& nodes, const Node* node);
std::vector<Node*> findPath(const std::vector<std::vector<int>>& grid, const Node& start, const Node& end);