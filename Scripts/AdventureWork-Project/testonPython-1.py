# %% [markdown]
# #### Start
# ``` mermaid
# flowchart LR
#     st(["Start"]) --> stp1("Variable Update") --> stp2[("connect Iceberg warehouse")] -->stp3{"check list of table"}
# --showing-->stp4(["End"])
# --not showing-->stp1
# 
# ```

# %%
from pyspark.sql import SparkSession

LOCAL_WAREHOUSE_PATH = "/data/data_files/iceberg/iceberg_warehouse"
CATALOG_NAME = "local"

spark = SparkSession.builder \
    .appName("Iceberg Setup") \
    .config(f"spark.sql.catalog.{CATALOG_NAME}", "org.apache.iceberg.spark.SparkCatalog") \
    .config(f"spark.sql.catalog.{CATALOG_NAME}.catalog-impl", "org.apache.iceberg.hadoop.HadoopCatalog") \
    .config(f"spark.sql.catalog.{CATALOG_NAME}.warehouse", f"file:///{LOCAL_WAREHOUSE_PATH}") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .getOrCreate()

spark.catalog.setCurrentCatalog("local")


tables = spark.catalog.listTables("db")
tables
for table in tables:
    print(table)

# print([i for i in 'data' if i not in 'ai']) 

# %%
# from pyspark.sql import functions as sf

# news_articles = spark.table("local.db.news_articles").filter(sf.col("partition_date") == "20251101")
# news_articles.show(10, truncate=False)

# %%
# from pyspark.sql import functions as sf

# news_source = spark.table("local.db.news_articles") \
#     .select("source") \
#     .distinct()

# news_source_count = spark.table("local.db.news_articles") \
#     .groupBy("source")\
#     .count()

# news_source.show(10, truncate=False)
# news_source_count.show(10, truncate=False)

# %% [markdown]
# #### Joining
# ``` mermaid
# erDiagram
#     direction LR
#     Person ||--o{ Customer : "may be customer"
#     Customer ||--o{ SalesOrderHeader : "can place orders"
#     Person {
#         string BusinessEntityID PK "Key Column"
#         string FirstName
#         string MiddleName
#         string LastName
#     }
#     Customer {
#         string CustomerID PK "Key Column"
#         string PersonID FK "Key Column"
#         string AccountNumber        "Customer_Account_Number"
#     }
#     SalesOrderHeader {
#         string CustomerID FK "Key Column"
#         string AccountNumber        "Sales_Account_Number"
#         number    SubTotal        "Fact Column"
#         number    TaxAmt           "Fact Column"
#         number    Freight           "Fact Column"
#         number    TotalDue        "Fact Column"
#     }
# 
# 
# 
# ```

# %%
from pyspark.sql import SparkSession
from pyspark.sql import functions as sf


SalesOrderHeader = spark.table("local.Sales.SalesOrderHeader").alias("soh") # CustomerID
Customer = spark.table("local.Sales.Customer").alias("cust") # CustomerID, PersonID
Person = spark.table("local.Person.Person").alias("prsn") # BusinessEntityID

df_all_join = SalesOrderHeader\
    .join(Customer, sf.col("soh.CustomerID") == sf.col("cust.CustomerID"), "inner")\
    .join(Person, sf.col("cust.CustomerID") == sf.col("prsn.BusinessEntityID"), "inner")

df_all = df_all_join\
    .select(sf.to_date(sf.col("soh.OrderDate"),"M/d/yyyy").alias("OrderDate"), "soh.SalesOrderNumber", 
            sf.col("soh.AccountNumber").alias("Sales_Account_Number"), 
            "soh.SubTotal", "soh.TaxAmt", "soh.Freight", "soh.TotalDue", 
            sf.col("cust.AccountNumber").alias("Customer_Account_Number"), 
            "prsn.FirstName", "prsn.MiddleName", "prsn.LastName")

# %% [markdown]
# #### Next Process
# ```mermaid
# flowchart LR
# 
# start[("all data")] --"Customer Account Number"
# --> STP1("Applied Ranking")
# -->SPT2>"get Max Value Out"]
# -->SPT3[\"Filter Max Value"/]
# -->SPT4[["get Customer Account Number Out"]]
# 
# ```

# %%
from pyspark.sql import functions as sf
from pyspark.sql import window as swf

win_spec = swf.Window.partitionBy("Customer_Account_Number").orderBy("TotalDue")

df_numbered = df_all.withColumn("rowNumber",sf.row_number().over(win_spec))

maxValue = df_numbered.agg(sf.max("rowNumber")).collect()[0][0]

df_numbered_filter = df_numbered.filter(sf.col("rowNumber") == maxValue)

# Customer_Account_Number = df_numbered_filter.select("Customer_Account_Number").collect[0]


df_numbered_filter.show(10, truncate=False)


Customer_Account_Number = df_numbered_filter.select("Customer_Account_Number").collect()
print(Customer_Account_Number)
for row in Customer_Account_Number:
    print(row["Customer_Account_Number"])

Customer_Account_Number = [row[0] for row in df_numbered_filter.select("Customer_Account_Number").collect()]
Customer_Account_Number

# %% [markdown]
# #### Next Process
# ```mermaid
# flowchart LR
# 
# start[("all data")] --"Filter Customer Account Number"
# --> STP1[/"Grouped and Sum"\]
# ```

# %%
from pyspark.sql import functions as sf


# Step 1: Filter for the desired customers

df_filtered = df_all.filter(sf.col("Customer_Account_Number").isin(Customer_Account_Number))


# Step 2: Create a "yyyyMM" column from OrderDate
df_with_month = df_filtered.withColumn("OrderMonth", sf.date_format("OrderDate", "yyyyMM"))


# %%
# Step 3.1: Group and aggregate
df_grouped = df_with_month.groupBy(
    "OrderMonth",
    "Customer_Account_Number",
    "FirstName",
    "MiddleName",
    "LastName"
).agg(
    sf.sum("SubTotal").alias("Total_SubTotal"),
    sf.sum("TaxAmt").alias("Total_TaxAmt"),
    sf.sum("Freight").alias("Total_Freight"),
    sf.sum("TotalDue").alias("Total_TotalDue")
)

# Step 4.1: Display the result
df_grouped.orderBy("OrderMonth").show(truncate=False)




# %%
# Step 3.2: Group and aggregate
df_cube = df_with_month.cube(
    "OrderMonth",
    "Customer_Account_Number",
    "FirstName",
    "MiddleName",
    "LastName"
).agg(
    sf.sum("SubTotal").alias("Total_SubTotal"),
    sf.sum("TaxAmt").alias("Total_TaxAmt"),
    sf.sum("Freight").alias("Total_Freight"),
    sf.sum("TotalDue").alias("Total_TotalDue")
)

# Step 3.2: Display the result
df_cube.orderBy(sf.desc("OrderMonth")).show(truncate=False)


# %%

# Step 3.3: Group and aggregate
df_rollup = df_with_month.rollup(
    "OrderMonth",
    "Customer_Account_Number",
    "FirstName",
    "MiddleName",
    "LastName"
).agg(
    sf.sum("SubTotal").alias("Total_SubTotal"),
    sf.sum("TaxAmt").alias("Total_TaxAmt"),
    sf.sum("Freight").alias("Total_Freight"),
    sf.sum("TotalDue").alias("Total_TotalDue")
)

# Step 3.3: Display the result
df_rollup.orderBy(sf.desc("OrderMonth")).show(truncate=False)

# %%
spark.stop()


