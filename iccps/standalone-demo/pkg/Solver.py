#Solver.py
from riaps.run.comp import Component
from riaps.run.exc import PortError
import os
import subprocess
import pwd
import signal
import psutil
import logging
import requests

from time import time, sleep

import libs.config as cfg
# from libs.config import *
from libs.DoubleAuctionSolver import DoubleAuctionSolver, Offer
from libs.EthereumClient import EthereumClient
from libs.MatchingContract import MatchingContract

from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
from libs.Grafana.config import Config
from libs.Grafana.dbase import Database
import datetime



import random, string
from cgi import logfile
from pexpect.replwrap import bash




def randomword(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

class Solver(Component):
    def __init__(self,logfile):
        super(Solver, self).__init__()
        self.pid = os.getpid()

        self.logger.info("(PID %s) - starting Solver",str(self.pid))

        #Waste Space parameters
        self.delta = 1 # 1 MB #
        self.size = self.delta
        self.name = '/tmp/tmp%s' % randomword(8)
        self.logger.info(os.getcwd())

        #App Specific parameters
        self.solverID = 1
        print("solverID %s" %self.solverID)
        self.solution = None
        self.objective = 0
        self.connected =0
        self.new_offers = False
        self.solver = DoubleAuctionSolver()
        self.buying_offers = []
        self.selling_offers = []
        self.finalized = -1
        self.waiting_solutionID = False
        self.PREDICTION = False
        self.PREDICTION_WINDOW = cfg.PREDICTION_WINDOW
        self.recordTime = False
        self.interval_trades ={}
        self.solutions ={}
        self.ISID = 0
        self.DeadLine = 0.5 #seconds ideally this would be gotten from the framework API
        self.Pgain = 25#50
        self.PWMax = 50
        self.priorPW = self.PREDICTION_WINDOW


        self.logpath = '/tmp/' + logfile + '.log'
        self.killLog = 'killLog.log'
        try: os.remove(self.logpath)
        except OSError: pass
        self.fh = logging.FileHandler(self.logpath)
        self.fh.setLevel(logging.INFO)
        self.fh.setFormatter(self.logformatter)
        self.logger.addHandler(self.fh)
        self.logger.info("(PID %s) - starting Solver",str(self.pid))
        self.s = open('/dev/zero').read(1024*100-1)

        self.dbase = Database()
        self.dbase.post(now=datetime.datetime.now(), tag_dict={"object":"Solver_"+str(self.solverID)}, seriesName="PWMax", value=self.PWMax)

        self.uid = os.geteuid()
#         self.logger.info("UID: %s" %self.uid)
        self.username = pwd.getpwuid(self.uid)[0]
#         self.logger.info("USERNAME: %s" %self.username)

        self.thisProcess = psutil.Process(self.pid)
        self.cpuUtil = self.thisProcess.cpu_percent()




    # def connectGrafana(self):
    #     try :
    #         # self.db = InfluxDBClient(Config.INFLUX_DBASE_HOST,Config.INFLUX_DBASE_PORT,
    #         #                          Config.INFLUX_DBASE_USER,Config.INFLUX_DBASE_PASSWORD,
    #         #                          "solverDbase")
    #         # self.db.create_database(Config.INFLUX_DBASE_NAME)
    #         # self.db.switch_database(Config.INFLUX_DBASE_NAME)
    #         self.dbase = Database()
    #         self.dbase.post(now=datetime.datetime.now(), tag_dict={"object":"Solver_"+str(self.solverID)}, seriesName="PWMax", value=self.PWMax)
    #
    #     except requests.exceptions.ConnectionError as e:
    #         self.logger.warning("CONNECTION ERROR %s" %e)
    #         self.logger.warning("try again")
    #         self.connectGrafana()





#     def on_contractAddr(self):
#         self.logger.info("on_contractAddr()")
#
#         req = self.contractAddr.recv_pyobj()
#         self.logger.info("PID (%s) - on_contractAddr():%s",str(self.pid),str(req))
#
#         self.epoch = time() - req['time']
#         self.contract_address = req['contract']
#         self.logger.info("Contract address: " + self.contract_address)
#         self.logger.info("Setting up connection to Ethereum client...")
#         client = EthereumClient(ip=MINER, port=PORT)
#         self.account = client.accounts()[0] # use the first owned address
#         self.logger.info("Creating contract object...")
#         self.contract = MatchingContract(client, self.contract_address)
#         self.connected = 1

    def on_contractAddr(self):
        try :
            req = self.contractAddr.recv_pyobj()
            if 'contract' in req:
                self.logger.info("PID (%s) - on_contractAddr():%s",str(self.pid),str(req))
                self.epoch = time() - req['time']
                self.time_interval = int(time() - self.epoch) // cfg.INTERVAL_LENGTH

                self.solutions[self.time_interval]={}

                self.contract_address = req['contract']
                self.logger.info("Contract address: " + self.contract_address)
                self.logger.info("Setting up connection to Ethereum client...")
                client = EthereumClient(ip=cfg.MINER, port=cfg.PORT)
                self.account = client.accounts()[0] # use the first owned address
                self.logger.info("Creating contract object...")
                self.contract = MatchingContract(client, self.contract_address)
                # self.contract.registerProsumer(self.account, prosumer_id, cfg.PROSUMER_FEEDER[prosumer_id])
                self.connected = 1

            else :
                self.logger.info("reply is:%s " %req)
        except PortError as e:
            self.logger.info("on_contractAddr:port exception = %d" % e.errno)
            if e.errno in (PortError.EAGAIN,PortError.EPROTO):
                self.logger.info("on_contractAdd: port error received")



    def on_poller(self):
        now = self.poller.recv_pyobj()
        self.logger.info('PID(%s) - on_poller(): %s',str(self.pid),str(now))
        self.logger.info('update')

        if self.connected == 0 :
            self.query_contract_address()

        elif self.connected == 1 :
            self.logger.debug("Polling events...")
            #
            # if self.time_interval == 28:
            #     with open(self.killLog, 'w') as f:
            #         f.write("KILL PROCESS: %s" %time())
            #     self.logger.warning("KILL PROCESS: %s" %time())
            #     os.kill(self.pid,signal.SIGKILL)

            for event in self.contract.poll_events():
                params = event['params']
                name = event['name']
                self.logger.info("{}({}).".format(name, params))

                if (name == "BuyingOfferPosted") or (name == "SellingOfferPosted"):
                    self.new_offers = True
                    offer = Offer(params['ID'], params['prosumer'], params['startTime'], params['endTime'], params['energy'], params['value'])
                    if name == "BuyingOfferPosted":
                        self.buying_offers.append(offer)
                    else:
                        self.selling_offers.append(offer)

                elif name == "Solve":
                    interval = params['interval']
                    clear = self.solver.solve(self.buying_offers, self.selling_offers, interval)
                    self.contract.submitClearingPrice(self.account, True, interval, clear['price'])


#         bashCommand = 'quota -w %s | awk "NR==3"' %self.uid # returns row
# #             self.logger.info("bashCommand: %s" %bashCommand)
#         p1 = subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE)
#         output, error = p1.communicate()
#         quota = " ".join(output.decode().split()).split(' ')
# #         self.logger.info("QUOTA: %s" %quota)
#         space = quota[1].strip('*') # I think the asterisk shows because the value is changing.
# #         self.logger.info("SPACE: %s" %space)
#         limit = quota[3]
        now=datetime.datetime.now()

        self.cpuUtil = self.thisProcess.cpu_percent()
        self.memUsage = self.thisProcess.memory_info()
#         self.logger.info("rss: %s" %self.memUsage[0])
        # self.dbase.post(now=now , tag_dict={"disk":"space"}, seriesName="Disk", value=space)
        # self.dbase.post(now=now , tag_dict={"disk":"limit"}, seriesName="Disk", value=limit)
        self.dbase.post(now=now , tag_dict={"cpu":"use"}, seriesName="CPU", value=self.cpuUtil)
        self.dbase.post(now=now , tag_dict={"mem":"rss"}, seriesName="Mem", value=self.memUsage[0])
        self.dbase.post(now=now , tag_dict={"mem":"vms"}, seriesName="Mem", value=self.memUsage[1])


    def on_solve(self):
        self.logger.warning('Calling "on_solve" which is not doing anything. Consider removing it.')


    def handleSpcLimit(self):
        '''This is a function called by the riaps platform and should be generated if we are doing disk limits'''
        self.logger.warning('handleSpcLimit() ')
        try:
            with open(self.logpath, 'w'): #opening the log file like this truncates it.
                pass
#             os.remove(self.logpath)
#             os.remove(self.name)
#             self.size = self.delta
#             now = datetime.datetime.now()
#             self.dbase.post(now=now, tag_dict={"resource":"storage"}, seriesName="Waste", value=self.size)

        except FileNotFoundError as e:
            self.logger.info("handleSpcLimit: Remove Error = %s" % e)
            self.logger.info("file does not exist")

    def handleMemLimit(self):
        now = datetime.datetime.now()
        memNow = self.thisProcess.memory_info()
        self.logger.warning('handleMEMLimit(): %s' %str(memNow))
        if not self.PREDICTION:
            self.PWMax = self.priorPW-1
            self.dbase.post(now=now, tag_dict={"object":"Solver_"+str(self.solverID)}, seriesName="RSSNow", value=memNow[0])
            self.dbase.post(now=now, tag_dict={"object":"Solver_"+str(self.solverID)}, seriesName="PWMax", value=self.PWMax)

    def handleDeadline(self,funcName):
        self.logger.warning("handleDeadline(): %s" % funcName)
        #if self.self.Pgain += 1
        if not self.PREDICTION:
            self.PWMax = self.priorPW-1
            self.dbase.post(now=datetime.datetime.now(), tag_dict={"object":"Solver_"+str(self.solverID)}, seriesName="PWMax", value=self.PWMax)

    def handleCPULimit(self):
        self.logger.warning('handleCPULimit()')
        if not self.PREDICTION:
            self.PWMax = self.priorPW-1
            self.dbase.post(now=datetime.datetime.now(), tag_dict={"object":"Solver_"+str(self.solverID)}, seriesName="PWMax", value=self.PWMax)

    def handleNICStateChange(self, state):
        if state=="down":
            self.logger.warning("NIC is %s" % state)
            # lost connection to contract
            self.connected = 0
            # self.connectGrafana()
            self.dbase.post(now=datetime.datetime.now(), tag_dict={"object":"Solver_"+str(self.solverID)}, seriesName="PWMax", value=self.PWMax)
        else:
            self.logger.warning("NIC is %s" % state)



    def __destroy__(self):
        self.logger.info("(PID %s) - stopping Solver",str(self.pid))


    def query_contract_address(self):
        msg = {
            'request': "query_contract_address"
        }
        self.logger.info(msg)

        try:
            #self.cltReqPort.send_pyobj(msg)
            self.contractAddr.send_pyobj(msg)
        except PortError as e:
            self.logger.info("query_contract_address:send exception = %d" % e.errno)
            if e.errno in (PortError.EAGAIN,PortError.EPROTO):
                self.logger.info("query_contract_address: try again")

    def waste(self):
        self.logger.info("WASTE %s" %self.s)
#         try:
# #             cmd = 'dd if=/dev/zero of=%s bs=1M count=%d' % (self.name,self.size)
# #             res = os.system(cmd)
#             self.logger.info(self.s)
#         except:
#             self.logger.info("waste: op failed at %d" % (self.size))
#         if res == 0:
#             self.size += self.delta
#         now = datetime.datetime.now()
#         self.dbase.post(now=now, tag_dict={"resource":"storage"}, seriesName="Waste", value=self.size)
