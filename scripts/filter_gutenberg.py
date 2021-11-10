import argparse
import csv
import gzip
import json
import re
import logging
import random


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--index", dest="index", help="Gutenberg index file")
    parser.add_argument("--output", dest="output", help="Output file")
    parser.add_argument("--authors", dest="authors", nargs="*", help="Regexes for authors to include")
    parser.add_argument("--title", dest="title", nargs="*", help="Regexes for titles to include")
    parser.add_argument("--subjects", dest="subjects", nargs="*", help="Regexes for subjects to include")
    parser.add_argument("--years", dest="years", nargs="*", help="Years, or year-ranges, to include")
    parser.add_argument("--languages", dest="languages", nargs="*", help="Language codes to include")
    parser.add_argument("--nauthors", dest="nauthors", nargs="*", help="Regexes for authors to exclude")
    parser.add_argument("--ntitle", dest="ntitle", nargs="*", help="Regexes for titles to exclude")
    parser.add_argument("--nsubjects", dest="nsubjects", nargs="*", help="Regexes for subjects to exclude")
    parser.add_argument("--nyears", dest="nyears", nargs="*", help="Years, or year-ranges, to exclude")
    parser.add_argument("--nlanguages", dest="nlanguages", nargs="*", help="Language codes to exclude")
    parser.add_argument("--random_seed", dest="random_seed", default=0, type=int, help="Random seed")
    parser.add_argument("--log_level", dest="log_level", default="INFO",
                        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"], help="Logging level")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    random.seed(args.random_seed)
    
    patterns = {}
    for field in ["subjects", "authors", "title"]:
        pos = getattr(args, field)
        neg = getattr(args, "n" + field)
        patterns[field.title()] = (
            re.compile(".*(?:{}).*".format("|".join(pos)), re.I) if pos else None,
            re.compile(".*(?:{}).*".format("|".join(neg)), re.I) if neg else None,
        )
    def year_set(ys):
        if len(ys) == 1:
            return [ys[0]]
        else:
            return list(range(ys[0], ys[1] + 1))
        
    year_sets = (
        set(sum([year_set(list(map(int, s.split("-")))) for s in args.years], [])) if args.years else None,
        set(sum([year_set(list(map(int, s.split("-")))) for s in args.nyears], [])) if args.nyears else None,
    )

    items = []
    with gzip.open(args.index, "rt") as ifd:
        for row in csv.DictReader(ifd, delimiter="\t"):
            keep = True
            years = set([int(x) for x in re.findall(r"\d+", row.get("Authors", ""))])

            if year_sets[0]:
                keep = keep and (len(year_sets[0] & years) > 0)
            if year_sets[1]:
                keep = keep and (not len(year_sets[1] & years) > 0)

            if args.languages:
                keep = keep and (row["Language"] in args.languages)
            if args.nlanguages:
                keep = keep and (not row["Language"] in args.nlanguages)

            for k, (pos, neg) in patterns.items():
                if pos:
                    keep = keep and (pos.match(row[k]))
                if neg:
                    keep = keep and (not neg.match(row[k]))
            # Text#, Type, Issued, Title, Language, Authors, Subjects, LoCC, Bookshelves

            if keep:
                items.append(row)

    with gzip.open(args.output, "wt") as ofd:
        for item in items:
            ofd.write(json.dumps(item) + "\n")
