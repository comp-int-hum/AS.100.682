import argparse
import re
import gzip
import json
import csv
import random
import logging
import pandas
import altair as alt
from altair_saver import save

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", dest="input", help="Input file")
    parser.add_argument("--labeling", dest="labeling", default=None)
    parser.add_argument("--window_size", dest="window_size", type=int, default=15)
    parser.add_argument("--field", dest="field")
    parser.add_argument("--field_lookup", dest="field_lookup")
    parser.add_argument("--output", dest="output", help="Output file")
    parser.add_argument("--random_seed", dest="random_seed", default=0, type=int, help="Random seed")
    parser.add_argument("--log_level", dest="log_level", default="INFO",
                        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"], help="Logging level")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    random.seed(args.random_seed)
    
    with gzip.open(args.input, "rt") as ifd:
        data = json.loads(ifd.read())

    field_lookup = {}
    if args.field_lookup:
        with open(args.field_lookup, "rt") as ifd:
            for i, line in enumerate(ifd):
                for item in line.split("\t"):
                    field_lookup[item] = i

    topic_labels = {}
    with open(args.labeling, "rt") as ifd:
        for i, line in enumerate(ifd):
            if not re.match(r"^\s*$", line):
                topic_labels[i] = line.split("\t")[0]

    buckets = {}
    for datum in data:
        bucket = datum[args.field]
        if isinstance(bucket, int):
            bucket = bucket - (bucket % args.window_size)
        else:
            bucket = field_lookup[bucket]
        for k, v in datum["topics"].items():
            label = topic_labels[int(k)] if int(k) in topic_labels else k
            if re.match(r"^\s*$", label):
                label = "Unlabeled topics"
            key = (bucket, label)
            buckets[key] = buckets.get(key, {"bucket" : bucket, "label" : label, "weight" : 0.0})
            buckets[key]["weight"] += v
    
    df = pandas.DataFrame(list(buckets.values()))

    im = alt.Chart(df, width=1000, height=800).configure_view(stroke=None).mark_area().encode(
        x=alt.X(
            "bucket:N",
            title=args.field,
            axis=alt.Axis(format=".4", ticks=False, titleFontSize=30, labelFontSize=15, grid=False, domain=False)
        ),
        y=alt.Y(
            "weight",
            stack="normalize",
            title="Topic prominence",
            axis=alt.Axis(labels=False, ticks=False, titleFontSize=30, grid=False, domain=False)
        ),
        color=alt.Color(
            "label:N",
            legend=alt.Legend(title="Topics", symbolLimit=50, titleFontSize=30, labelFontSize=15, labelLimit=400)
        )
    )
    im.save(args.output, scale_factor=1.0)
