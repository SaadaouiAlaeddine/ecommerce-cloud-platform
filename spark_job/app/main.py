# simple_word_count.py
from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder \
    .appName("SimpleWordCount") \
    .getOrCreate()

# Create some sample text data
text_data = [
    "Hello Spark",
    "This is a simple example",
    "Learning Spark is fun",
    "Apache Spark for beginners",
    "This is a basic word count example"
]

# Create a DataFrame
df = spark.createDataFrame([(text,) for text in text_data], ["text"])

# Show the data
print("Original text data:")
df.show(truncate=False)

# Split the text into words and count occurrences
word_counts = df.selectExpr("explode(split(text, ' ')) as word") \
    .groupBy("word") \
    .count() \
    .orderBy("count", ascending=False)

# Show word count results
print("\nWord count results:")
word_counts.show(20)

# Print total number of words
total_words = word_counts.agg({"count": "sum"}).collect()[0][0]
print(f"\nTotal number of words: {total_words}")

# Stop the Spark session
spark.stop()