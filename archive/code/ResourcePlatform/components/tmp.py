import logging
logging.basicConfig(level=logging.INFO)
from ResourceAllocationLP import ResourceAllocationLP, ArchitectureJob, JobOffer, ResourceOffer

solver = ResourceAllocationLP()


unposted_ro = {}
posted_ro = {}
unposted_jo = {}
posted_jo = {}

#posted_ro[0] = ResourceOffer(params['offerID'], params['actorID'], params['architecture'], params['capCPU'], params['capRAM'], params['capStorage'], params['price'])
posted_ro[0] = ResourceOffer(0, 0, 1, 198, 389, 2708480000000, 1)

# unposted_jo[0] = JobOffer(params['offerID'], params['actorID'], params['timeLimit'], params['price'])
# unposted_jo[0].update(params['architecture'], ArchitectureJob(params['reqCPU'], params['reqRAM'], params['reqStorage'], params['imageHash']))
# posted_jo[0] = unposted_jo.pop(params['offerID'])

unposted_jo[0] = JobOffer(0, 1, 60, 10000)
unposted_jo[0].update(1, ArchitectureJob(50, 50, 166643595, 'f43fb87e58bd371076ba002383d105b6db5d9cbac73aa80ed1975b9fb6654555'))
posted_jo[0] = unposted_jo.pop(0)

print(posted_ro)
print(posted_jo)


(solution, objective) = solver.solve(posted_jo.values(), posted_ro.values())

print(f"Job allocation problem solved, objective = {objective}")
