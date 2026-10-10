"""Bronze: land raw CSV as-is in Parquet, adding ingestion metadata only."""
from pyspark.sql import functions as F
from common import get_spark

spark = get_spark("bronze")
raw = spark.read.option("header", True).csv("data/raw/claims.csv")  # all strings on purpose
bronze = (
    raw.withColumn("_ingested_at", F.current_timestamp())
       .withColumn("_source_file", F.input_file_name())
)
bronze.write.mode("overwrite").parquet("data/bronze/claims")
print("bronze rows:", bronze.count())
