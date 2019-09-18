#!/usr/bin/python

##############################################################################
#
# Command line tool for setting up blockchain test hosts with correct config
#
# @Author Michael A. Walker
# @Date   2017-06-20
#
##############################################################################

# imports
import sys, getopt
from subprocess import call


def main(argv):
   commandHelp = "host-config.py -c <prosumerCount> -d <dsoCount> -p <prosumerRpcStartPort> -m <minerCount>"
   prosumerCount= ''
   dsoCount= ''
   prosumerRpcStartPort= ''
   minerCount= ''

   try:
      opts, args = getopt.getopt(argv,"hc:d:p:m",["prosumerCount=","dsoCount=","prosumerRpcStartPort=","minerCount="])
   except getopt.GetoptError:
      print commandHelp
      sys.exit(2)
   if len(opts) <= 0:
      print commandHelp
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print commandHelp
         sys.exit()
      elif opt in ("-c", "--prosumerCount"):
         prosumerCount = arg
      elif opt in ("-d", "--dsoCount"):
         dsoCount = arg
      elif opt in ("-p", "--prosumerRpcStartPort"):
         prosumerRpcStartPort = arg
      elif opt in ("-m", "--minerCount"):
         minerCount = arg

   print 'prosumer count is "', prosumerCount
   print 'dso count is "', dsoCount
   print 'prosumer rpc start port is "', prosumerRpcStartPort
   print 'miner count is "', minerCount

   for i in range(1,int(prosumerCount)):
      call(["cp", "-R", '/home/ubuntu/ethereum/custom/data/', '/home/ubuntu/ethereum/custom/data' + str(i) + '/' ])

if __name__ == "__main__":
   main(sys.argv[1:])
