from xlrd import open_workbook
from xlrd import xldate_as_tuple
import csv,numpy
BATTERY=True

for feeder in range(1,12):
    wb = open_workbook('Feeder'+str(feeder)+'.xlsx')
    sh = wb.sheet_by_index(0)
    t=[]
    for col in range(1,sh.ncols):
        for rx in  range(1,sh.nrows):
            t.append(xldate_as_tuple( sh.cell_value(rowx=rx,colx=0), wb.datemode) [3:] )        
        fname=sh.cell_value(rowx=0,colx=col)
        multiplier=1
        if 'Consumer' not in fname and 'Producer' not in fname:
          continue
        if 'Consumer' in fname:
            multiplier=-1            
        csvfile=open('prosumer_'+str(feeder)+str(col).zfill(2)+ '.csv','wb')
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['startTime','endTime','energy'])       
        usingBattery=False
        BatteryCharge=0  
        nextBatteryUsageCx=0
        BatteryEntries={}        
        for cx in  range(1,sh.nrows):
            value=sh.cell_value(rowx=cx,colx=col)*multiplier   
            if value==0:
                continue
            if multiplier==1 and cx > nextBatteryUsageCx and BATTERY :
                if not usingBattery:
                    i=numpy.random.uniform(1,10)
                #print i
                if i<=2:
                    usingBattery=True
                if usingBattery:
                    BatteryCharge2=BatteryCharge+value
                    BatteryEntries[cx]=value                    
                    if BatteryCharge2>14:
                        BatteryCharge=14
                        value=BatteryCharge2-14
                        usingBattery=False                        
                        print BatteryCharge
                        for entry in BatteryEntries.keys():
                             spamwriter.writerow([entry,cx+5,BatteryEntries[entry]])
                        spamwriter.writerow([cx,cx,round(value,2)])                                                
                        nextBatteryUsageCx=cx+5
                        BatteryCharge=0
                        BatteryEntries={}
                        continue 
                    else:
                      BatteryCharge= BatteryCharge2
                      continue
            spamwriter.writerow([cx,cx,value])
        csvfile.close()
    
    