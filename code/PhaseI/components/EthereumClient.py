import pycurl
import json
import logging
from io import BytesIO
from time import time, sleep
from threading import Thread, RLock

from config import * 

PENDING_TIMEOUT = 120 # if a transaction has been pending for more than 120 seconds, submit it again
CLIENT_TIMEOUT = 600 # if a transaction has been stuck for more than 600 seconds, restart the client

class EthereumClient:
  def encode_address(address):
    return "000000000000000000000000" + address[2:]

  def encode_uint(value):
    return format(value, "064x")

  def encode_int(value):
    return format(value & 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff, "064x")

  def __init__(self, ip, port):
self.ip = ip
    self.port = port

    self.waiting = [] # transactions which have not been submitted
    self.pending = [] # transactions which have been submitted but not yet mined
    self.lock = RLock()
    # TODO: restructure code to get rid of this ugliness...
    from Filter import Filter
    self.filter = Filter(self, self.ip, self.port)
    thread = Thread(target=self.__run)
    thread.start()
    
  def __run(self):
    logging.basicConfig(format='%(asctime)s / %(levelname)s: %(message)s', level=logging.INFO)
    while True:
      sleep(1) # wait one second
      with self.lock:
        for trans in self.pending + self.waiting:
          if time() > trans['request_time'] + CLIENT_TIMEOUT: # transaction has been stuck for a long time
            self.__restart_client()
        for trans in list(self.pending): # iterate over a copy so that we can remove items
          receipt = self.command("eth_getTransactionReceipt", params=[trans['hash']])
          if receipt is not None: # yay!
            self.pending.remove(trans)
            logging.info("Transaction {} has been mined.".format(trans['data']))
          elif time() > trans['submission_time'] + PENDING_TIMEOUT: # timeout for pending transaction
            self.pending.remove(trans)
            logging.info("Pending transaction {} has timed out, resubmitting...".format(trans['data']))
            self.__submit_trans(trans)
          # otherwise, there is nothing to do
        for trans in list(self.waiting): # iterate over a copy so that we can remove items
          self.waiting.remove(trans)
          self.__submit_trans(trans) # resubmit
          
  def __restart_client(self):
    logging.info("Restarting the client...")
    # TODO: writeme
    self.filter = Filter(self, self.ip, self.port) # recreate even filter
            
  def __submit_trans(self, trans):
    try:
      trans_hash = self.command("eth_sendTransaction", params=[{
        'from': trans['from'], 
        'data': trans['data'], 
        'to': trans['to'], 
        'gas': TRANSACTION_GAS
      }])
      if trans_hash.startswith("0x"): # this looks like a transaction hash (this check could be more thorough of course...)
        trans['hash'] = trans_hash
        trans['submission_time'] = time()
        logging.info("Transaction {} has been submitted...".format(trans['data']))
        self.pending.append(trans) # keep track of pending transactions
        return # nothing else to do
    except BaseException as e:
      print(e)
    # something went wrong
    logging.info("Failed to submit transaction {}...".format(trans['data']))
    self.waiting.append(trans) # keep track of transaction which have not been submitted

  def transaction(self, from_address, data, to_address):
    trans = {
      'request_time': time(),
      'from': from_address,
      'to': to_address,
      'data': data
    }
    with self.lock:
      self.__submit_trans(trans)

  def get_addresses(self):
    return self.command("eth_accounts")

  def command(self, method, params=[], id=1, jsonrpc="2.0", verbose=False):
    """ Method to abstract away 'curl' usage to interact with RPC of geth clients. """
    # the <ip:port> to connect to
    ipPort = str(self.ip) + ":" + str(self.port)
    # buffer to capture output
    buffer = BytesIO()
    # start building curl command to process
    try:
        c = pycurl.Curl()
        c.setopt(pycurl.URL, ipPort)
        c.setopt(pycurl.HTTPHEADER, ['Accept:application/json'])
        c.setopt(pycurl.WRITEFUNCTION, buffer.write)
        data2 = {"jsonrpc":str(jsonrpc),"method": str(method),"params":params,"id":str(id)}
        data = json.dumps(data2)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, data)
        if verbose:
            c.setopt(pycurl.VERBOSE, 1)
        #perform pycurl
        c.perform()

        # check response code (HTTP codes)
        if (c.getinfo(pycurl.RESPONSE_CODE) != 200):
            if exceptions:
                raise Exception('rpc_communication_error', 'return_code_not_200')
            return {'error':'rpc_comm_error','desc':'return_code_not_200','error_num':None}
        #close pycurl object
        c.close()
    except pycurl.error as e:
        c.close()
        errno, message = e.args
        if exceptions:
            raise Exception('rpc_communication_error', 'Error No: ' + errno + ", message: " + message)
        return {'error':'rpc_comm_error','desc':message,'error_num':errno}

    # decode result
    results = str(buffer.getvalue().decode('iso-8859-1'))
    if verbose:
        print (results)
 
    # convert result to json object for parsing
    data = json.loads(results)
    # return appropriate result
    if 'result' in data.keys():
        return data["result"]
    else:
        if 'error' in data.keys():
            if exceptions:
                raise Exception('rpc_communication_error', data)
            return data
        else:
            if exceptions:
                raise Exception('rpc_communication_error', "Unknown Error: possible method/parameter(s) were wrong and/or networking issue.")
            return {"error":"Unknown Error: possible method/parameter(s) were wrong and/or networking issue."}


