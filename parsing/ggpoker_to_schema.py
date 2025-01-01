import re
from binascii import Error


# def extract_seat_data(hand_text):
#     seats = {}
#     seat_lines = re.findall(r"Seat (\d+): (.+?) \(([\d,]+) in chips\)", hand_text)
#     for seat_num, player_id, chips in seat_lines:
#         seats[int(seat_num)] = {
#             "player_id": player_id.strip(),
#             "chips": int(chips.replace(",", "")),
#         }
#     return seats
#
# def get_ante(hand_text):
#     antes = re.findall(r"ante (\d+)", hand_text)
#     if len(antes):
#         return len(antes) * int(antes[0])
#     else:
#         return 0
#
# def get_hero_position(seats, hand_text):
#     # Find the SB—loop through array with
#     small_blind_id = re.findall(r"(.+?): posts small", hand_text)
#     cur_position = 1
#     for seat in seats:
#         seat_num, name, _ = seat
#
# # Helper function to parse actions
# def parse_actions(hand_text, hero_seat):
#     actions = []
#     action_lines = re.findall(r"(\S+): (posts|bets|raises|calls|checks|folds).*", hand_text)
#     for player_id, action in action_lines:
#         actions.append({"player_id": player_id, "action": action})
#     return actions

# Table '1' 8-max Seat #6 is the button
def extract_button(line):
    match = re.search(r"#(\d+)", line)
    if match:
        return int(match.group(1))  # Extract the capturing group
    # else:
    #     raise ValueError(f"Unable to extract button for: {line}")

def get_position_name(num_players, seat, btn):
    loc = (seat - btn) % num_players
    if loc == 0:
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

def populate_uid_to_seatstack_map(working_map, lines, num_players, btn):
    i = 0
    while "Seat" in lines[2 + i]:
        extract = re.findall(r"Seat (\d+): (\w+) \(([\d,]+) in chips\)", lines[2 + i])
        seat, uid, chip_count = extract[0]
        chip_count = chip_count.replace(',', '')
        working_map[uid] = (get_position_name(num_players, int(seat), btn), int(chip_count))
        i += 1

def extract_num_players(round):
    num_p = re.findall(r"in chips", round)
    return len(num_p)

def extract_blinds(round):
    # posts big blind 160
    match = re.search(r"posts big blind (\d+)", round)
    j = match.group(1)
    if match:
        return int(match.group(1))

def extract_hole(round):
    # "Dealt to Hero [3d 2d]"
    match = re.search(r"Dealt to Hero \[([^\s\]]+)\s+([^\s\]]+)\]", round)
    if match:
        return (match.group(1), match.group(2))

# (start_pot_size, [actions so far], label)
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
                t = re.findall(r"(\w+):.*\b(\d+)$", line)
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
                    t = re.findall(r"(\S+): (\w+) \d+(?:,\d+)* to (\d+(?:,\d+)*)", line)
                else:
                    t = re.findall(r"(\S+): (\w+)(?: (\d+(?:,\d+)*))?", line)

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
                    t = re.findall(r"(\S+): (\w+) \d+(?:,\d+)* to (\d+(?:,\d+)*)", line)
                else:
                    t = re.findall(r"(\S+): (\w+)(?: (\d+(?:,\d+)*))?", line)

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
                    t = re.findall(r"(\S+): (\w+) \d+(?:,\d+)* to (\d+(?:,\d+)*)", line)
                else:
                    t = re.findall(r"(\S+): (\w+)(?: (\d+(?:,\d+)*))?", line)

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
                    t = re.findall(r"(\S+): (\w+) \d+(?:,\d+)* to (\d+(?:,\d+)*)", line)
                else:
                    t = re.findall(r"(\S+): (\w+)(?: (\d+(?:,\d+)*))?", line)

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
                    t = re.findall(r"(\S+): (\w+) \d+(?:,\d+)* to (\d+(?:,\d+)*)", line)
                else:
                    t = re.findall(r"(\S+): (\w+)(?: (\d+(?:,\d+)*))?", line)

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
                    t = re.findall(r"(\S+): (\w+) \d+(?:,\d+)* to (\d+(?:,\d+)*)", line)
                else:
                    t = re.findall(r"(\S+): (\w+)(?: (\d+(?:,\d+)*))?", line)

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
                    t = re.findall(r"(\S+): (\w+) \d+(?:,\d+)* to (\d+(?:,\d+)*)", line)
                else:
                    t = re.findall(r"(\S+): (\w+)(?: (\d+(?:,\d+)*))?", line)

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
                    t = re.findall(r"(\S+): (\w+) \d+(?:,\d+)* to (\d+(?:,\d+)*)", line)
                else:
                    t = re.findall(r"(\S+): (\w+)(?: (\d+(?:,\d+)*))?", line)

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

    # print("\n \n PREFLOP: ")
    # print(preflop)
    # print("\n \n FLOP: ")
    # print(flop)
    # print("\n \nTURN: ")
    # print(turn)
    # print("\n \nRIVER: ")
    # print(river)

    return preflop, flop, turn, river

