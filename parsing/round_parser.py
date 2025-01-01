def split_by_round(content):
    lines = content.splitlines()

    round_data = []
    current_round = []

    for line in lines:
        if "Poker Hand" in line:  # Replace with your round identifier
            if current_round:
                round_data.append("\n".join(current_round))
                current_round = []
        current_round.append(line)

    if current_round:
        round_data.append("\n".join(current_round))
    return round_data
