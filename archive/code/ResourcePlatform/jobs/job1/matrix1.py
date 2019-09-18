#python script to generate random matrices from the number of rows and columns entered by the user.

import random
from random import randint
from pymongo import MongoClient
import time
import logging
#Rows and columns of each matrix, this is the variable we need to vary
m1=5
m2=5
n1=5
n2=5

list=[]
mylist=[]


def main():
	begin=time.clock()
	try:
		client = MongoClient("172.19.0.1", 27017)
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

	#Inserting the matrix into mongodb
	record = collection.insert_one({ "name": "sram40","qty":list})



if __name__=="__main__":
	main()
