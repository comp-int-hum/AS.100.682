import argparse
import re
import json
import bs4

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input", help="Input file")
    parser.add_argument("-o", "--output", dest="output", help="Output file")
    args = parser.parse_args()

    documents = []
    with open(args.input, "rt") as ifd:
        text = ifd.read()
        tree = bs4.BeautifulSoup(text, "html.parser")
        desc = tree.find("sourcedesc")
        year = desc.find("date")
        location = desc.find("pubplace")
        document = {"text" : " ".join([t.get_text() for t in tree.find_all("text")])}
        if year:
            m = re.match(r".*(\d{4}).*", year.get_text())
            if m:
                document["year"] = int(m.group(1))
        if location:
            document["location"] = location.get_text()
        documents.append(document)

    with open(args.output, "wt") as ofd:
        for document in documents:
            ofd.write(json.dumps(document) + "\n")
