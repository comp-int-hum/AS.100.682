import argparse
import gzip
import random
import logging
import csv
import json
import re
from gensim.models import LdaModel
from gensim.corpora import Dictionary


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", dest="input", help="Input file")
    parser.add_argument("--model", dest="model", help="Model file")
    parser.add_argument("--text", dest="text")
    parser.add_argument("--translation", dest="translation", default=None)
    parser.add_argument("--lower_case", dest="lower_case", action="store_true", default=False)
    parser.add_argument("--keep_punctuation", dest="keep_punctuation", action="store_true", default=False)
    parser.add_argument("--output", dest="output", help="Output file")
    parser.add_argument("--random_seed", dest="random_seed", default=0, type=int, help="Random seed")
    parser.add_argument("--log_level", dest="log_level", default="INFO",
                        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"], help="Logging level")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    random.seed(args.random_seed)
    
    model = LdaModel.load(args.model)
    docs = []
    
    with gzip.open(args.input, "rt") as ifd, gzip.open(args.output, "wt") as ofd:
        for line in ifd:
            item = json.loads(line)
            text = item.get(args.text, "")
            text = text.lower() if args.lower_case else text
            text = text if args.keep_punctuation else re.sub(r"[^a-zA-Z0-9\s]", "", text)
            text = text.split()
            translation = item.get(args.translation, "")
            translation = translation.lower() if args.lower_case else translation
            translation = translation if args.keep_punctuation else re.sub(r"[^a-zA-Z0-9\s]", "", translation)
            translation = translation.split()
            topics = {k : float(v) for k, v in model.get_document_topics(model.id2word.doc2bow(text + translation))}
            labeled = dict([(k, v) for k, v in item.items() if k not in [args.text, args.translation]] + [("topics", topics)])
            docs.append(labeled)
            
    with gzip.open(args.output, "wt") as ofd:
        ofd.write(json.dumps(docs))
