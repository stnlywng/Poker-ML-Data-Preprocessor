import re

extract_button_regex = r"#(\d+)"
uid_seat_stack_regex = r"Seat (\d+): (\w+) \(([\d,]+) in chips\)"
hole_card_regex = r"Dealt to Hero \[([^\s\]]+)\s+([^\s\]]+)\]"
blinds_regex = r"(?:Level\d+\((\d+(?:,\d{3})*)/(\d+(?:,\d{3})*)\)|Hold'em No Limit \((\d+)/(\d+)\))"

posts_regex = r"(\w+):.*\b(\d+)$"
raise_regex = r"(\S+): (\w+) \d+(?:,\d+)* to (\d+(?:,\d+)*)"
normal_action_regex = r"(\S+): (\w+)(?: (\d+(?:,\d+)*))?"

# Accomodate for just *** FLOP *** and *** FIRST FLOP *** cases.
flop_pattern = r"FLOP \*\*\* \[([2-9TJQKA][hdcs]) ([2-9TJQKA][hdcs]) ([2-9TJQKA][hdcs])\]"
turn_pattern = r"TURN \*\*\* \[[2-9TJQKA][hdcs] [2-9TJQKA][hdcs] [2-9TJQKA][hdcs]\] \[([2-9TJQKA][hdcs])\]"
river_pattern = r"RIVER \*\*\* \[[2-9TJQKA][hdcs] [2-9TJQKA][hdcs] [2-9TJQKA][hdcs] [2-9TJQKA][hdcs]\] \[([2-9TJQKA][hdcs])\]"

# Table '1' 8-max Seat #6 is the button
def extract_button(line):
    match = re.search(extract_button_regex, line)
    if match:
        return int(match.group(1))  # Extract the capturing group

def get_position_name(num_players, seat, btn):
    loc = (seat - btn) % num_players
    if loc == 0 and num_players == 2:
        return "bb"
    elif loc == 0:
        return "btn"
    elif loc == 1:
        return "sb"
    elif loc == 2:
        return "bb"
    elif loc == (num_players - 1):
        return "co"
    elif loc == (num_players - 2):
        return "hj"
    elif loc == 3:
        return "utg1"
    elif loc == (num_players - 3):
        return "lj"
    elif loc == 4:
        return "utg2"
    elif loc == 5:
        return "utg3"

# Seat 3: 76610b78 (9,074 in chips)
def populate_uid_to_seatstack_map(working_map, lines, num_players, btn):
    i = 0
    while "Seat" in lines[2 + i]:
        extract = re.findall(uid_seat_stack_regex, lines[2 + i])
        if len(extract) == 0:
            for p in lines:
                print(repr(p))
        seat, uid, chip_count = extract[0]
        working_map[uid] = (get_position_name(num_players, (i + 1), btn), int(chip_count))
        i += 1

# Count by how many "in chips" are present.
def extract_num_players(round):
    num_p = re.findall(r"in chips", round)
    return len(num_p)

# posts big blind 160
def extract_blinds(round):
    match = re.search(blinds_regex, round)
    
    if match:
        # Check if it's a cash game format (groups 3 and 4) or tournament format (groups 1 and 2)
        if match.group(3) and match.group(4):
            # Cash game format
            if int(match.group(4)) == 0:
                return int(match.group(3)) * 2
            return int(match.group(4))
        else:
            # Tournament format
            return int(match.group(2).replace(',', ''))
    else:
        print(f"Warning: Could not extract blinds from: {round}")
        return None

# Dealt to Hero [2s 8h]
def extract_hole(round):
    match = re.search(hole_card_regex, round)
    if match:
        return (match.group(1), match.group(2))