def extract_flop(round):
    flop_pattern = r"\*\*\* FLOP \*\*\* \[([2-9TJQKA][hdcs]) ([2-9TJQKA][hdcs]) ([2-9TJQKA][hdcs])\]"
    match = re.search(flop_pattern, round)
    if match:
        return [match.group(1), match.group(2), match.group(3)]
    else:
        return None

def extract_turn(round):
    # "Dealt to Hero [3d 2d]"
    turn_pattern = r"\*\*\* TURN \*\*\* \[[2-9TJQKA][hdcs] [2-9TJQKA][hdcs] [2-9TJQKA][hdcs]\] \[([2-9TJQKA][hdcs])\]"
    match = re.search(turn_pattern, round)
    if match:
        return match.group(1)
    else:
        return None

def extract_river(round):
    river_pattern = r"\*\*\* RIVER \*\*\* \[[2-9TJQKA][hdcs] [2-9TJQKA][hdcs] [2-9TJQKA][hdcs] [2-9TJQKA][hdcs]\] \[([2-9TJQKA][hdcs])\]"
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
                tracker[seat] += count
    if flop_actions:
        for seat, action, count in flop_actions:
            if count:
                tracker[seat] += count
    if turn_actions:
        for seat, action, count in turn_actions:
            if count:
                tracker[seat] += count

    return list(tracker.items())


def ggpoker_to_schema(round):
    #lines = round.splitLines()
    lines = round.split("\n")

    # needed for all rounds (pre-flop, flop, turn, river)
    btn = extract_button(lines[1])
    num_players = extract_num_players(round)

    uid_to_seatstack = {}  # ("6539a8dd", ("btn", 3600))
    try:
        populate_uid_to_seatstack_map(uid_to_seatstack, lines, num_players, btn)
    except:
        print(round)
        raise Exception("oh noo" + round + "that was the round")


    position, c = uid_to_seatstack["Hero"]
    blinds = extract_blinds(round)
    hole_cards = extract_hole(round)
    flop_cards = extract_flop(round)
    turn_card = extract_turn(round)
    river_card = extract_river(round)

    # [actions prior, money prior, label]
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

    # result = [lst for lst in [pf_final, flop_final, turn_final, river_final] if lst]
    # return result if result else None  # Return None if all are empty
    return finals


