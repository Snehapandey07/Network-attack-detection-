from collections import deque


def count_reachable(graph, start):

    visited = set()
    queue = deque([start])

    while queue:

        node = queue.popleft()

        if node in visited:
            continue

        visited.add(node)

        for neighbor in graph.get(node, []):
            queue.append(neighbor)

    return len(visited)


def find_critical_node(graph):

    if not graph:
        return None, 0

    original_size = len(graph)

    most_critical = None
    biggest_loss = 0

    for node in graph:

        temp_graph = {}

        for n in graph:

            if n == node:
                continue

            temp_graph[n] = [
                neighbor
                for neighbor in graph[n]
                if neighbor != node
            ]

        if not temp_graph:
            continue

        start = next(iter(temp_graph))

        reachable = count_reachable(
            temp_graph,
            start
        )

        loss = original_size - reachable

        if loss > biggest_loss:

            biggest_loss = loss
            most_critical = node

    return most_critical, biggest_loss