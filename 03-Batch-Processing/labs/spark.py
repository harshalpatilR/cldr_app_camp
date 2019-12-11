#!/usr/bin/python

from pyspark.sql import SparkSession
import logging
import sys
#from pyspark.sql import HiveContext

# Build the sparkSession and set application name from config file
spark = SparkSession.builder.appName("HarshalExample").getOrCreate()
# Setting LogLevel for the sparkContext from config file
spark.sparkContext.setLogLevel("INFO")
# Creating Pyarrow file system object to perform HDFS operations
table_name = "harshal_galaxy.measurments"



#HiveContext.setConf("hive.exec.dynamic.partition", "true")
#HiveContext.setConf("hive.exec.dynamic.partition.mode", "nonstrict")

cleanup_query = """
DROP TABLE IF EXISTS harshal_galaxy.merged_spark
"""

merge_query="""CREATE TABLE harshal_galaxy.merged_spark
(
detector_name STRING,
country STRING,
latitude DECIMAL(15,6),
longitude DECIMAL(15,6),
astrophysicist_name STRING,
year_of_birth INT,
nationality STRING,
galaxy_name STRING,
galaxy_type STRING,
distance_ly DECIMAL(10,5),
absolute_magnitude DECIMAL(10,5),
apparent_magnitude DECIMAL(10,5),
galaxy_group STRING,
measurement_id STRING,
measurement_time INT,
amplitude_1 DECIMAL(15,12),
amplitude_2 DECIMAL(15,12),
amplitude_3 DECIMAL(15,12)
)
PARTITIONED BY (detector_id INT)
STORED AS PARQUET"""


insert_query="""
SELECT
detectors.detector_name,
detectors.country,
cast(detectors.latitude as DECIMAL(38,5)),
cast(detectors.longitude as DECIMAL(38,5)),
astrophysicists.astrophysicist_name,
cast(astrophysicists.year_of_birth as INT),
astrophysicists.nationality,
galaxies.galaxy_name,
galaxies.galaxy_type,
cast(galaxies.distance_ly as DECIMAL(10,5)),
cast(galaxies.absolute_magnitude as DECIMAL(10,5)),
cast(galaxies.apparent_magnitude as DECIMAL(10,5)),
galaxies.galaxy_group,
measurements.measurement_id,
cast(measurements.measurement_time as INT),
cast(measurements.amplitude_1 as DECIMAL(15,12)),
cast(measurements.amplitude_2 as DECIMAL(15,12)),
cast(measurements.amplitude_3 as DECIMAL(15,12)),
cast(detectors.detector_id as INT)
FROM harshal_galaxy.measurments as measurements
join harshal_galaxy.detectors ON measurements.detector_id = detectors.detector_id
join harshal_galaxy.astrophysicists ON measurements.astrophysicist_id = astrophysicists.astrophysicist_id
join harshal_galaxy.galaxies ON measurements.galaxy_id = galaxies.galaxy_id
WHERE detectors.detector_id is not null
"""




query = f"select * from {table_name} limit 10"

buff = spark.sql(cleanup_query)
buff = spark.sql(merge_query)
buff = spark.sql(insert_query)
buff.show(10)
buff.write.mode("overwrite").saveAsTable("harshal_galaxy.merged_spark")

