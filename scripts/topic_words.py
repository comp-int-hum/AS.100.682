import argparse
import gzip
import logging
import random
import csv
from gensim.models import LdaModel
from gensim.corpora import Dictionary


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", dest="model", help="Model file")
    parser.add_argument("--output", dest="output", help="Output file")
    parser.add_argument("--random_seed", dest="random_seed", default=0, type=int, help="Random seed")
    parser.add_argument("--log_level", dest="log_level", default="INFO",
                        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"], help="Logging level")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    random.seed(args.random_seed)    
    
    model = LdaModel.load(args.model)
    topics = model.show_topics(num_topics=model.num_topics, formatted=False)

    with open(args.output, "wt") as ofd:
        c = csv.writer(ofd, delimiter="\t")
        for topic_num, topic_terms in topics:
            c.writerow([w for w, _ in topic_terms])
