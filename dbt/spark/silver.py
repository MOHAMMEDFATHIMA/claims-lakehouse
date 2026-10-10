"""Silver: type, clean, de-duplicate, validate. Bad rows go to quarantine, not away.

Reconciliation invariant checked at the end:
    bronze_rows == silver_rows + quarantine_rows + duplicates_removed
"""
from pyspark.sql import functions as F, Window
from common import get_spark

spark = get_spark("silver")
b = spark.read.parquet("data/bronze/claims")
bronze_rows = b.count()

typed = (
    b.withColumn("claim_id", F.col("claim_id").cast("long"))
     .withColumn("policy_id", F.col("policy_id").cast("long"))
     .withColumn("loss_date", F.to_date("loss_date", "yyyy-MM-dd"))
     .withColumn("report_date", F.to_date("report_date", "yyyy-MM-dd"))  # bad -> null
     .withColumn("incurred_amount", F.col("incurred_amount").cast("double"))
     .withColumn("paid_amount", F.col("paid_amount").cast("double"))
)

# De-duplicate on claim_id, keep the latest ingested record.
w = Window.partitionBy("claim_id").orderBy(F.col("_ingested_at").desc())
dedup = typed.withColumn("_rn", F.row_number().over(w)).filter("_rn = 1").drop("_rn")
dupes_removed = bronze_rows - dedup.count()

rules = {
    "state_present": F.col("state").isNotNull(),
    "report_date_valid": F.col("report_date").isNotNull(),
    "incurred_non_negative": F.col("incurred_amount") >= 0,
    "report_after_loss": F.col("report_date") >= F.col("loss_date"),
}
valid_expr = F.lit(True)
for cond in rules.values():
    valid_expr = valid_expr & F.coalesce(cond, F.lit(False))

silver = dedup.filter(valid_expr)
quarantine = dedup.filter(~valid_expr)

silver.write.mode("overwrite").partitionBy("line_of_business").parquet("data/silver/claims")
quarantine.write.mode("overwrite").parquet("data/silver/claims_quarantine")

s, q = silver.count(), quarantine.count()
print(f"bronze={bronze_rows:,} silver={s:,} quarantine={q:,} duplicates_removed={dupes_removed:,}")
assert bronze_rows == s + q + dupes_removed, "reconciliation failed"
print("reconciliation OK")
