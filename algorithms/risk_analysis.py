def calculate_risk(
    cycle_found,
    components,
    total_nodes
):

    score = 0

    if cycle_found:
        score += 40

    if components == 1:
        score += 20

    if total_nodes >= 5:
        score += 20

    if total_nodes >= 10:
        score += 20

    if score >= 80:
        level = "HIGH"

    elif score >= 50:
        level = "MEDIUM"

    else:
        level = "LOW"

    return score, level