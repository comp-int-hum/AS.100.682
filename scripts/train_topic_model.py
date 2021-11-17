import argparse
import json
import re
import gzip
import logging
import random
from gensim.models import LdaModel
from gensim.corpora import Dictionary
import numpy

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", dest="input", help="Input file")
    parser.add_argument("--lower_case", dest="lower_case", action="store_true", default=False)
    parser.add_argument("--keep_punctuation", dest="keep_punctuation", action="store_true", default=False)
    parser.add_argument("--topic_count", dest="topic_count", type=int)
    parser.add_argument("--max_doc_length", dest="max_doc_length", type=int)
    parser.add_argument("--passes", dest="passes", default=20, type=int)
    parser.add_argument("--iterations", dest="iterations", default=100, type=int)
    parser.add_argument("--text", dest="text")
    parser.add_argument("--translation", dest="translation", default=None)
    parser.add_argument("--output", dest="output", help="Output file")
    parser.add_argument("--random_seed", dest="random_seed", default=0, type=int, help="Random seed")
    parser.add_argument("--log_level", dest="log_level", default="INFO",
                        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"], help="Logging level")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    random.seed(args.random_seed)
    numpy.random.seed(args.random_seed)
    
    docs = []
    with gzip.open(args.input, "rt") as ifd:
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
            num_subdocs = round(0.5 + (len(text) + len(translation)) / args.max_doc_length)
            if num_subdocs == 0:
                continue
            text_per = int(len(text) / num_subdocs)
            translation_per = int(len(translation) / num_subdocs)
            for i in range(num_subdocs):
                next_doc = text[i * text_per : (i + 1) * text_per] + translation[i * translation_per : (i + 1) * translation_per]
                docs.append(next_doc)

    dictionary = Dictionary(docs)
    dictionary.filter_extremes(no_below=0.005, no_above=0.5)
    corpus = [dictionary.doc2bow(doc) for doc in docs]
    model = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=args.topic_count,
        alpha="auto",
        eta="auto",
        iterations=args.iterations,
        passes=args.passes,
        eval_every=None
    )
    model.save(args.output)
