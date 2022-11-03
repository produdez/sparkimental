# this first
import findspark

findspark.init()
findspark.find()

from pprint import pprint

# then pyspark
from pyspark import SparkContext
from pyspark.conf import SparkConf

conf = SparkConf()
conf.setAppName("Python executed")

# If you dont set default master in spark-defaults.conf 
conf.setMaster("spark://spark-master:7077")

sc = SparkContext.getOrCreate(conf)
print('Spark Config:')
pprint(sc.getConf().getAll())

nums= sc.parallelize([1,2,3,4])
squared = nums.map(lambda x: x*x).collect()
for num in squared:
    print('%i ' % (num))
