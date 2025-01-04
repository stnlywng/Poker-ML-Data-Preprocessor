import re

extract_button_regex = r"#(\d+)"
uid_seat_stack_regex = r"Seat (\d+): (\w+) \(([\d,]+) in chips\)"
hole_card_regex = r"Dealt to Hero \[([^\s\]]+)\s+([^\s\]]+)\]"
blinds_regex = r"posts big blind (\d+)"

posts_regex = r"(\w+):.*\b(\d+)$"
raise_regex = r"(\S+): (\w+) \d+(?:,\d+)* to (\d+(?:,\d+)*)"
normal_action_regex = r"(\S+): (\w+)(?: (\d+(?:,\d+)*))?"

flop_pattern = r"\*\*\* FLOP \*\*\* \[([2-9TJQKA][hdcs]) ([2-9TJQKA][hdcs]) ([2-9TJQKA][hdcs])\]"
turn_pattern = r"\*\*\* TURN \*\*\* \[[2-9TJQKA][hdcs] [2-9TJQKA][hdcs] [2-9TJQKA][hdcs]\] \[([2-9TJQKA][hdcs])\]"
river_pattern = r"\*\*\* RIVER \*\*\* \[[2-9TJQKA][hdcs] [2-9TJQKA][hdcs] [2-9TJQKA][hdcs] [2-9TJQKA][hdcs]\] \[([2-9TJQKA][hdcs])\]"

# Table '1' 8-max Seat #6 is the button
def extract_button(line):
    match = re.search(extract_button_regex, line)
    if match:
        return int(match.group(1))  # Extract the capturing group

def get_position_name(num_players, seat, btn):
    loc = (seat - btn) % num_players
    if loc == 0:
        return "btn"
    elif loc == 1:
        return "sb"
    elif loc == 2:
        return "bb"
    elif loc == (num_players - 1): #[6]
        return "co"
    elif loc == (num_players - 2): #[5]
        return "hj"
    elif loc == 3:
        return "utg1"
    elif loc == (num_players - 3): #[4]
        return "lj"
    elif loc == 4:
        return "utg2"
    elif loc == 5:
        return "utg3"

# Seat 3: 76610b78 (9,074 in chips)
def populate_uid_to_seatstack_map(working_map, lines, num_players, btn):
    i = 0
    while "Seat" in lines[2 + i]:
        print("working on line: ", lines[2 + i])
        extract = re.findall(uid_seat_stack_regex, lines[2 + i])
        seat, uid, chip_count = extract[0]
        chip_count = chip_count.replace(',', '')
        print(f"found uid {uid} with {seat} with {chip_count}")
        working_map[uid] = (get_position_name(num_players, (i + 1), btn), int(chip_count))
        i += 1

# Count by how many "in chips" are present.
def extract_num_players(round):
    num_p = re.findall(r"in chips", round)
    return len(num_p)

# posts big blind 160
def extract_blinds(round):

    match = re.search(blinds_regex, round)
    j = match.group(1)
    if match:
        return int(match.group(1))

# Dealt to Hero [2s 8h]
def extract_hole(round):
    match = re.search(hole_card_regex, round)
    if match:
        return (match.group(1), match.group(2))


