#python script to generate the actual job of 500 x 500 multiplication.
#Here the hash of the matrix multiplication result is stored in mongodb.
#Using Hashlib to produce sha256 of the matrix resultant

import random
from random import randint
from pymongo import MongoClient
import time
import logging
import hashlib

m1=500
m2=500
n1=500
n2=500

list=[]
mylist=[]


def main():
	#begin=time.clock()
	try:
		client = MongoClient("localhost", 27017)
		print("Connected successfully!!!")
	except:
		print("Could not connect to MongoDB")

	db = client.matrixdb
	collection = db.matrix_collection

	#First Matrix
	a = [[random.random() for col in range(n1)] for row in range(m1)]
	for i in range(m1):

		for j in range(n1):
			a[i][j]=1
			#print(a[i][j],end= " ")
		#print()

	#Second matrix
	b = [[random.random() for col in range(n2)] for row in range(m2)]
	for i in range(m2):
		for j in range(n2):
			b[i][j]=1
			#print(b[i][j],end= " ")
		#print()
	#print("\n")

	#Resultant matrix calculator
	c=[[random.random()for col in range(n2)]for row in range(m1)]
	if (n1==m2):
		for i in range(m1):
			for j in range(n2):
				c[i][j]=0
			for k in range(n1):
				c[i][j]+=a[i][k]*b[k][j]
				#print(c[i][j],end= " ")
				list.append(c[i][j])
			#print()
	#else:
		#print("Multiplication not possible\n")

	#Hashing using sha256
	mylist=hashlib.sha256(str(list).encode())
	hex_dig = mylist.hexdigest()
	print(hex_dig)

	#Inserting the matrix into mongodb
	record = collection.insert_one({ "name": "sram40","qty":hex_dig})
	#end=time.clock()
#	print("Total execution time {}".format(end-begin))


if __name__=="__main__":
	main()
