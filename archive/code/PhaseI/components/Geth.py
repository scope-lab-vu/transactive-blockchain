import pycurl
import json
from io import BytesIO

class Geth:
  def encode_address(address):
    return "000000000000000000000000" + address[2:]

  def encode_uint(value):
    return format(value, "064x")

  def encode_int(value):
    return format(value & 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff, "064x")

  def __init__(self, ip, port):
    # TODO do validation of input 
    self.ip = ip
    self.port = port
    
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

  def get_addresses(self):
    return self.command("eth_accounts")


