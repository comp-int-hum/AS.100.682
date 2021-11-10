import argparse
import re
import gzip
from io import BytesIO
from zipfile import ZipFile
import os.path
import logging
import json
import requests

headers = {
    "user-agent" : "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6",
    "referer" : "http://www.google.com",
}

url = "http://aleph.gutenberg.org/{0}/{1}/{1}-h.zip"

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--records", dest="records", help="File of Gutenberg records")
    parser.add_argument("--output", dest="output", help="Output file")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    
    with gzip.open(args.records, "rt") as ifd, ZipFile(args.output, "w") as ofd:
        for line in ifd:
            item = json.loads(line)
            eid = item["Text#"]
            logging.info("Processing item called '%s' with id '%s'", item["Title"], eid)
            specific_url = url.format("/".join(eid[0:-1]), eid)
            data = requests.get(specific_url, timeout=10, headers=headers)
            if data.status_code != 200:
                data = requests.get(specific_url.replace("-h.zip", ".zip"), timeout=10)
            if data.status_code != 200:
                logging.info("Skipping because could not resolve URL")
                continue
            try:
                with ZipFile(BytesIO(data.content)) as zfd:
                    for member_name in zfd.namelist():
                        _, ext = os.path.splitext(member_name)
                        if re.match(r".*\.[a-z]+$", member_name) and not ext in [".png", ".jpg"]:
                            content = zfd.read(member_name)
                            new_member_name = "files/{}".format(os.path.basename(member_name))
                            ofd.writestr(new_member_name, content)
            except:
                logging.info("Skipping because the zip file appears malformed")
