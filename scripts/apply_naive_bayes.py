import argparse
import pickle
import json
import re
import gzip
import logging
import random
import cmd
import numpy
import pandas
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import KFold
from sklearn.metrics import f1_score

class ClassifyInput(cmd.Cmd):
    def __init__(self, vect, model):
        self.prompt = "text > "
        self.vect = vect
        self.model = model
        super(ClassifyInput, self).__init__()
    def emptyline(self):
        pass
    def postcmd(self, stop, line):
        return re.match(r"^\s*$", line)
    def default(self, line):
        word_frame = pandas.DataFrame(self.vect.transform([line]).todense()).to_numpy()
        print(word_frame[0].sum())
        print(model.predict(word_frame)[0])
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", dest="input", help="Input file")
    parser.add_argument("--model", dest="model", help="Model file")
    parser.add_argument("--lower_case", dest="lower_case", action="store_true", default=False)
    parser.add_argument("--keep_punctuation", dest="keep_punctuation", action="store_true", default=False)
    parser.add_argument("--text", dest="text", default="text")
    parser.add_argument("--translation", dest="translation", default="translation")
    parser.add_argument("--target_field", dest="target_field", help="Field to try and classify")
    parser.add_argument("--output", dest="output", help="Output file")
    parser.add_argument("--random_seed", dest="random_seed", default=0, type=int, help="Random seed")
    parser.add_argument("--log_level", dest="log_level", default="INFO",
                        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"], help="Logging level")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    random.seed(args.random_seed)
    numpy.random.seed(args.random_seed)

    with gzip.open(args.model, "rb") as ifd:
        cvect, model = pickle.loads(ifd.read())
        
    if args.input:
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
                texts.append(" ".join(text + translation))
                labels.append({k : v for k, v in doc.items() if k not in [args.text, args.translation]})

        word_frame = pandas.DataFrame(cvect.transform(texts).todense()).to_numpy()
        label_frame = pandas.DataFrame(labels).to_numpy()

        guesses = model.predict(word_frame)
        print("\n".join(["labels: {}\tguess: {}".format(ls.tolist(), g) for ls, g in zip(label_frame, guesses)]))
    else:
        ClassifyInput(cvect, model).cmdloop("Enter text to classify (blank line to exit)")
