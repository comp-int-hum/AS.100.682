import argparse
import logging
import random
import json
import gzip

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", dest="input", help="Input file")
    parser.add_argument("--field", dest="field", help="Field")
    parser.add_argument("--output", dest="output", help="Output file")
    parser.add_argument("--random_seed", dest="random_seed", default=0, type=int, help="Random seed")
    parser.add_argument("--log_level", dest="log_level", default="INFO",
                        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"], help="Logging level")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    random.seed(args.random_seed)

    unique_values = set()
    with gzip.open(args.input, "rt") as ifd:
        for line in ifd:
            doc = json.loads(line)
            values = doc.get(args.field, [])
            for value in (values if isinstance(values, list) else [values]):
                unique_values.add(value)

    with open(args.output, "wt") as ofd:
        ofd.write("\n".join(list(unique_values)))
