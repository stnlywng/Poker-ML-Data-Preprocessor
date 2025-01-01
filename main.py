import argparse
from src.config import INPUT_DIRECTORY, OUTPUT_DIRECTORY
from src.schemas import preflop_schema, flop_schema, turn_schema, river_schema
from src.spark_session import get_spark_session
from src.parsing import read_files, split_by_round, ggpoker_to_schema

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process poker data and save to specified format.")
    parser.add_argument("--format", type=str, choices=["json", "parquet"], required=True,
                        help="Output format: 'json' or 'parquet'.")
    parser.add_argument("--input", type=str, required=False, default=INPUT_DIRECTORY,
                        help="Input directory (default from config).")
    parser.add_argument("--output", type=str, required=False, default=OUTPUT_DIRECTORY,
                        help="Output directory (default from config).")

    args = parser.parse_args()
    output_format = args.format
    input_dir = args.input
    output_dir = args.output

    # Initialize Spark session
    spark = get_spark_session()

    # Read and process data
    file_content_only = read_files(spark, input_dir)
    all_rounds = file_content_only.flatMap(split_by_round)
    type_and_table = all_rounds.flatMap(ggpoker_to_schema)

    preflop_data = type_and_table.filter(lambda x: x[0][0] == "pf")
    flop_data = type_and_table.filter(lambda x: x[0][0] == "f")
    turn_data = type_and_table.filter(lambda x: x[0][0] == "t")
    river_data = type_and_table.filter(lambda x: x[0][0] == "r")

    # Convert each to DataFrame with schema
    preflop_df = spark.createDataFrame(preflop_data, schema=preflop_schema)
    flop_df = spark.createDataFrame(flop_data, schema=flop_schema)
    turn_df = spark.createDataFrame(turn_data, schema=turn_schema)
    river_df = spark.createDataFrame(river_data, schema=river_schema)

    # Write DataFrames to the specified format and directories
    preflop_df.write.mode("overwrite").format(output_format).save(f"{output_dir}/preflop")
    flop_df.write.mode("overwrite").format(output_format).save(f"{output_dir}/flop")
    turn_df.write.mode("overwrite").format(output_format).save(f"{output_dir}/turn")
    river_df.write.mode("overwrite").format(output_format).save(f"{output_dir}/river")

    spark.stop()

if __name__ == "__main__":
    main()
