import zmq

c = zmq.Context()
s = c.socket(zmq.REP)
s.bind('tcp://127.0.0.1:10001')

#use recv_pyobj as it serializes the object
while True:
    msg = s.recv_pyobj()
    print (str(msg))
    s.send_pyobj(msg)
