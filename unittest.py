import unittest

from .parsing.ggpoker_to_schema import (
    extract_button, get_position_name, populate_uid_to_seatstack_map,
    extract_num_players, extract_blinds, extract_hole, extract_flop,
    extract_turn, extract_river, ggpoker_to_schema
)

class TestPokerParser(unittest.TestCase):
    def setUp(self):
        self.sample_hand = """Poker Hand #TM54069188: Tournament #3035883, Bounty Hunters $5.25 Hold'em No Limit - Level6(150/300) - 2024/11/20 21:16:09
Table '7' 8-max Seat #4 is the button
Seat 1: a72064d9 (10,769 in chips)
Seat 2: 1f74a273 (12,802 in chips)
Seat 3: 76610b78 (26,640 in chips)
Seat 4: Hero (7,260 in chips)
Seat 5: 5f0ae6e2 (40,120 in chips)
Seat 6: 896411cc (32,126 in chips)
Seat 8: 41187f7f (9,955 in chips)
a72064d9: posts the ante 45
5f0ae6e2: posts the ante 45
41187f7f: posts the ante 45
Hero: posts the ante 45
76610b78: posts the ante 45
896411cc: posts the ante 45
1f74a273: posts the ante 45
5f0ae6e2: posts small blind 150
896411cc: posts big blind 300
*** HOLE CARDS ***
Dealt to a72064d9
Dealt to 1f74a273
Dealt to 76610b78
Dealt to Hero [Tc 7c]
Dealt to 5f0ae6e2
Dealt to 896411cc
Dealt to 41187f7f
41187f7f: folds
a72064d9: folds
1f74a273: folds
76610b78: raises 300 to 600
Hero: calls 600
5f0ae6e2: calls 450
896411cc: calls 300
*** FLOP *** [2s 4c Jc]
5f0ae6e2: bets 300
896411cc: raises 450 to 750
76610b78: calls 750
Hero: calls 750
5f0ae6e2: folds
*** TURN *** [2s 4c Jc] [Th]
896411cc: checks
76610b78: bets 1,738
Hero: calls 1,738
896411cc: calls 1,738
*** RIVER *** [2s 4c Jc Th] [Ad]
896411cc: checks
76610b78: checks
Hero: checks
896411cc: shows [Ac 3c] (Pair of Aces)
76610b78: shows [Ts Ks] (Pair of Tens)
Hero: shows [Tc 7c] (Pair of Tens)
*** SHOWDOWN ***
896411cc collected 10,479 from pot
*** SUMMARY ***
Total pot 10,479 | Rake 0 | Jackpot 0 | Bingo 0 | Fortune 0 | Tax 0
Board [2s 4c Jc Th Ad]
Seat 1: a72064d9 folded before Flop
Seat 2: 1f74a273 folded before Flop
Seat 3: 76610b78 showed [Ts Ks] and lost with Pair of Tens
Seat 4: Hero (button) showed [Tc 7c] and lost with Pair of Tens
Seat 5: 5f0ae6e2 (small blind) folded on the Flop
Seat 6: 896411cc (big blind) showed [Ac 3c] and won (10,479) with Pair of Aces
Seat 8: 41187f7f folded before Flop"""

    def test_extract_button(self):
        line = "Table '7' 8-max Seat #4 is the button"
        self.assertEqual(extract_button(line), 4)

    def test_get_position_name(self):
        self.assertEqual(get_position_name(8, 4, 4), "btn")
        self.assertEqual(get_position_name(8, 5, 4), "sb")
        self.assertEqual(get_position_name(8, 6, 4), "bb")

    def test_extract_num_players(self):
        self.assertEqual(extract_num_players(self.sample_hand), 7)

    def test_extract_blinds(self):
        blind_line = "896411cc: posts big blind 300"
        self.assertEqual(extract_blinds(blind_line), 300)

    def test_extract_hole(self):
        hole_line = "Dealt to Hero [Tc 7c]"
        self.assertEqual(extract_hole(hole_line), ("Tc", "7c"))

    def test_extract_flop(self):
        flop_line = "*** FLOP *** [2s 4c Jc]"
        self.assertEqual(extract_flop(flop_line), ["2s", "4c", "Jc"])

    def test_extract_turn(self):
        turn_line = "*** TURN *** [2s 4c Jc] [Th]"
        self.assertEqual(extract_turn(turn_line), "Th")

    def test_extract_river(self):
        river_line = "*** RIVER *** [2s 4c Jc Th] [Ad]"
        self.assertEqual(extract_river(river_line), "Ad")

    def test_ggpoker_to_schema(self):
        result = ggpoker_to_schema(self.sample_hand)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        for game_state, label in result:
            self.assertIn("pf", [state[0] for state, _ in result])

if __name__ == "__main__":
    unittest.main()