def process_action_line(line, uid_to_seatstack):
    """Helper function to process action lines consistently"""
    if "raises" in line:
        t = re.findall(raise_regex, line)
    else:
        t = re.findall(normal_action_regex, line)

    if not t:
        return None

    uid, action, chip_count = t[0]
    
    # Handle empty or invalid chip counts
    if not chip_count or chip_count == "":
        chip_count = None
    else:
        try:
            chip_count = int(chip_count)
        except (ValueError, TypeError):
            chip_count = None

    if "all-in" in line:
        action += " all-in"

    seat, stack = uid_to_seatstack[uid]
    return (seat, action, chip_count)

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
                if t:
                    uid, chip_count = t[0]
                    try:
                        chip_count = int(chip_count)
                        seat, stack = uid_to_seatstack[uid]
                        current_pot += chip_count
                        preflop_actions.append((seat, "posts", chip_count))
                    except (ValueError, TypeError):
                        continue
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
                action_data = process_action_line(line, uid_to_seatstack)
                if action_data:
                    seat, action, chip_count = action_data
                    if chip_count is not None:
                        current_pot += chip_count
                    preflop.append((pf_start_pot, preflop_actions.copy(), (action, chip_count)))
                    preflop_actions.append((seat, action, chip_count))
            else:
                action_data = process_action_line(line, uid_to_seatstack)
                if action_data:
                    seat, action, chip_count = action_data
                    if chip_count is not None:
                        current_pot += chip_count
                    # else:
                    #     print("line1 - :", line)
                    #     print(f"vals: {seat} {action} {chip_count}")
                    #     print("something wrong1 - :", round)
                    preflop_actions.append((seat, action, chip_count))
                # else:
                #     print("line2 - ", line)
                #     print(f"vals: {seat} {action} {chip_count}")
                #     print("something wrong2 - ", round)
        elif current_round == "f":
            if "TURN" in line:
                current_round = "t"
                turn_start_pot = current_pot
            elif "Hero" in line:
                action_data = process_action_line(line, uid_to_seatstack)
                if action_data:
                    seat, action, chip_count = action_data
                    if chip_count is not None:
                        current_pot += chip_count
                    flop.append((flop_start_pot, preflop_actions, flop_actions.copy(), (action, chip_count)))
                    flop_actions.append((seat, action, chip_count))
            else:
                action_data = process_action_line(line, uid_to_seatstack)
                if action_data:
                    seat, action, chip_count = action_data
                    if chip_count is not None:
                        current_pot += chip_count
                    flop_actions.append((seat, action, chip_count))
        elif current_round == "t":
            if "RIVER" in line:
                current_round = "r"
                river_start_pot = current_pot
            elif "Hero" in line:
                action_data = process_action_line(line, uid_to_seatstack)
                if action_data:
                    seat, action, chip_count = action_data
                    if chip_count is not None:
                        current_pot += chip_count
                    turn.append((turn_start_pot, preflop_actions, flop_actions, turn_actions.copy(), (action, chip_count)))
                    turn_actions.append((seat, action, chip_count))
            else:
                action_data = process_action_line(line, uid_to_seatstack)
                if action_data:
                    seat, action, chip_count = action_data
                    if chip_count is not None:
                        current_pot += chip_count
                    turn_actions.append((seat, action, chip_count))
        elif current_round == "r":
            if "SHOWDOWN" in line:
                break
            elif "Hero" in line:
                action_data = process_action_line(line, uid_to_seatstack)
                if action_data:
                    seat, action, chip_count = action_data
                    if chip_count is not None:
                        current_pot += chip_count
                    river.append((river_start_pot, preflop_actions, flop_actions, turn_actions, river_actions.copy(), (action, chip_count)))
                    river_actions.append((seat, action, chip_count))
            else:
                action_data = process_action_line(line, uid_to_seatstack)
                if action_data:
                    seat, action, chip_count = action_data
                    if chip_count is not None:
                        current_pot += chip_count
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
    round = round.replace('\x00', '')
    round = convert_cash_game(round)
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


def convert_cash_game(hand_history):
    # print("Before: ", hand_history)

    # Function to convert cash amounts to chips
    def convert_to_chips(match):
        amount = match.group(1)
        if amount.startswith('$'):
            # Remove $ and convert to chips (multiply by 100)
            if amount == '$,':
                return ""
            return str(int(float(amount[1:].replace(',', '')) * 100))
        else:
            # Just remove commas from tournament numbers
            return amount.replace(',', '')

    hand_history = re.sub(r'(\$[\d,.]+|[\d,]+)', convert_to_chips, hand_history)

    # print("After: ", hand_history)

    return hand_history