# (Start Round Pot, All Actions Till Round (multiple arrays could be), Current Round Actoins, Label - (action, chip_count)))
def rectrieve_actions_chip_counts_labels_for_hero(round, lines, uid_to_seatstack):
    current_round = ""
    current_pot = 0

    pf_start_pot = 0
    flop_start_pot = 0
    turn_start_pot = 0
    river_start_pot = 0

    preflop = []
    flop = []
    turn = []
    river = []

    preflop_actions = []
    flop_actions = []
    turn_actions = []
    river_actions = []

    for line in lines:
        # Means we got to some sort of show-down
        if "shows" in line or "returned" in line:
            break
        # Go through the log.
        if current_round == "":
            if "posts" in line:
                t = re.findall(posts_regex, line)
                uid, chip_count = t[0]
                chip_count = int(chip_count.replace(',', ''))
                seat, stack = uid_to_seatstack[uid]
                current_pot += chip_count
                preflop_actions.append((seat, "posts", chip_count))
            elif "HOLE CARDS" in line:
                current_round = "pf"
                pf_start_pot = current_pot
        elif current_round == "pf":
            if "Dealt to" in line:
                continue
            elif "FLOP" in line:
                current_round = "f"
                flop_start_pot = current_pot
            elif "Hero" in line:
                if "raises" in line:
                    t = re.findall(raise_regex, line)
                else:
                    t = re.findall(normal_action_regex, line)

                uid, action, chip_count = t[0]
                chip_count = chip_count.replace(',', '')

                if chip_count == "":
                    chip_count = None
                else:
                    chip_count = int(chip_count)
                    current_pot += chip_count

                if "all-in" in line:
                    action += " all-in"

                seat, stack = uid_to_seatstack[uid]

                preflop.append((pf_start_pot, preflop_actions.copy(), (action, chip_count)))
                preflop_actions.append((seat, action, chip_count))
            else:
                if "raises" in line:
                    t = re.findall(raise_regex, line)
                else:
                    t = re.findall(normal_action_regex, line)

                uid, action, chip_count = t[0]
                chip_count = chip_count.replace(',', '')

                if chip_count == "":
                    chip_count = None
                else:
                    chip_count = int(chip_count)
                    current_pot += chip_count

                if "all-in" in line:
                    action += " all-in"

                seat, stack = uid_to_seatstack[uid]
                preflop_actions.append((seat, action, chip_count))
        elif current_round == "f":
            if "TURN" in line:
                current_round = "t"
                turn_start_pot = current_pot
            elif "Hero" in line:
                if "raises" in line:
                    t = re.findall(raise_regex, line)
                else:
                    t = re.findall(normal_action_regex, line)

                uid, action, chip_count = t[0]
                chip_count = chip_count.replace(',', '')

                if chip_count == "":
                    chip_count = None
                else:
                    chip_count = int(chip_count)
                    current_pot += chip_count

                if "all-in" in line:
                    action += " all-in"

                seat, stack = uid_to_seatstack[uid]

                flop.append((flop_start_pot, preflop_actions, flop_actions.copy(), (action, chip_count)))
                flop_actions.append((seat, action, chip_count))
            else:
                if "raises" in line:
                    t = re.findall(raise_regex, line)
                else:
                    t = re.findall(normal_action_regex, line)

                uid, action, chip_count = t[0]
                chip_count = chip_count.replace(',', '')

                if chip_count == "":
                    chip_count = None
                else:
                    chip_count = int(chip_count)
                    current_pot += chip_count

                if "all-in" in line:
                    action += " all-in"

                seat, stack = uid_to_seatstack[uid]
                flop_actions.append((seat, action, chip_count))

        elif current_round == "t":
            if "RIVER" in line:
                current_round = "r"
                river_start_pot = current_pot
            elif "Hero" in line:
                if "raises" in line:
                    t = re.findall(raise_regex, line)
                else:
                    t = re.findall(normal_action_regex, line)

                uid, action, chip_count = t[0]
                chip_count = chip_count.replace(',', '')

                if chip_count == "":
                    chip_count = None
                else:
                    chip_count = int(chip_count)
                    current_pot += chip_count

                if "all-in" in line:
                    action += " all-in"

                seat, stack = uid_to_seatstack[uid]

                turn.append((turn_start_pot, preflop_actions, flop_actions, turn_actions.copy(), (action, chip_count)))
                turn_actions.append((seat, action, chip_count))
            else:
                if "raises" in line:
                    t = re.findall(raise_regex, line)
                else:
                    t = re.findall(normal_action_regex, line)

                uid, action, chip_count = t[0]
                chip_count = chip_count.replace(',', '')

                if chip_count == "":
                    chip_count = None
                else:
                    chip_count = int(chip_count)
                    current_pot += chip_count

                if "all-in" in line:
                    action += " all-in"

                seat, stack = uid_to_seatstack[uid]
                turn_actions.append((seat, action, chip_count))
        elif current_round == "r":
            if "SHOWDOWN" in line:
                break
            elif "Hero" in line:
                if "raises" in line:
                    t = re.findall(raise_regex, line)
                else:
                    t = re.findall(normal_action_regex, line)

                uid, action, chip_count = t[0]
                chip_count = chip_count.replace(',', '')

                if chip_count == "":
                    chip_count = None
                else:
                    chip_count = int(chip_count)
                    current_pot += chip_count

                if "all-in" in line:
                    action += " all-in"

                seat, stack = uid_to_seatstack[uid]

                river.append((river_start_pot, preflop_actions, flop_actions, turn_actions, river_actions.copy(), (action, chip_count)))
                river_actions.append((seat, action, chip_count))
            else:
                if "raises" in line:
                    t = re.findall(raise_regex, line)
                else:
                    t = re.findall(normal_action_regex, line)

                uid, action, chip_count = t[0]
                chip_count = chip_count.replace(',', '')

                if chip_count == "":
                    chip_count = None
                else:
                    chip_count = int(chip_count)
                    current_pot += chip_count

                if "all-in" in line:
                    action += " all-in"

                seat, stack = uid_to_seatstack[uid]
                river_actions.append((seat, action, chip_count))

    return preflop, flop, turn, river

