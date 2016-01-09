import csv
import sys
import json
import json_formatter

if __name__ == "__main__":
    metInfo = {}

    #load the table as a dictionary
    with open('node_information.csv', 'rb') as csvfile:
        tablereader = csv.reader(csvfile)
        for row in tablereader:
            try:
                ind=int(row[1])
            except ValueError:
                ind=0
            if ind > 0:
                metInfo[row[1]]={}
                metInfo[row[1]]['name']=row[0]
                metInfo[row[1]]['KEGGID']=row[2]
                metInfo[row[1]]['fullname']=row[3]
                metInfo[row[1]]['centralcarbon']= int(row[9])
                metInfo[row[1]]['aminoacid']= int(row[8])
                metInfo[row[1]]['nucleotide']= int(row[7])
                metInfo[row[1]]['cofactor']= int(row[6])
                metInfo[row[1]]['fattyacid']= int(row[5])
                metInfo[row[1]]['other']= int(row[4])

    with open(sys.argv[-1]) as in_file:
        network = json.load(in_file)


    for key in network['nodes'].keys():
        if metInfo[key]['centralcarbon']:
            network['nodes'][key]['color']='red'
        elif metInfo[key]['aminoacid']:
            network['nodes'][key]['color']='green'
        elif metInfo[key]['nucleotide']:
            network['nodes'][key]['color']='blue'
        elif metInfo[key]['cofactor']:
            network['nodes'][key]['color']='yellow'
        elif metInfo[key]['fattyacid']:
            network['nodes'][key]['color']='purple'
        elif metInfo[key]['other']:
            network['nodes'][key]['color']='gray'


    print json_formatter.dumps(network)