ggpoker_to_schema("""Poker Hand #TM54497943: Tournament #3062152, Bounty Hunters $3.15 Hold'em No Limit - Level7(175/350) - 2024/11/26 19:20:02
Table '2' 8-max Seat #7 is the button
Seat 1: Hero (9,850 in chips)
Seat 2: 1faf558b (20,200 in chips)
Seat 3: d3d4c296 (8,275 in chips)
Seat 4: 1a21cb70 (16,104 in chips)
Seat 5: 491b1bd4 (19,519 in chips)
Seat 6: 6fccf0f0 (10,000 in chips)
Seat 7: 208437c3 (14,680 in chips)
Seat 8: 79852ed6 (12,847 in chips)
1a21cb70: posts the ante 50
79852ed6: posts the ante 50
1faf558b: posts the ante 50
491b1bd4: posts the ante 50
Hero: posts the ante 50
6fccf0f0: posts the ante 50
d3d4c296: posts the ante 50
208437c3: posts the ante 50
79852ed6: posts small blind 175
Hero: posts big blind 350
*** HOLE CARDS ***
Dealt to Hero [7c 7d]
Dealt to 1faf558b 
Dealt to d3d4c296 
Dealt to 1a21cb70 
Dealt to 491b1bd4 
Dealt to 6fccf0f0 
Dealt to 208437c3 
Dealt to 79852ed6 
1faf558b: folds
d3d4c296: calls 350
1a21cb70: folds
491b1bd4: folds
6fccf0f0: folds
208437c3: raises 1,050 to 1,400
79852ed6: calls 1,225
Hero: calls 1,050
d3d4c296: folds
*** FLOP *** [9d 9c 8s]
79852ed6: checks
Hero: checks
208437c3: bets 1,980
79852ed6: calls 1,980
Hero: raises 6,420 to 8,400 and is all-in
208437c3: raises 4,830 to 13,230 and is all-in
79852ed6: folds
Uncalled bet (4,830) returned to 208437c3
208437c3: shows [Kc 9s] (Three Nines)
Hero: shows [7c 7d] (Pair of Nines and Pair of Sevens)
*** TURN *** [9d 9c 8s] [Qd]
*** RIVER *** [9d 9c 8s Qd] [5h]
*** SHOWDOWN ***
208437c3 collected 23,730 from pot
*** SUMMARY ***
Total pot 23,730 | Rake 0 | Jackpot 0 | Bingo 0 | Fortune 0 | Tax 0
Board [9d 9c 8s Qd 5h]
Seat 1: Hero (big blind) showed [7c 7d] and lost with Pair of Nines and Pair of Sevens
Seat 2: 1faf558b folded before Flop
Seat 3: d3d4c296 folded before Flop
Seat 4: 1a21cb70 folded before Flop
Seat 5: 491b1bd4 folded before Flop
Seat 6: 6fccf0f0 folded before Flop
Seat 7: 208437c3 (button) showed [Kc 9s] and won (23,730) with Three Nines
Seat 8: 79852ed6 (small blind) folded on the Flop""")