# *** FLOP *** [6s 9d Qs]
def extract_flop(round):
    match = re.search(flop_pattern, round)
    if match:
        return [match.group(1), match.group(2), match.group(3)]
    else:
        return None

# *** TURN *** [6s 9d Qs] [7s]
def extract_turn(round):
    # "Dealt to Hero [3d 2d]"
    match = re.search(turn_pattern, round)
    if match:
        return match.group(1)
    else:
        return None

#*** RIVER *** [6s 9d Qs 7s] [5c]
def extract_river(round):
    match = re.search(river_pattern, round)
    if match:
        return match.group(1)
    else:
        return None


def calculate_start_round_stacks(uid_to_seatstack, preflop_actions = None, flop_actions = None, turn_actions = None):
    tracker = {val1: val2 for _, (val1, val2) in uid_to_seatstack.items()}

    if preflop_actions:
        for seat, action, count in preflop_actions:
            if count:
                tracker[seat] -= count
    if flop_actions:
        for seat, action, count in flop_actions:
            if count:
                tracker[seat] -= count
    if turn_actions:
        for seat, action, count in turn_actions:
            if count:
                tracker[seat] -= count

    return list(tracker.items())


def ggpoker_to_schema(round):
    lines = round.split("\n")

    # needed for all rounds (pre-flop, flop, turn, river)
    btn = extract_button(lines[1])
    num_players = extract_num_players(round)

    uid_to_seatstack = {}  # ("6539a8dd", ("btn", 3600))
    populate_uid_to_seatstack_map(uid_to_seatstack, lines, num_players, btn)


    position, c = uid_to_seatstack["Hero"]
    blinds = extract_blinds(round)
    hole_cards = extract_hole(round)
    flop_cards = extract_flop(round)
    turn_card = extract_turn(round)
    river_card = extract_river(round)

    # (Start Round Pot, All Actions Till Round (multiple arrays could be), Current Round Actoins, Label - (action, chip_count)))
    preflop, flop, turn, river = rectrieve_actions_chip_counts_labels_for_hero(round, lines, uid_to_seatstack)

    finals = []

    for t in preflop:
        start_round_pot, actions, label = t
        start_round_stacks = calculate_start_round_stacks(uid_to_seatstack)
        game_state = ("pf", hole_cards, num_players, position, blinds, start_round_pot, start_round_stacks, actions)
        finals.append((game_state, label))

    for t in flop:
        start_round_pot, pf_actions, actions, label = t
        start_round_stacks = calculate_start_round_stacks(uid_to_seatstack, pf_actions)
        game_state = ("f", hole_cards, flop_cards, num_players, position, blinds, start_round_pot, start_round_stacks, actions, pf_actions)
        finals.append((game_state, label))

    for t in turn:
        start_round_pot, pf_actions, f_actions, actions, label = t
        start_round_stacks = calculate_start_round_stacks(uid_to_seatstack, pf_actions, f_actions)
        game_state = ("t", hole_cards, flop_cards, turn_card, num_players, position, blinds, start_round_pot, start_round_stacks, actions, pf_actions, f_actions)
        finals.append((game_state, label))

    for t in river:
        start_round_pot, pf_actions, f_actions, t_actions, actions, label = t
        start_round_stacks = calculate_start_round_stacks(uid_to_seatstack, pf_actions, f_actions, t_actions)
        game_state = ("r", hole_cards, flop_cards, turn_card, river_card, num_players, position, blinds, start_round_pot, start_round_stacks, actions, pf_actions, f_actions, t_actions)
        finals.append((game_state, label))

    return finals
