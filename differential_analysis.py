import argparse
import json
import pandas

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input", help="Input file")
    parser.add_argument("-o", "--output", dest="output", help="Output file")
    parser.add_argument("-t", "--time_field", dest="time_field", help="")
    parser.add_argument("-n", "--num_intervals", dest="num_intervals", type=int, default=5)
    args = parser.parse_args()

    min_val, max_val = None, None
    with gzip.open(args.input, "rt") as ifd:
        for line in ifd:
            j = json.loads(line)
            if args.time_field not in j:
                continue
            t = j[args.time_field]
            if not isinstance(t, (float, int)):
                t = datetime.datetime.strptime(t, "%a %b %d %H:%M:%S %z %Y").timestamp()
            if min_val == None or t < min_val:
                min_val = t
            if max_val == None or t > max_val:
                max_val = t
    inc = 0.01 * (max_val - min_val)
    max_val += inc
    min_val -= inc
    interval = (max_val - min_val) / args.num_intervals

    indices = {
        "temporal_buckets" : {},
        "geographic_buckets" : {},
        "categorical_buckets" : {},
    }
    buckets = [[] for _ in range(args.num_intervals)]
    bucket_counts = [0 for _ in range(args.num_intervals)]
    features = set(["not_in_liwc"])
    with gzip.open(args.input, "rt") as ifd:
        for line in ifd:
            j = json.loads(line)
            if args.time_field not in j:
                continue
            t = j[args.time_field]
            if not isinstance(t, (float, int)):
                t = datetime.datetime.strptime(t, "%a %b %d %H:%M:%S %z %Y").timestamp()            
            i = int((t - min_val) / interval)
            bucket_counts[i] += j.get("total", 0)
            for k, v in j["liwc"].items():
                buckets[i][k] = buckets[i].get(k, 0) + v
                features.add(k)
    feature_to_id = {k : i for i, k in enumerate(features)}
    id_to_feature = {v : k for k, v in feature_to_id.items()}
    distributions = numpy.zeros(shape=(args.num_intervals, len(features)))
    data_sums = numpy.array(bucket_counts)
    for i, b in enumerate(buckets):
        for k, v in b.items():
            distributions[i][feature_to_id[k]] = v
            #print(distributions[0], data_sums[0])
    distributions = (distributions.T / data_sums).T
    print(distributions.sum(1), min_val, interval)

