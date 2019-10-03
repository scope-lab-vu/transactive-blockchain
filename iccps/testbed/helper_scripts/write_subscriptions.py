house_num = ['B0','C1','C2','B3','B4','A5','B6','B7','A8','A9','C10','A11','A12','A13','C14','A15','A16','C17','C18','B19','B20','C21','B22','B23','B24','A25','A26','C27','A28','C29']
phases = ['BS','CS','CS','BS','BS','AS','BS','BS','AS','AS','CS','AS','AS','AS','CS','AS','AS','CS','CS','BS','BS','CS','BS','BS','BS','AS','AS','CS','AS','CS']

ofile = open("subs.txt",'w')

for i in range(30):
    ostring = "subscribe \"precommit:batt_inv_F1_house_{0}.P_Out <- testAgent/batt_{1}_P_Out\";\n".format(house_num[i],i)
    ofile.write(ostring)

ofile.write("\n\n");

for i in range(30):
    ostring = "publish \"commit:batt_F1_house_{0}.state_of_charge -> batt_{1}_charge\";\n".format(house_num[i],i)
    ofile.write(ostring)

ofile.write("\n\n")

for i in range(30):
    ostring = """batt_{0}_charge:
    topic: gridlabdSimulator1/batt_{0}_charge
    default: 0\n""".format(i)
    ofile.write(ostring)


ofile.close()
