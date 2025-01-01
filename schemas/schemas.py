from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType

player_stack_schema = StructType([
    StructField("player", StringType(), True),
    StructField("stack", IntegerType(), True)
])

action_schema = StructType([
    StructField("player", StringType(), True),
    StructField("action", StringType(), True),
    StructField("amount", IntegerType(), True)
])

label_schema = StructType([
    StructField("action", StringType(), True),
    StructField("size", IntegerType(), True)
])

preflop_gamestate_schema = StructType([
    StructField("round", StringType(), True),
    StructField("hole_cards", ArrayType(StringType()), True),
    StructField("num_players", IntegerType(), True),
    StructField("position", StringType(), True),
    StructField("blinds", IntegerType(), True),
    StructField("start_round_pot", IntegerType(), True),
    StructField("start_round_stacks", ArrayType(player_stack_schema), True),
    StructField("actions_in_round", ArrayType(action_schema), True)
])

preflop_schema = StructType([
    StructField("preflop_gamestate", preflop_gamestate_schema, True),
    StructField("label", label_schema, True)
])

flop_gamestate_schema = StructType([
    StructField("round", StringType(), True),
    StructField("hole_cards", ArrayType(StringType()), True),
    StructField("flop_cards", ArrayType(StringType()), True),
    StructField("num_players", IntegerType(), True),
    StructField("position", StringType(), True),
    StructField("blinds", IntegerType(), True),
    StructField("start_round_pot", IntegerType(), True),
    StructField("start_round_stacks", ArrayType(player_stack_schema), True),
    StructField("actions_in_round", ArrayType(action_schema), True),
    StructField("preflop_actions", ArrayType(action_schema), True)
])

flop_schema = StructType([
    StructField("flop_gamestate", flop_gamestate_schema, True),
    StructField("label", label_schema, True)
])

turn_gamestate_schema = StructType([
    StructField("round", StringType(), True),
    StructField("hole_cards", ArrayType(StringType()), True),
    StructField("flop_cards", ArrayType(StringType()), True),
    StructField("turn_card", StringType(), True),
    StructField("num_players", IntegerType(), True),
    StructField("position", StringType(), True),
    StructField("blinds", IntegerType(), True),
    StructField("start_round_pot", IntegerType(), True),
    StructField("start_round_stacks", ArrayType(player_stack_schema), True),
    StructField("actions_in_round", ArrayType(action_schema), True),
    StructField("preflop_actions", ArrayType(action_schema), True),
    StructField("flop_actions", ArrayType(action_schema), True)
])

turn_schema = StructType([
    StructField("turn_gamestate", turn_gamestate_schema, True),
    StructField("label", label_schema, True)
])

river_gamestate_schema = StructType([
    StructField("round", StringType(), True),
    StructField("hole_cards", ArrayType(StringType()), True),
    StructField("flop_cards", ArrayType(StringType()), True),
    StructField("turn_card", StringType(), True),
    StructField("river_card", StringType(), True),
    StructField("num_players", IntegerType(), True),
    StructField("position", StringType(), True),
    StructField("blinds", IntegerType(), True),
    StructField("start_round_pot", IntegerType(), True),
    StructField("start_round_stacks", ArrayType(player_stack_schema), True),
    StructField("actions_in_round", ArrayType(action_schema), True),
    StructField("preflop_actions", ArrayType(action_schema), True),
    StructField("flop_actions", ArrayType(action_schema), True),
    StructField("turn_actions", ArrayType(action_schema), True)
])

river_schema = StructType([
    StructField("river_gamestate", river_gamestate_schema, True),
    StructField("label", label_schema, True)
])
