from src.config import INPUT_DIRECTORY, OUTPUT_DIRECTORY
from src.schemas import preflop_schema
from src.schemas.schemas import flop_schema, turn_schema, river_schema
from src.spark_session import get_spark_session
from src.parsing import read_files, split_by_round, ggpoker_to_schema

def main():
    spark = get_spark_session()

    file_content_only = read_files(spark, INPUT_DIRECTORY)
    all_rounds = file_content_only.flatMap(split_by_round)
    type_and_table = all_rounds.flatMap(ggpoker_to_schema)

    print(type_and_table.take(1))

    preflop_data = type_and_table.filter(lambda x: x[0][0] == "pf")
    flop_data = type_and_table.filter(lambda x: x[0][0] == "f")
    turn_data = type_and_table.filter(lambda x: x[0][0] == "t")
    river_data = type_and_table.filter(lambda x: x[0][0] == "r")

    # Convert each to DataFrame with schema
    preflop_df = spark.createDataFrame(preflop_data, schema=preflop_schema)
    flop_df = spark.createDataFrame(flop_data, schema=flop_schema)
    turn_df = spark.createDataFrame(turn_data, schema=turn_schema)
    river_df = spark.createDataFrame(river_data, schema=river_schema)

    preflop_df.show(truncate=False)
    flop_df.show(truncate=False)
    turn_df.show(truncate=False)
    river_df.show(truncate=False)

    # Write DataFrames to Parquet
    preflop_df.write.mode("overwrite").json("output/preflop") #.parquet("output/preflop")
    flop_df.write.mode("overwrite").json("output/flop")#.parquet("output/flop")
    turn_df.write.mode("overwrite").json("output/turn")#.parquet("output/turn")
    river_df.write.mode("overwrite").json("output/river")#.parquet("output/river")

    spark.stop()

if __name__ == "__main__":
    main()
