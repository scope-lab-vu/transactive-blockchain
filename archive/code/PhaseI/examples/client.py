import zmq

c = zmq.Context()
s = c.socket(zmq.REQ)
s.connect('tcp://127.0.0.1:10001')

def echo(msg):
    s.send_pyobj(msg)
    msg2 = s.recv_pyobj()
    return msg2

class Client(object):
    pass

client = Client()
client.echo = echo

print(client.echo("hello"))
