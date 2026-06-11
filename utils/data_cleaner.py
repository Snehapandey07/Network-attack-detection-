def normalize(name):
    return name.strip().upper()


def clean_computers(computers):
    seen = set()
    clean = []

    for c in computers:
        name = normalize(c["name"])

        if name not in seen:
            seen.add(name)
            clean.append(name)

    return clean


def clean_connections(connections, valid_nodes):
    seen = set()
    clean = []

    valid_set = set(valid_nodes)

    for c in connections:

        source = normalize(c["source"])
        dest = normalize(c["destination"])

        # rule 1: ignore self loops
        if source == dest:
            continue

        # rule 2: both must exist
        if source not in valid_set or dest not in valid_set:
            continue

        # rule 3: remove duplicates
        edge = (source, dest)

        if edge not in seen:
            seen.add(edge)
            clean.append({
                "source": source,
                "destination": dest
            })

    return clean