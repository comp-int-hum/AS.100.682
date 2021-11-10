import argparse
import gzip
import os.path
import logging
import random
import json
import re
from zipfile import ZipFile
from bs4 import BeautifulSoup

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--downloaded", dest="downloaded", help="Path to downloaded Gutenberg documents")
    parser.add_argument("--records", dest="records", help="File of Gutenberg records")
    parser.add_argument("--output", dest="output", help="Output file")
    parser.add_argument("--random_seed", dest="random_seed", default=0, type=int, help="Random seed")
    parser.add_argument("--log_level", dest="log_level", default="INFO",
                        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"], help="Logging level")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    random.seed(args.random_seed)
    
    records = {}
    with gzip.open(args.records, "rt") as ifd, gzip.open(args.output, "wt") as ofd:
        for line in ifd:
            record = json.loads(line)
            records[int(record["Text#"])] = record
    
    with ZipFile(args.downloaded, "r") as zfd, gzip.open(args.output, "wt") as ofd:
        for member_name in zfd.namelist():
            m = re.match(r"files/(\d+)-h.htm", member_name)
            if m and int(m.group(1)) in records:
                logging.info("Processing file '%s'", member_name)
                text_num = int(m.group(1))
                record = records.get(text_num, {})
                raw_html = zfd.read(member_name).decode("utf-8", errors="replace")
                item = {
                    "text_id" : text_num,
                    "title" : record.get("Title", "unknown"),
                    "language" : record.get("Language", "unknown"),
                    "text" : BeautifulSoup(raw_html, "html.parser").get_text(),
                }
                editors, translators, authors = [], [], []
                for person in record["Authors"].split(";"):
                    if re.match(r".*editor.*", person, re.I) and "editor" not in item:
                        item["editor"] = person
                    elif re.match(r".*translator.*", person, re.I) and "translator" not in item:
                        item["translator"] = person
                    elif "author" not in item:
                        item["author"] = person

                for subject in record["Subjects"].split("--"):
                    item["Subject: {}".format(subject)] = True

                    
                for shelf in record["Bookshelves"].split(";"):
                    item["Shelf: {}".format(shelf)] = True

                for m in re.finditer(r"(\d+)", record["Authors"]):
                    year = int(m.group(1))
                    if year > 1700 and year < 1900 and "year" not in item:
                        item["year"] = year
                
                ofd.write(json.dumps(item) + "\n")
