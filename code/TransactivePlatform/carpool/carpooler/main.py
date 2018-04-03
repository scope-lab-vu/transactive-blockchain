import datetime
import random
import logging
#from .context import Prosumer

#class Carpooler(Prosumer.Prosumer):
#    def __init__(self, srclat, srclng, dstlat, dstlng, prosumer_id, ip, port):
class Carpooler():
    def __init__(self,srclat,srclng,dstlat,dstlng):
        self.seats = 0
        self.providing = 0
        self.earliest = 0
        self.latest = 0
        self.pud = 1000
        self.srclat = srclat
        self.srclng = srclng
        self.dstlat = dstlat
        self.dstlng = dstlng
        self.randomSetup()
        #super(Carpooler, self).__init__(prosumer_id, ip, port)

    def run(self):
        for i in range(10):
            print ("i is %s" %i)

    def randomSetup(self):
        #--Random number of seats--
        rnd = random.random()
        if rnd >=.5:
            self.seats = 1
        elif rnd >=.2 and rnd<.5:
            self.seats = 2
        else:
            self.seats = 3
        #--Randomly assign provider state and update pick up distance if proving=1--
        rnd = random.random()
        if rnd <= .1:
            self.providing = True
            self.pud = random.uniform(1, 5)
        else:
            self.providing = False
        #--Randomly assign departure interval--
        today = datetime.datetime.combine(datetime.date.today(),datetime.time(hour=7))
        departure_times = []
        for i in range(9):
            departure_times.append(today + datetime.timedelta(minutes=15*i))
        self.earliest = random.choice(departure_times)
        index = departure_times.index(self.earliest)
        self.latest = random.choice(departure_times[index:])

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.INFO)
