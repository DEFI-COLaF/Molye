import os
import regex as re
from bs4 import BeautifulSoup
import molyé_util as m_util



def in_year_range(doc_date, start_year, end_year):
    doc_year = int(doc_date["when"][:4])
    return start_year <= doc_year and doc_year < end_year

def write_lang_period_corpus(lines, lang, start, end, dataset):
    lang_corpus = "\n".join([l.strip() for l in lines if len(l.strip())])
    date_range = f"{start}-{end}"
    date_folder = f"{dataset}/{date_range}"
    if not os.path.isdir(date_folder):
        os.mkdir(date_folder)
    with open(f"{date_folder}/{lang}.txt", mode="w") as f:
        f.write(lang_corpus)




def check_tag_name(tag, target_names):
    return tag.name in target_names

def check_lang(tag, target_languages):
    return tag.has_attr("xml:lang") and tag.attrs["xml:lang"] in target_languages

def build_custom(target_tags, target_langs):
    return lambda x: check_tag_name(x, target_tags) and (check_lang(x, target_langs) or check_lang(x.parent, target_langs))

def get_line_group(doc, custom_func):
    lines = doc.find_all(custom_func)
    for line in lines:
        stage = line.find_all("stage")
        for s in stage:
            s.decompose()
    return lines

def get_token_count(file):
    with open(file) as f:
        text = f.read()
        my_l = len(text.split())
        print(file, my_l)
    return my_l

def combine_subcorpora(subcorpus_files, labels):
    combined = []
    [combined.append(open(f).read()) for f in subcorpus_files if f.split("/")[-1][:-4] in labels]
    combined = "\n".join(combined)
    return combined


def write_demo_corpora(corpus_fol, subcorpus_files):
    baragouin_labels = ["fra-deu", "fra-ang", "fra-nld"]
    creole_labels = ["gcf", "hat", "lou", "mau", "gcr"]

    combined_fol = f"{corpus_fol}/full_combined"
    dia = combine_subcorpora(subcorpus_files, ["fra-dia"])
    rcf = combine_subcorpora(subcorpus_files, ["rcf"])
    combined_baragouin = combine_subcorpora(subcorpus_files, baragouin_labels)
    combined_creole = combine_subcorpora(subcorpus_files, creole_labels)
    with open(f"{combined_fol}/all_peasant.txt", mode="w") as f:
        f.write(dia)
    with open(f"{combined_fol}/all_baragouin.txt", mode="w") as f:
        f.write(combined_baragouin)

    with open(f"{combined_fol}/all_americas.txt", mode="w") as f:
        f.write(combined_creole)

    with open(f"{combined_fol}/all_rcf.txt", mode="w") as f:
        f.write(rcf)


def main(dataset_f, start=1500, end=1940):
    file = f"{dataset_fol}/molyé.xml"
    soup = BeautifulSoup(open(file), features="xml")
    dates = [t for t in soup.find_all("date") if t.parent.name == "bibl"]

    good_dates = [date for date in dates if in_year_range(date, start, end)]
    timed_docs = [date.parent.parent.parent.parent.parent for date in good_dates]
    targets = [["met-fr"], ["fra-dia"], ["fra-deu"], ["fra-ang"], ["fra-nld"], ["fra-gsc"], ["rcf"], ["hat"], ["gcf"], ["lou"], ["gcr"], ["mau"]]
    for target_langs in targets:
        target_tags = ["p", "l"]
        custom = build_custom(target_tags, target_langs)
        grouped_lines = [get_line_group(doc, custom) for doc in timed_docs]
        for i, doc in enumerate(timed_docs):
            secondary = [s for s in doc.find_all(["s"], attrs={"xml:lang": target_langs}) if
                         s.parent not in grouped_lines[i]]
            grouped_lines[i].extend(secondary)
        print(target_langs, len([g for g in grouped_lines if len(g)]))
        flat_lines = ["\n".join([tag.text.strip() for tag in group if not tag.text.isspace()]) for group in grouped_lines]
        write_lang_period_corpus(flat_lines, target_langs[0], start, end, f"{dataset_fol}/subcorpora")

def create_simple_search_regex(search_words):
    wrapped = [fr"({word})" for word in search_words]
    united = "|".join(wrapped)
    bounded = fr"({united})"
    return bounded





def calculate_etre(corpus_file):
    past_cr = ["été", "étais", "était", "étaient", "té"]
    cond_cr = ["serais", "serait", "seraient", "sré"]
    fut_cr = ["sera", "seras", "sra"]

    pres = ["suis", "es", "est", "sommes", "êtes", "sont"]
    subj = ["sois", "soit", "soyons", "soyez", "soient"]
    past_subj = ["fusse", "fusses", "fût", "fussions", "fussiez", "fussent"]
    pret = ["fus", "fut", "fûmes", "fûtes", "furent"]
    fut_infl = ["serai", "serons", "seront", "serez"]
    cond_infl = ["serions", "seriez"]
    inf = ["être", "êt"]
    ce = ["c'est", "cé", "c'était", "est-ce"]
    cr = past_cr + cond_cr + fut_cr
    infl = pres + subj + past_subj + fut_infl + cond_infl + cr

    searches = {"inf": inf, "infl": infl, "cr": cr, "ce": ce}
    for k, v in searches.items():
        searches[k] = create_simple_search_regex(v)

    stats = {}
    text = open(corpus_file).read()
    for label, pattern in searches.items():
        stats[label] = len(re.findall(fr"\W{pattern}\W", text))
    return stats


dataset_fol = "../dataset_colaf"
main(dataset_fol)
subcorpora_fol = f"{dataset_fol}/subcorpora"
corpus_folder = f"{subcorpora_fol}/1500-1940"
subcorpus_files = [f"{corpus_folder}/{f}" for f in os.listdir(f"{corpus_folder}") if f[-3:] =="txt"]
write_demo_corpora(subcorpora_fol, subcorpus_files)
main(dataset_fol)


subcorpus_folder = f"{dataset_fol}/subcorpora/1500-1940"
test_corpora = [f"{subcorpus_folder}/{f}" for f in os.listdir(subcorpus_folder)]
for file in test_corpora:
    print(file)
    stats = calculate_etre(file)
    print(stats)