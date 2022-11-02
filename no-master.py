# this first
import findspark

findspark.init()
findspark.find()


import pyspark
from pyspark import SparkContext
from pyspark.conf import SparkConf
from pprint import pprint
conf = SparkConf()
conf.setAppName("Python executed")
sc = SparkContext.getOrCreate(conf)

print('Spark Config:')
pprint(sc.getConf().getAll())

nums= sc.parallelize([1,2,3,4])
squared = nums.map(lambda x: x*x).collect()
for num in squared:
    print('%i ' % (num))

from pyspark.sql import Row, SQLContext

sqlContext = SQLContext(sc)

list_p = [('John',19),('Smith',29),('Adam',35),('Henry',50)]
rdd = sc.parallelize(list_p)
ppl =rdd.map(lambda x: Row(name=x[0], age=int(x[1])))
DF_ppl = sqlContext.createDataFrame(ppl)
DF_ppl.printSchema()
