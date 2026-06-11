def has_cycle(graph):

    visited = set()
    recursion_stack = set()

    def dfs(node):

        visited.add(node)
        recursion_stack.add(node)

        for neighbour in graph.get(node, []):

            if neighbour not in visited:

                if dfs(neighbour):
                    return True

            elif neighbour in recursion_stack:
                return True

        recursion_stack.remove(node)

        return False

    for node in graph:

        if node not in visited:

            if dfs(node):
                return True

    return False