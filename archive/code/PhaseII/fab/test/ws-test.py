#! /usr/bin/python3

from websocket import create_connection
ws = create_connection("ws://127.0.0.1:9012")
print("Sending 'Hello, World'...")
ws.send("{\"jsonrpc\":\"2.0\",\"method\":\"rpc_modules\",\"params\":[],\"id\":1}")
print("Sent")
print("Receiving...")
result =  ws.recv()
print("Received '%s'" % result)
ws.close()
