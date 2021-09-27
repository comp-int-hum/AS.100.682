import argparse
import json
import csv

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input", help="Input file")
    parser.add_argument("-o", "--output", dest="output", help="Output file")
    args = parser.parse_args()

    inscriptions = []    
    with open(args.input, "rt") as ifd:
        for row in csv.DictReader(ifd):
            inscriptions.append(row)

    with open(args.output, "wt") as ofd:
        for inscription in inscriptions:
            ofd.write(json.dumps(inscription) + "\n")    