# def test_get_position_name():
#     # num_players = 2
#     print(f"num_players {2}, spot {1}, btn {1} -> {get_position_name(2, 1, 1)}")
#     print(f"num_players {2}, spot {2}, btn {1} -> {get_position_name(2, 2, 1)}")
#
#     # num_players = 3
#     print(f"num_players {3}, spot {1}, btn {1} -> {get_position_name(3, 1, 1)}")
#     print(f"num_players {3}, spot {2}, btn {2} -> {get_position_name(3, 2, 2)}")
#     print(f"num_players {3}, spot {3}, btn {1} -> {get_position_name(3, 3, 1)}")
#
#     # num_players = 4
#     print(f"num_players {4}, spot {1}, btn {1} -> {get_position_name(4, 1, 1)}")
#     print(f"num_players {4}, spot {2}, btn {1} -> {get_position_name(4, 2, 1)}")
#     print(f"num_players {4}, spot {3}, btn {3} -> {get_position_name(4, 3, 3)}")
#     print(f"num_players {4}, spot {4}, btn {1} -> {get_position_name(4, 4, 1)}")
#
#     # num_players = 5
#     print(f"num_players {5}, spot {1}, btn {1} -> {get_position_name(5, 1, 1)}")
#     print(f"num_players {5}, spot {2}, btn {1} -> {get_position_name(5, 2, 1)}")
#     print(f"num_players {5}, spot {3}, btn {1} -> {get_position_name(5, 3, 1)}")
#     print(f"num_players {5}, spot {4}, btn {1} -> {get_position_name(5, 4, 1)}")
#     print(f"num_players {5}, spot {5}, btn {1} -> {get_position_name(5, 5, 1)}")
#
#     # num_players = 6
#     print(f"num_players {6}, spot {1}, btn {1} -> {get_position_name(6, 1, 1)}")
#     print(f"num_players {6}, spot {2}, btn {1} -> {get_position_name(6, 2, 1)}")
#     print(f"num_players {6}, spot {3}, btn {1} -> {get_position_name(6, 3, 1)}")
#     print(f"num_players {6}, spot {4}, btn {1} -> {get_position_name(6, 4, 1)}")
#     print(f"num_players {6}, spot {5}, btn {4} -> {get_position_name(6, 5, 4)}")
#     print(f"num_players {6}, spot {6}, btn {1} -> {get_position_name(6, 6, 1)}")
#
#     # num_players = 7
#     print(f"num_players {7}, spot {1}, btn {1} -> {get_position_name(7, 1, 1)}")
#     print(f"num_players {7}, spot {2}, btn {3} -> {get_position_name(7, 2, 2)}")
#     print(f"num_players {7}, spot {3}, btn {5} -> {get_position_name(7, 3, 5)}")
#     print(f"num_players {7}, spot {4}, btn {7} -> {get_position_name(7, 4, 7)}")
#     print(f"num_players {7}, spot {5}, btn {1} -> {get_position_name(7, 5, 1)}")
#     print(f"num_players {7}, spot {6}, btn {2} -> {get_position_name(7, 6, 2)}")
#     print(f"num_players {7}, spot {7}, btn {1} -> {get_position_name(7, 7, 1)}")
#
#     # num_players = 8
#     print(f"num_players {8}, spot {1}, btn {1} -> {get_position_name(8, 1, 1)}")
#     print(f"num_players {8}, spot {2}, btn {1} -> {get_position_name(8, 2, 1)}")
#     print(f"num_players {8}, spot {3}, btn {1} -> {get_position_name(8, 3, 1)}")
#     print(f"num_players {8}, spot {4}, btn {1} -> {get_position_name(8, 4, 1)}")
#     print(f"num_players {8}, spot {5}, btn {1} -> {get_position_name(8, 5, 1)}")
#     print(f"num_players {8}, spot {6}, btn {1} -> {get_position_name(8, 6, 1)}")
#     print(f"num_players {8}, spot {7}, btn {1} -> {get_position_name(8, 7, 1)}")
#     print(f"num_players {8}, spot {8}, btn {1} -> {get_position_name(8, 8, 1)}")
#
#     # num_players = 9
#     print(f"num_players {9}, spot {1}, btn {1} -> {get_position_name(9, 1, 1)}")
#     print(f"num_players {9}, spot {2}, btn {1} -> {get_position_name(9, 2, 1)}")
#     print(f"num_players {9}, spot {3}, btn {3} -> {get_position_name(9, 3, 3)}")
#     print(f"num_players {9}, spot {4}, btn {1} -> {get_position_name(9, 4, 1)}")
#     print(f"num_players {9}, spot {5}, btn {1} -> {get_position_name(9, 5, 1)}")
#     print(f"num_players {9}, spot {6}, btn {2} -> {get_position_name(9, 6, 2)}")
#     print(f"num_players {9}, spot {7}, btn {1} -> {get_position_name(9, 7, 1)}")
#     print(f"num_players {9}, spot {8}, btn {8} -> {get_position_name(9, 8, 8)}")
#     print(f"num_players {9}, spot {9}, btn {1} -> {get_position_name(9, 9, 1)}")
#
# test_get_position_name()
