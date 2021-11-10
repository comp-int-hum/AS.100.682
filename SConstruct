import os
import os.path
import logging
import random
import subprocess
import shlex
import gzip
import re
import functools
import time
import imp
import sys
import json
import steamroller

# workaround needed to fix bug with SCons and the pickle module
del sys.modules['pickle']
sys.modules['pickle'] = imp.load_module('pickle', *imp.find_module('pickle'))
import pickle

# actual variable and environment objects
vars = Variables()
vars.AddVariables(
    ("OUTPUT_WIDTH", "", 500),
    ("DATA_PATH", "", "/mnt/data"),
    ("LATIN_PATH", "", "${DATA_PATH}/classics/perseus"),
    ("ORACC_PATH", "", "${DATA_PATH}/near_eastern_studies/oracc"),
    ("GUTENBERG_INDEX", "", "${DATA_PATH}/indices/gutenberg_20211008.tsv.gz"),
    ("GUTENBERG_PREDOWNLOADED", "", "${DATA_PATH}/english/predownloaded_gutenberg.zip"),
    ("DOWNLOAD", "", False),
    ("TOPIC_COUNT", "", 50),
    ("LOWER_CASE", "", 1),
    ("KEEP_PUNCTUATION", "", 0),
    ("TEXT_FIELD", "", "text"),
    ("TRANSLATION_FIELD", "", "translation"),
    ("EVOLUTION_FIELD", "", "year"),
    ("MAX_DOC_LENGTH", "", 1000),
)

env = Environment(variables=vars, ENV=os.environ, TARFLAGS="-c -z", TARSUFFIX=".tgz",
                  tools=["default", steamroller.generate],
)

# function for width-aware printing of commands
def print_cmd_line(s, target, source, env):
    if len(s) > int(env["OUTPUT_WIDTH"]):
        print(s[:int(float(env["OUTPUT_WIDTH"]) / 2) - 2] + "..." + s[-int(float(env["OUTPUT_WIDTH"]) / 2) + 1:])
    else:
        print(s)

# and the command-printing function
env['PRINT_CMD_LINE_FUNC'] = print_cmd_line

# and how we decide if a dependency is out of date
env.Decider("timestamp-newer")

env.AddBuilder(
    "CollectLatin",
    "scripts/collect_latin.py",
    "--perseus ${LATIN_PATH} --output ${TARGETS[0]}"
)

env.AddBuilder(
    "CollectCuneiform",
    "scripts/collect_cuneiform.py",
    "--oracc ${ORACC_PATH} --output ${TARGETS[0]}"
)

env.AddBuilder(
    "FilterGutenberg",
    "scripts/filter_gutenberg.py",
    "--index ${GUTENBERG_INDEX} --years ${YEARS} --languages ${LANGUAGES} --subjects ${SUBJECTS} --output ${TARGETS}"
)

env.AddBuilder(
   "DownloadGutenberg",
   "scripts/download_gutenberg.py",
   "--records ${SOURCES[0]} --output ${TARGETS[0]}"
)

env.AddBuilder(
    "CollectEnglish",
    "scripts/collect_english.py",
    "--records ${SOURCES[0]} --downloaded ${SOURCES[1]} --output ${TARGETS[0]}"
)

env.AddBuilder(
    "TrainTopicModel",
    "scripts/train_topic_model.py",
    "--input ${SOURCES[0]} --topic_count ${TOPIC_COUNT} --lower_case ${LOWER_CASE} --keep_punctuation ${KEEP_PUNCTUATION} --text ${TEXT_FIELD} --translation ${TRANSLATION_FIELD} --max_doc_length ${MAX_DOC_LENGTH} --output ${TARGETS[0]}"
)

env.AddBuilder(
    "ApplyTopicModel",
    "scripts/apply_topic_model.py",
    "--model ${SOURCES[0]} --input ${SOURCES[1]} --lower_case ${LOWER_CASE} --keep_punctuation ${KEEP_PUNCTUATION} --text ${TEXT_FIELD} --translation ${TRANSLATION_FIELD} --output ${TARGETS[0]}"
)

env.AddBuilder(
    "TopicWords",
    "scripts/topic_words.py",
    "--model ${SOURCES[0]} --output ${TARGETS[0]}"
)

