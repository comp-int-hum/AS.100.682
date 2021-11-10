import argparse
import logging
import random

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--figures", dest="figures", nargs="*")
    parser.add_argument("--output", dest="output", help="Output file")
    parser.add_argument("--random_seed", dest="random_seed", default=0, type=int, help="Random seed")
    parser.add_argument("--log_level", dest="log_level", default="INFO",
                        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"], help="Logging level")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    random.seed(args.random_seed)    
    
    c = """\\documentclass[a0paper,landscape]{tikzposter}

\\usepackage{enumitem,cprotect}
\\usepackage{times}
\\usepackage{latexsym}
\\usepackage{tikz}
\\usetikzlibrary{calc,positioning,shadows.blur,decorations.pathreplacing}
\\usepackage{calc}
\\usepackage{url}
\\usepackage{xparse}
\\usepackage{subfig}
\\usepackage{multicol}
\\usepackage{stfloats}
\\usepackage{enumitem}
\\usepackage{listings}


\\title{\\textrm{\\fontsize{80}{100} \\selectfont Topic modeling for conceptual change over time}}

\\author{\\textrm{ \\fontsize{60}{72} \\selectfont Sede, Richard, Hale, and Karoline}}
\\institute{\\textrm{\\fontsize{60}{72} \\selectfont Johns Hopkins University}}
\\begin{document}
\\maketitle[titletextscale=0.1,width=\\textwidth]

\\begin{columns}
\\column{0.4}
\\block{Sede}{
\\includegraphics{english_topic_evolution.png}
}
\\block{Karoline}{
\\includegraphics{english_topic_evolution.png}
}
\\column{0.2}
\\column{0.4}
\\block{Richard}{
\\includegraphics{english_topic_evolution.png}
}
\\block{Hale}{
\\includegraphics{english_topic_evolution.png}
}

\\end{columns}
\\end{document}
    """
    with open(args.output, "wt") as ofd:
        ofd.write(c)
