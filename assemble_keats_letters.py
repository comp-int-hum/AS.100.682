import argparse
import re
import json
import bs4

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input", help="Input file")
    parser.add_argument("-o", "--output", dest="output", help="Output file")
    args = parser.parse_args()

    letters = []
    with open(args.input, "rt") as ifd:
        for text in ifd.read().split("<h2><a")[1:-1]:
            text = "<html><h2><a" + text + "</html>"
            s = bs4.BeautifulSoup(text, "html.parser")
            recipient = re.match(r"^[CLXIV]+\.?.TO (.*?)\.?$", s.find("h2").get_text()).group(1)
            info_text = s.find("p", {"class":"right"}).get_text()
            content = []
            for p in s.find_all("p"):
                if p.get("class") != "right":
                    content.append(p.get_text())
            letter = {
                "recipient" : recipient,
                "text" : "\n".join(content),
            }
            m = re.match(r".*(\d{4}).*", info_text, re.S)
            if m:
                letter["year"] = int(m.group(1))
            letters.append(letter)

    with open(args.output, "wt") as ofd:
        for letter in letters:
            ofd.write(json.dumps(letter) + "\n")

