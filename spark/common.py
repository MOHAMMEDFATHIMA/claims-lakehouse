from pyspark.sql import SparkSession


def get_spark(app: str = "claims-lakehouse") -> SparkSession:
    return (
        SparkSession.builder.appName(app)
        .config("spark.sql.shuffle.partitions", "8")  # tune for your machine
        .config("spark.sql.adaptive.enabled", "true")
        .getOrCreate()
    )
