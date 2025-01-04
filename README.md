# Poker Hand History Organization and Preperation for ML with Spark (PokerCraft). 

## Table of Contents
1. [Project Overview](#project-overview)
2. [Sample Usage](#Sample-Usage)
3. [Technologies Used](#technologies-used)
4. [Setup and Installation](#setup-and-installation)

---

## Project Overview
Designed to parse and prepare Poker Hand History (No Limit Holdem) for Machine Learning, making use of PySpark to process and structure data via a distributed system.
The project is tailored for applications in data analysis, game simulation, and AI model training.

Flexible and extensible for processing poker game data across multiple stages of a game (Preflop, Flop, Turn, River). 


- **Structured Data with Defined Schemas**:
  - GGPoker Hand History to JSON or PARQUET formats.
  - Predefined schemas for every poker round (Preflop, Flop, Turn, River).
- **Scalable Data Processing**:
  - Integration with PySpark for high-performance distributed data processing.
  - Able to process all files in a given directory—easy and quick use.

---


## Sample Usage
```bash
spark-submit main.py --format [json/parquet] --input ./path/to/data --output ./path/to/output
```

### Input - (PokerCraft Hand History)
In this example, Hero has a single action in each stage of the game. Ran with spark-submit main.py --format json --input ./data --output ./output
```text
Poker Hand #TM54069188: Tournament #3035883, Bounty Hunters $5.25 Hold'em No Limit - Level6(150/300) - 2024/11/20 21:16:09
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
Seat 8: 41187f7f folded before Flop
```
### Output - (JSON or Parquet)
**PREFLOP:**
```json
{
  "preflop_gamestate": {
    "round": "pf",
    "hole_cards": ["Tc", "7c"],
    "num_players": 7,
    "position": "btn",
    "blinds": 300,
    "start_round_pot": 765,
    "start_round_stacks": [
      { "player": "lj", "stack": 10769 },
      { "player": "hj", "stack": 12802 },
      { "player": "co", "stack": 26640 },
      { "player": "btn", "stack": 7260 },
      { "player": "sb", "stack": 40120 },
      { "player": "bb", "stack": 32126 },
      { "player": "utg1", "stack": 9955 }
    ],
    "actions_in_round": [
      { "player": "lj", "action": "posts", "amount": 45 },
      { "player": "sb", "action": "posts", "amount": 45 },
      { "player": "utg1", "action": "posts", "amount": 45 },
      { "player": "btn", "action": "posts", "amount": 45 },
      { "player": "co", "action": "posts", "amount": 45 },
      { "player": "bb", "action": "posts", "amount": 45 },
      { "player": "hj", "action": "posts", "amount": 45 },
      { "player": "sb", "action": "posts", "amount": 150 },
      { "player": "bb", "action": "posts", "amount": 300 },
      { "player": "utg1", "action": "folds" },
      { "player": "lj", "action": "folds" },
      { "player": "hj", "action": "folds" },
      { "player": "co", "action": "raises", "amount": 600 }
    ]
  },
  "label": {
    "action": "calls",
    "size": 600
  }
}
```

**FLOP:**
```json
{
  "flop_gamestate": {
    "round": "f",
    "hole_cards": ["Tc", "7c"],
    "flop_cards": ["2s", "4c", "Jc"],
    "num_players": 7,
    "position": "btn",
    "blinds": 300,
    "start_round_pot": 2715,
    "start_round_stacks": [
      { "player": "lj", "stack": 10724 },
      { "player": "hj", "stack": 12757 },
      { "player": "co", "stack": 25995 },
      { "player": "btn", "stack": 6615 },
      { "player": "sb", "stack": 39475 },
      { "player": "bb", "stack": 31481 },
      { "player": "utg1", "stack": 9910 }
    ],
    "actions_in_round": [
      { "player": "sb", "action": "bets", "amount": 300 },
      { "player": "bb", "action": "raises", "amount": 750 },
      { "player": "co", "action": "calls", "amount": 750 }
    ],
    "preflop_actions": [
      { "player": "lj", "action": "posts", "amount": 45 },
      { "player": "sb", "action": "posts", "amount": 45 },
      { "player": "utg1", "action": "posts", "amount": 45 },
      { "player": "btn", "action": "posts", "amount": 45 },
      { "player": "co", "action": "posts", "amount": 45 },
      { "player": "bb", "action": "posts", "amount": 45 },
      { "player": "hj", "action": "posts", "amount": 45 },
      { "player": "sb", "action": "posts", "amount": 150 },
      { "player": "bb", "action": "posts", "amount": 300 },
      { "player": "utg1", "action": "folds" },
      { "player": "lj", "action": "folds" },
      { "player": "hj", "action": "folds" },
      { "player": "co", "action": "raises", "amount": 600 },
      { "player": "btn", "action": "calls", "amount": 600 },
      { "player": "sb", "action": "calls", "amount": 450 },
      { "player": "bb", "action": "calls", "amount": 300 }
    ]
  },
  "label": {
    "action": "calls",
    "size": 750
  }
}
```

**TURN:**
```json
{
  "turn_gamestate": {
    "round": "t",
    "hole_cards": ["Tc", "7c"],
    "flop_cards": ["2s", "4c", "Jc"],
    "turn_card": "Th",
    "num_players": 7,
    "position": "btn",
    "blinds": 300,
    "start_round_pot": 5265,
    "start_round_stacks": [
      { "player": "lj", "stack": 10724 },
      { "player": "hj", "stack": 12757 },
      { "player": "co", "stack": 25245 },
      { "player": "btn", "stack": 5865 },
      { "player": "sb", "stack": 39175 },
      { "player": "bb", "stack": 30731 },
      { "player": "utg1", "stack": 9910 }
    ],
    "actions_in_round": [
      { "player": "bb", "action": "checks" },
      { "player": "co", "action": "bets", "amount": 1738 }
    ],
    "preflop_actions": [ ... ],
    "flop_actions": [ ... ]
  },
  "label": {
    "action": "calls",
    "size": 1738
  }
}
```

**RIVER:**
```json
{
  "river_gamestate": {
    "round": "r",
    "hole_cards": ["Tc", "7c"],
    "flop_cards": ["2s", "4c", "Jc"],
    "turn_card": "Th",
    "river_card": "Ad",
    "num_players": 7,
    "position": "btn",
    "blinds": 300,
    "start_round_pot": 10479,
    "start_round_stacks": [
      { "player": "lj", "stack": 10724 },
      { "player": "hj", "stack": 12757 },
      { "player": "co", "stack": 23507 },
      { "player": "btn", "stack": 4127 },
      { "player": "sb", "stack": 39175 },
      { "player": "bb", "stack": 28993 },
      { "player": "utg1", "stack": 9910 }
    ],
    "actions_in_round": [
      { "player": "bb", "action": "checks" },
      { "player": "co", "action": "checks" }
    ],
    "preflop_actions": [ ... ],
    "flop_actions": [ ... ],
    "turn_actions": [ ... ]
  },
  "label": {
    "action": "checks"
  }
}
```

---


## Technologies Used
- **PySpark**: Core technology for distributed data processing.
- **Python 3.8+**: Primary programming language, Version for Spark Support.
- **Git**: Version control for collaborative development.

[//]: # (---)

[//]: # ()
[//]: # (## Setup and Installation)

[//]: # ()
[//]: # (### Prerequisites)

[//]: # (- Python 3.8 or later.)

[//]: # (- Apache Spark installed and configured.)

[//]: # (- Java 8+ installed.)

[//]: # (- pipenv or virtualenv for managing dependencies &#40;optional&#41;.)

[//]: # ()
[//]: # (### Installation Steps)

[//]: # (1. **Clone the Repository**:)

[//]: # (   ```bash)

[//]: # (   git clone https://github.com/your-repo/pyspark-poker-project.git)

[//]: # (   cd pyspark-poker-project)

[//]: # (   ```)

[//]: # ()
[//]: # (2. **Set up a Python Environment**:)

[//]: # (   Using `pipenv`:)

[//]: # (   ```bash)

[//]: # (   pipenv install)

[//]: # (   pipenv shell)

[//]: # (   ```)

[//]: # (   Or using `virtualenv`:)

[//]: # (   ```bash)

[//]: # (   python3 -m venv env)

[//]: # (   source env/bin/activate)

[//]: # (   pip install -r requirements.txt)

[//]: # (   ```)

[//]: # ()
[//]: # (3. **Configure Spark**:)

[//]: # (   Ensure `SPARK_HOME` is set and add Spark binaries to your PATH.)

[//]: # ()
[//]: # (4. **Run Tests**:)

[//]: # (   Verify installation with tests:)

[//]: # (   ```bash)

[//]: # (   python -m unittest discover tests)

[//]: # (   ```)
