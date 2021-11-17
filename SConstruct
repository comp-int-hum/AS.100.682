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
    ("GUTENBERG_PREDOWNLOADED", "", "${DATA_PATH}/english/predownloaded_gutenberg.zip"),
    ("GUTENBERG_RECORDS", "", "${DATA_PATH}/english/predownloaded_gutenberg_records.json.gz"),
    ("MAX_DOC_LENGTH", "", 1000),
    ("PROJECTS", "", {
        "latin" : {
            "data" : "${DATA_PATH}/classics/perseus",
            "topic_count" : 50,
            "fields_to_classify" : [],
            "evolution_field" : "author",
        },
        "cuneiform" : {
            "data" : "${DATA_PATH}/near_eastern_studies/oracc",
            "topic_count" : 50,
            "fields_to_classify" : [],
            "evolution_field" : "period",
        },
        "english" : {
            "data" : "${DATA_PATH}/english/predownloaded_gutenberg.zip",
            "topic_count" : 50,
            "fields_to_classify" : [],
            "evolution_field" : "year",
        },
    }),

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


for name, script, options in [
        ("CollectLatin", "scripts/collect_latin.py", "--perseus ${LATIN_PATH} --output ${TARGETS[0]}"),
        ("CollectCuneiform", "scripts/collect_cuneiform.py", "--oracc ${ORACC_PATH} --output ${TARGETS[0]}"),
#        ("FilterGutenberg", "scripts/filter_gutenberg.py", "--index ${GUTENBERG_INDEX} --years ${YEARS} --languages ${LANGUAGES} --subjects ${SUBJECTS} --output ${TARGETS}"),
#        ("DownloadGutenberg", "scripts/download_gutenberg.py", "--records ${SOURCES[0]} --output ${TARGETS[0]}"),
        ("CollectEnglish", "scripts/collect_english.py", "--records ${GUTENBERG_RECORDS} --downloaded ${GUTENBERG_PREDOWNLOADED} --output ${TARGETS[0]}"),
        ("TrainTopicModel", "scripts/train_topic_model.py", "--input ${SOURCES[0]} --topic_count ${TOPIC_COUNT} ${'--lower_case' if LOWER_CASE else ''} ${'--keep_punctuation' if KEEP_PUNCTUATION else ''} --text ${TEXT_FIELD} --translation ${TRANSLATION_FIELD} --max_doc_length ${MAX_DOC_LENGTH} --output ${TARGETS[0]}"),
        ("ApplyTopicModel", "scripts/apply_topic_model.py", "--model ${SOURCES[0]} --input ${SOURCES[1]} ${'--lower_case' if LOWER_CASE else ''} ${'--keep_punctuation' if KEEP_PUNCTUATION else ''} --text ${TEXT_FIELD} --translation ${TRANSLATION_FIELD} --output ${TARGETS[0]}"),
        ("FieldValues", "scripts/field_values.py", "--input ${SOURCES[0]} --field ${EVOLUTION_FIELD} --output ${TARGETS[0]}"),
        ("TopicWords", "scripts/topic_words.py", "--model ${SOURCES[0]} --output ${TARGETS[0]}"),
        ("TopicDocuments", "scripts/topic_documents.py", "--input ${SOURCES[0]} --output ${TARGETS[0]} --display_field ${DISPLAY_FIELD}"),
        ("PlotTopicEvolution", "scripts/plot_topic_evolution.py", "--input ${SOURCES[0]} --field ${EVOLUTION_FIELD} --labeling ${SOURCES[1]} ${'--field_lookup ' if len(SOURCES) == 3 else ''} ${SOURCES[2]} --output ${TARGETS[0]}"),
        ("GenerateLatex", "scripts/generate_latex.py", "--figures ${SOURCES} --output ${TARGETS[0]}")
        ]:
    env.AddBuilder(name, script, options)


figures = []
for project_name, project_info in env["PROJECTS"].items():
    data_collector = getattr(env, "Collect{}".format(project_name.title()))
    data = data_collector(
        "work/${PROJECT_NAME}/data.json.gz",
        [],
        PROJECT_NAME=project_name
    )
    topic_model = env.TrainTopicModel(
        "work/${PROJECT_NAME}/topic_model.bin",
        data,
        PROJECT_NAME=project_name,
        TOPIC_COUNT=project_info.get("topic_count", 50),
        TEXT_FIELD=project_info.get("text_field", "text"),
        TRANSLATION_FIELD=project_info.get("translation_field", "translation"),
    )
    top_words = env.TopicWords(
        "work/${PROJECT_NAME}/top_words.tsv",
        topic_model,
        PROJECT_NAME=project_name,
    )
    docwise_topics = env.ApplyTopicModel(
        "work/${PROJECT_NAME}/docwise_topics.json.gz",
        [topic_model, data],
        LOWER_CASE=project_info.get("lower_case", False),
        KEEP_PUNCTUATION=project_info.get("keep_punctuation", False),
        PROJECT_NAME=project_name,
        TEXT_FIELD=project_info.get("text_field", "text"),
        TRANSLATION_FIELD=project_info.get("translation_field", "translation"),        
    )
    top_documents = env.TopicDocuments(
        "work/${PROJECT_NAME}/top_documents.tsv",
        docwise_topics,
        DISPLAY_FIELD=project_info.get("display_field", "title"),
        PROJECT_NAME=project_name,
    )
    # topic_evolution = env.PlotTopicEvolution(
    #     "work/${PROJECT_NAME}/topic_evolution.png",
    #     [docwise_topics, "lookups/${PROJECT_NAME}_topic_labels.txt"],
    #     EVOLUTION_FIELD=project_info.get("evolution_field", "year"),
    #     PROJECT_NAME=project_name,
    # )

# poster_code = env.GenerateLatex(
#     "work/poster.tex",
#     figures,
# )

# poster = env.PDF(
#     "work/poster.pdf",
#     poster_code
# )
