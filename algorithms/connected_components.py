def count_components(graph):

    visited = set()
    components = 0

    def dfs(node):
        visited.add(node)

        for neighbour in graph.get(node, []):
            if neighbour not in visited:
                dfs(neighbour)

    for node in graph:

        if node not in visited:
            dfs(node)
            components += 1

    return components