import argparse
from glob import glob
import zipfile
import json
import gzip
import re
import os.path
import logging
import random


def process_cdl(tree):
    f, s = [tree.get("f", {}).get("form", ""),
            tree.get("f", {}).get("sense", "")
            ] if tree.get("node") == "l" else ["*", "*"]
    return sum([process_cdl(x) for x in tree.get("cdl", [])], []) + ([(f, s)] if "*" not in [f, s] else [])


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--oracc", dest="oracc", help="Path to ORACC")
    parser.add_argument("--cdli", dest="cdli", help="Path to CDLI data")
    parser.add_argument("--output", dest="output", help="Output file")
    parser.add_argument("--random_seed", dest="random_seed", default=0, type=int, help="Random seed")
    parser.add_argument("--log_level", dest="log_level", default="INFO",
                        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"], help="Logging level")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    random.seed(args.random_seed)
    
    data = {}

    for zfname in glob(os.path.join(args.oracc, "*zip")):
        base = os.path.splitext(os.path.basename(zfname))[0].replace("_", "/")
        logging.info("Processing file '%s'", zfname)

        with zipfile.ZipFile(zfname, "r") as zfd:
            for fname in zfd.namelist():
                if fname.endswith("json") and (not fname.endswith("sortcodes.json")):
                    with zfd.open(fname) as ifd:
                        text = ifd.read()
                        if text != b'':
                            j = json.loads(text)
                            tp = j["type"]
                            if tp == "corpus":
                                # project, proxies, members (can all be ignored?)
                                # what are "proxies" (look like "members")?
                                pass
                            elif tp == "catalogue":
                                # summaries(ignore), members
                                # id_text|id_composite, designation, period, provenience
                                #pass
                                for eid, props in j.get("members", {}).items():
                                    data[eid] = data.get(eid, {})
                                    for p, v in props.items():
                                        data[eid][p] = data[eid].get(p, set())
                                        if isinstance(v, list):
                                            for vv in v:                                                
                                                data[eid][p].add(vv)
                                        else:
                                            data[eid][p].add(v)
                                # for eid, summary in j.get("summaries", {}).items():
                                #     print(eid, summary)
                            elif tp == "FeatureCollection":
                                # features
                                #pass
                                for feat in j["features"]:
                                    props = feat["properties"]
                                    #eid = props.get("uri", None)
                                    #eid = props.get("cdli_id", props.get("id_text", None)) #props.get("id_composite")))
                                    eid = props.get("id_text", props.get("id_composite"))
                                    if eid == None: # or not eid.startswith("P"):
                                        #iss.writerow({"project" : base, "file" : fname, "id" : "", "reason" : "Neither 'id_text' nor 'id_composite' field"})
                                        continue
                                    data[eid] = data.get(eid, {})
                                    coords = feat["geometry"]["coordinates"]
                                    if len(coords) == 0:
                                        #iss.writerow({"project" : base, "file" : fname, "id" : eid, "reason" : "Zero-length coordinates"})
                                        pass
                                    else:
                                        lon, lat = coords
                                        data[eid]["coordinates"] = data[eid].get("coordinates", set())
                                        data[eid]["coordinates"].add((lon, lat))
                                    for p, v in props.items():
                                        data[eid][p] = data[eid].get(p, set())
                                        data[eid][p].add(v)
                            elif tp == "metadata":
                                # config, formats, witnesses
                                # pass
                                for eid, rest in j.get("witnesses", {}).items():
                                    data[eid] = data.get(eid, {})
                                    for p, vs in rest.items():
                                        data[eid][p] = data[eid].get(p, set())
                                        for v in vs:
                                            data[eid][p].add(v)
                            elif tp == "glossary":
                                # lang, entries, instances, summaries(ignore)
                                pass
                            elif tp == "cdl":
                                # textid, cdl
                                eid = j["textid"]
                                data[eid] = data.get(eid, {})
                                out = process_cdl(j)
                                text = {
                                    "text" : " ".join([x[0] for x in out]),
                                    "translation" : " ".join([x[1] for x in out])
                                }
                                for k, v in text.items():
                                    data[eid][k] = data[eid].get(k, set())
                                    data[eid][k].add(v)
                            elif tp == "index":
                                # name, keys, map (ignore?)
                                pass
                            elif tp == "portal":
                                # chunks (ignore)
                                pass
                            elif tp == "signlist":
                                # signs (ignore)
                                pass
                            else:
                                raise Exception("Unknown document type '{}' in file '{}'".format(tp, fname))

    data = {k : v for k, v in data.items() if "text" in v}
                            
    logging.info("Loaded %d inscriptions", len(data))
                                
    fields = {}
    with gzip.open(args.output, "wt") as ofd:
        for v in data.values():
            for k in list(v.keys()):
                fields[k] = fields.get(k, {})
                if k in ["text", "translation"] and isinstance(v[k], set):
                    v[k] = " ".join(v[k])
                elif isinstance(v[k], set):
                    v[k] = list(v[k])
            ofd.write(json.dumps(v) + "\n")
