def build_graph(connections):

    graph = {}

    for connection in connections:

        source = connection["source"]
        destination = connection["destination"]

        if source not in graph:
            graph[source] = []

        graph[source].append(destination)

    return graph