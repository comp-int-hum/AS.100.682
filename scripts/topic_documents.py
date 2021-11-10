import argparse
import csv
import json
import gzip
import logging
import random

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", dest="input", help="Input file")
    parser.add_argument("--output", dest="output", help="Output file")
    parser.add_argument("--display_field", dest="display_field", help="Display field")
    parser.add_argument("--random_seed", dest="random_seed", default=0, type=int, help="Random seed")
    parser.add_argument("--log_level", dest="log_level", default="INFO",
                        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"], help="Logging level")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    random.seed(args.random_seed)    

    docs = []
    topics = set()
    with gzip.open(args.input, "rt") as ifd:
        for doc in json.loads(ifd.read()):
            doc["topics"] = {int(k) : v for k, v in doc["topics"].items()}
            for t in doc["topics"].keys():
                topics.add(t)
            docs.append(doc)

    with open(args.output, "wt") as ofd:
        for t in range(max(topics) + 1):
            ofd.write("\t".join([str(x.get(args.display_field, "Unknown")) for x in sorted(docs, key=lambda x : -x["topics"].get(t, 0.0))[0:10] if x["topics"].get(t, 0.0) > 0.0]) + "\n")
        
