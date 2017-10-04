from xlrd import open_workbook
from xlrd import xldate_as_tuple
import csv

for feeder in range(1,11):
    wb = open_workbook('Feeder'+str(feeder)+'.xlsx')
    sh = wb.sheet_by_index(0)
    t=[]
    for col in range(1,sh.ncols):
        for rx in  range(1,sh.nrows):
            t.append(xldate_as_tuple( sh.cell_value(rowx=rx,colx=0), wb.datemode) [3:] )
        print t	
        fname=sh.cell_value(rowx=0,colx=col)
        multiplier=1
        if 'Consumer' in fname:
            multiplier=-1
        csvfile=open('prosumer_'+str(feeder)+str(col).zfill(2)+ '.csv','wb')
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['startTime','endTime','energy'])       
        for cx in  range(1,sh.nrows):
            value=sh.cell_value(rowx=cx,colx=col)*multiplier
            spamwriter.writerow([cx,cx,value])
        csvfile.close()
    
    