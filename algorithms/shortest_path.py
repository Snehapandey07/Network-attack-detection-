from collections import deque

def shortest_path(graph, start, end):

    if start not in graph:
        return None

    queue = deque([[start]])
    visited = set()

    while queue:

        path = queue.popleft()
        node = path[-1]

        if node == end:
            return path

        if node not in visited:

            visited.add(node)

            for neighbour in graph.get(node, []):
                new_path = list(path)
                new_path.append(neighbour)
                queue.append(new_path)

    return None