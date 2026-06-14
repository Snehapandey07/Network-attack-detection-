def calculate_metrics(graph):

    total_nodes = len(graph)

    total_edges = sum(
        len(neighbours)
        for neighbours in graph.values()
    )

    average_degree = 0

    if total_nodes > 0:
        average_degree = round(
            total_edges / total_nodes,
            2
        )

    density = 0

    if total_nodes > 1:
        density = round(
            total_edges /
            (total_nodes * (total_nodes - 1)),
            3
        )

    return {
        "nodes": total_nodes,
        "edges": total_edges,
        "avg_degree": average_degree,
        "density": density
    }