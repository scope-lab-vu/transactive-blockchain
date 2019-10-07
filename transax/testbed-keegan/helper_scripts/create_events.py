import csv
i = 0
j = 0
filename = 'step.player'
with open(filename, 'w', newline='') as csvfile:
    outwriter = csv.writer(csvfile, delimiter=' ')
    outwriter.writerow(['#time','topic','value'])

    while i < 86400e9:
            outwriter.writerow([str(int(i)), 'step', str(int(j))])
            i = i + 900e9
            j = j + 1
