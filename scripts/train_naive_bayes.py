import argparse
import pickle
import json
import re
import gzip
import logging
import random
import numpy
import pandas
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import KFold
from sklearn.metrics import f1_score

#from sklearn.
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", dest="input", help="Input file")
    parser.add_argument("--lower_case", dest="lower_case", action="store_true", default=False)
    parser.add_argument("--keep_punctuation", dest="keep_punctuation", action="store_true", default=False)
    parser.add_argument("--num_splits", dest="num_splits", type=int, default=3)
    parser.add_argument("--max_doc_length", dest="max_doc_length", type=int, default=1000)
    parser.add_argument("--target_field", dest="target_field", required=True, help="Field to try and classify")
    parser.add_argument("--text", dest="text", default="text")
    parser.add_argument("--translation", dest="translation", default="translation")
    parser.add_argument("--output", dest="output", help="Output file")
    parser.add_argument("--random_seed", dest="random_seed", default=0, type=int, help="Random seed")
    parser.add_argument("--log_level", dest="log_level", default="INFO",
                        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"], help="Logging level")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    random.seed(args.random_seed)
    numpy.random.seed(args.random_seed)

    texts = []
    labels = []
    with gzip.open(args.input, "rt") as ifd:
        for line in ifd:
            doc = json.loads(line)
            text = doc.get(args.text, "")
            text = text.lower() if args.lower_case else text
            text = text if args.keep_punctuation else re.sub(r"[^a-zA-Z0-9\s]", "", text)
            text = text.split()
            translation = doc.get(args.translation, "")
            translation = translation.lower() if args.lower_case else translation
            translation = translation if args.keep_punctuation else re.sub(r"[^a-zA-Z0-9\s]", "", translation)
            translation = translation.split()
            num_subdocs = round(0.5 + (len(text) + len(translation)) / args.max_doc_length)
            if num_subdocs == 0:
                continue
            text_per = int(len(text) / num_subdocs)
            translation_per = int(len(translation) / num_subdocs)
            for i in range(num_subdocs):
                subtext = " ".join(
                    text[i*text_per : (i + 1)*text_per] + translation[i*translation_per : (i + 1)*translation_per]
                )
                texts.append(subtext)
                labels.append({k : v for k, v in doc.items() if k not in [args.text, args.translation]})

    cvect = CountVectorizer(max_df=0.5, min_df=10)
    word_frame = pandas.DataFrame(cvect.fit_transform(texts).todense()).to_numpy()
    label_frame = pandas.DataFrame(labels)[args.target_field].to_numpy()

    kf = KFold(n_splits=args.num_splits, shuffle=True, random_state=args.random_seed)

    scores = []
    for split, (train_indices, test_indices) in enumerate(kf.split(label_frame), 1):
        logging.info("Performing random fold #%d", split)
        train_X, train_Y = word_frame[train_indices], label_frame[train_indices]
        test_X, test_Y = word_frame[test_indices], label_frame[test_indices]
        model = MultinomialNB()
        model.fit(train_X, train_Y)
        guesses = model.predict(test_X)
        scores.append(
            (
                f1_score(test_Y, guesses, average="macro"),
                f1_score(test_Y, guesses, average="micro")                
            )
        )
    
    logging.info(
        "Average macro/micro F1 score: %.3f/%.3f",
        sum([x[0] for x in scores]) / len(scores),
        sum([x[1] for x in scores]) / len(scores)
    )

    final_model = MultinomialNB()
    final_model.fit(word_frame, label_frame)
    with gzip.open(args.output, "wb") as ofd:
        ofd.write(pickle.dumps((cvect, final_model)))
