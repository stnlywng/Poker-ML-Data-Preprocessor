def read_files(spark, input_directory):
    whole_input_files = spark.sparkContext.wholeTextFiles(input_directory)
    return whole_input_files.map(lambda file: file[1])
