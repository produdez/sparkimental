# Imports
import os
import pickle
import time
import pandas as pd
from IPython.display import display

import findspark

findspark.init()
findspark.find()

from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split
from pyspark.sql.types import *
from pyspark.sql.functions import udf
from pyspark.sql.functions import col


def setup_output(output_file_path_relative):
    cwd = os.getcwd()
    data_output_path = cwd + output_file_path_relative
    print("Data output path: ", data_output_path)
    return data_output_path


# Function defs
def config_n_connect_spark():
    '''
        Config and connect to running spark cluster
        - Make sure cluster is running before this -
    '''

    conf = SparkConf()
    conf.setAppName("Spakimental")
    conf.setMaster("spark://spark-master:7077")
    sc = SparkContext.getOrCreate(conf)
    print("Spark web UI link: ", sc._jsc.sc().uiWebUrl().get())  # type: ignore
    return sc

def create_data_stream(sparkContext):
    '''
        Create data stream from socket connection
    '''

    spark = SparkSession(sparkContext)
    # change this to 'INTO' if u want more info log
    spark.sparkContext.setLogLevel('WARN')

    data_stream = (
        spark.readStream.format("socket")
        .option("host", "spark-master")
        .option("port", 9999)
        .load()
    )
    return data_stream

def load_n_broadcast_model(sparkContext):
    '''
        Load model and broadcast object over all spark slave nodes
    '''
    model_rdd_pkl = sparkContext.binaryFiles("./models/SentimentIntensityAnalyzer.pkl")
    model_rdd_data = model_rdd_pkl.collect()
    _model = pickle.loads(model_rdd_data[0][1])  # local
    model = sparkContext.broadcast(_model)  # broadcasted
    return model

def process_data_stream(dStream, model):
    '''
        Predict on the streaming query:
            1. Read stream
            2. Separate lines
            3. Predict using udf (user defined function)
            4. return result
    '''
    def predict(text): 
        prediction = model.value.polarity_scores(text)["compound"]
        return float(prediction)
    
    # parallelized prediction function
    predict_udf = udf(predict, DoubleType())

    lines = dStream.select(
        explode(
            split(dStream.value, "\n")
        ).alias("text")
    )

    df = lines.select(col("text"), predict_udf(col("text")).alias("score"))
    return df




def clear_database(output_path):
    try:
        os.remove(output_path)
    except Exception as e:
        print('......')
        print(e)
        print('If the .csv file does not exist, it\'s fine, don\'t worry abt this error')
        print('......')


def merge_result(batchDF, batchID, output_path):
    print("Batch #", batchID, " - size: ", batchDF.count())
    batchDF.show()
    # save to local csv file on master node
    batchDF.toPandas().to_csv(
        output_path, mode="a", index=False, header=False
    )

def run_stream_query(query, wait_time):
    """Run and Stop a running streaming query"""

    while query.isActive:
        msg = query.status["message"]
        data_avail = query.status["isDataAvailable"]
        trigger_active = query.status["isTriggerActive"]
        if (
            not data_avail
            and not trigger_active
            and msg != "Initializing StreamExecution"
        ):
            print("Stopping query...")
            query.stop()
        time.sleep(0.5)

    # Okay wait for the stop to happen
    print("Query inactive, awaiting termination...")
    query.awaitTermination(wait_time)

def verify_n_format_result(output_path):
    df_prediction = pd.read_csv(output_path, header=None)
    df_input = pd.read_csv("./data/animal-crossing.csv")
    
    print(f'Prediction shape: {df_prediction.shape}, Input shape: {df_input.shape}')
    print("Valid result? (same input/output entries count) ", df_prediction.shape[0] == df_input.shape[0])
    
    print('Adding column name to output, final output:')
    df_final = df_prediction.rename(columns={0: "text", 1: "score"})
    display(df_final.head(3))
    df_final.to_csv(output_path, mode="w", index=False)

# Main function

def print_separator(header):
    print(f"\n----------{header}----------------------------------------------\n")

def main():
    # ENV VAR
    OUTPUT_FILE_PATH_RELATIVE = "/data/model-output.csv"

    
    # Setup input and functionalities
    print_separator('Setting Up')
    spark_context = config_n_connect_spark()
    data_stream = create_data_stream(spark_context)
    model = load_n_broadcast_model(spark_context)

    # Setup output (database)
    output_path = setup_output(OUTPUT_FILE_PATH_RELATIVE)
    clear_database(output_path)

    # Start streaming/prediction process
    print_separator('Streaming Pipeline Started')
    prediction_data_stream = process_data_stream(data_stream, model)
    query = (
        prediction_data_stream.writeStream.outputMode("append")
        .format("console")
        .queryName("stream-model-query")
        .foreachBatch(lambda batchDF, batchID: merge_result(batchDF, batchID, output_path))
        .start()
    )
    run_stream_query(query, 5000)

    # Final verifications
    print_separator('Verification')
    verify_n_format_result(output_path)

    print_separator('Done !!!')


# Entry point for script
main()
