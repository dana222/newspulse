from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
spark = (SparkSession.builder.appName("NewsPulse").master("local[*]").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")
schema = StructType([
    StructField("source",StringType(),True),
    StructField("title",StringType(),True),
    StructField("url",StringType(),True),
    StructField("ts",TimestampType(),True),
])
stream = spark.readStream.schema(schema).json("data/incoming")
q_src = (stream.groupBy("source").count()
    .writeStream.outputMode("complete").format("memory").queryName("by_source").start())
q_win = (stream.withWatermark("ts","2 hours")
    .groupBy(F.window("ts","1 hour")).count()
    .writeStream.outputMode("append").format("memory").queryName("by_window").start())
STOPWORDS = {"the","a","an","and","or","in","is","to","of","for","on","at","by","with","this","that","was","are","be","as","it","have","has","will","from","not","but","its","been","more"}
q_words = (stream
    .select(F.explode(F.split(F.lower(F.col("title")),r"[^a-z]+")).alias("word"))
    .filter(F.length("word")>3)
    .filter(~F.col("word").isin(STOPWORDS))
    .groupBy("word").count()
    .writeStream.outputMode("complete").format("memory").queryName("top_words").start())
spark.streams.awaitAnyTermination()
