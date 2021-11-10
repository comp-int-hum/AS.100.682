import argparse
from glob import glob
import os.path
import gzip
import json
import logging
import random
from bs4 import BeautifulSoup

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--perseus", dest="perseus", help="Path to Perseus project data")
    parser.add_argument("--output", dest="output", help="Output file")
    parser.add_argument("--random_seed", dest="random_seed", default=0, type=int, help="Random seed")
    parser.add_argument("--log_level", dest="log_level", default="INFO",
                        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"], help="Logging level")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    random.seed(args.random_seed)

    with gzip.open(args.output, "wt") as ofd:
        for lat_fname in glob(os.path.join(args.perseus, "*", "opensource", "*lat.xml")):
            document = {}
            with open(lat_fname, "rt") as ifd:
                tree = BeautifulSoup(ifd, "xml")
                titleStmt_elem = tree.find("titleStmt")
                if titleStmt_elem:
                    title_elem = titleStmt_elem.find("title")
                    document["title"] = title_elem.get_text() if title_elem else "Unknown"
                    author_elem = titleStmt_elem.find("author")
                    document["author"] = author_elem.get_text() if author_elem else "Unknown"
                else:
                    document["title"] = "Unknown"
                    document["author"] = "Unknown"                    
                    
                logging.info("Processing file '%s'", document["title"])
                document["text"] = "\n".join([t.get_text() for t in tree.find_all("text")])
            eng_fname = lat_fname.replace("lat.xml", "eng.xml")
            if os.path.exists(eng_fname):
                with open(eng_fname, "rt") as ifd:
                    tree = BeautifulSoup(ifd, "xml")
                    document["translation"] = "\n".join([t.get_text() for t in tree.find_all("text")])
            ofd.write(json.dumps(document) + "\n")
        