env.AddBuilder(
    "TopicDocuments",
    "scripts/topic_documents.py",
    "--input ${SOURCES[0]} --output ${TARGETS[0]} --display_field ${DISPLAY_FIELD}"
)

env.AddBuilder(
    "PlotTopicEvolution",
    "scripts/plot_topic_evolution.py",
    "--input ${SOURCES[0]} --field ${EVOLUTION_FIELD} --labeling ${SOURCES[1]} ${'--field_lookup ' if len(SOURCES) == 3 else ''} ${SOURCES[2]} --output ${TARGETS[0]}"
)

env.AddBuilder(
    "GenerateLatex",
    "scripts/generate_latex.py",
    "--figures ${SOURCES} --output ${TARGETS[0]}"
)

latin = env.CollectLatin(
    "work/latin.json.gz",
    []
)

cuneiform = env.CollectCuneiform(
    "work/cuneiform.json.gz",
    []
)

english_records = env.FilterGutenberg(
  "work/english_records.json.gz",
  [],
  YEARS="1760-1850",
  LANGUAGES="en",
  SUBJECTS="poet"
)

english_docs = env.DownloadGutenberg(
   "work/english_files.zip",
   english_records
) if env["DOWNLOAD"] else env.File(env["GUTENBERG_PREDOWNLOADED"])

english = env.CollectEnglish(
  "work/english.json.gz",
  [english_records, english_docs]
)

english_model = env.TrainTopicModel(
  "work/english_model.bin",
  english
)

latin_model = env.TrainTopicModel(
    "work/latin_model.bin",
    latin
)

cuneiform_model = env.TrainTopicModel(
    "work/cuneiform_model.bin",
    cuneiform,
    LOWER_CASE=0,
    KEEP_PUNCTUATION=1
)

latin_top_words = env.TopicWords(
    "work/latin_top_words.tsv",
    latin_model
)

english_top_words = env.TopicWords(
  "work/english_top_words.tsv",
  english_model
)

cuneiform_top_words = env.TopicWords(
    "work/cuneiform_top_words.tsv",
    cuneiform_model
)

cuneiform_docwise_topics = env.ApplyTopicModel(
    "work/cuneiform_docwise_topics.json.gz",
    [cuneiform_model, cuneiform],
    LOWER_CASE=0,
    KEEP_PUNCTUATION=1
)

english_docwise_topics = env.ApplyTopicModel(
  "work/english_docwise_topics.json.gz",
  [english_model, english]
)

latin_docwise_topics = env.ApplyTopicModel(
    "work/latin_docwise_topics.json.gz",
    [latin_model, latin]
)

english_top_documents = env.TopicDocuments(
    "work/english_top_documents.tsv",
    english_docwise_topics,
    DISPLAY_FIELD="title"
)

latin_top_documents = env.TopicDocuments(
    "work/latin_top_documents.tsv",
    latin_docwise_topics,
    DISPLAY_FIELD="title"
)

cuneiform_top_documents = env.TopicDocuments(
    "work/cuneiform_top_documents.tsv",
    cuneiform_docwise_topics,
    DISPLAY_FIELD="display_name"
)

english_evolution = env.PlotTopicEvolution(
   "work/english_topic_evolution.png",
   [english_docwise_topics, "lookups/english_topic_labels.txt"],
   EVOLUTION_FIELD="year"
)

#cuneiform_evolution = env.PlotTopicEvolution(
#    "work/cuneiform_topic_evolution.png",
#    [cuneiform_docwise_topics, "lookups/cuneiform_topic_labels.txt", "lookups/cuneiform_field_lookup.txt"],
#    EVOLUTION_FIELD="period"
#)

# latin_evolution = env.PlotTopicEvolution(
#     "work/latin_topic_evolution.png",
#     [latin_docwise_topics, "lookups/latin_topic_labels.txt", "lookups/latin_field_lookup.txt"],
#     EVOLUTION_FIELD="author"
# )

poster_code = env.GenerateLatex(
   "work/poster.tex",
   []
)

poster = env.PDF(
   "work/poster.pdf",
   poster_code
)
