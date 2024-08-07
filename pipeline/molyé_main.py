# -*- coding: utf-8 -*-
import os

import molyé_util as m_util


import requests
from bs4 import BeautifulSoup
from lxml import etree as ET
import io
import regex as re
import transform_tc as tc
import transform_wiki as wiki
import metadata_patterns
import annotation

import transform_hat_gcf as hat
import transform_gcr as gcr
import transform_gal_local as gal
import transform_rcf as rcf
import transform_lou as lou

def extract_short_metadata(file_text):
    metadata = {}
    soup = BeautifulSoup(file_text, features="xml")
    titleStmt = soup.find("titleStmt")
    metadata["title"] = titleStmt.find("title").text
    metadata["author"] = titleStmt.find("author").text
    metadata["id"] = titleStmt.find("idno").text
    metadata["sourceDesc"] = str(soup.find("sourceDesc"))
    #metadata["date"] = soup.find("bibl", type="PrintSource").find("date")["when"]
    #extract the whole tage
    metadata["langUsage"] = str(soup.find("langUsage"))
    return metadata


def prep_work_extract(file_name, langs, level):
    file_text = m_util.read_file(file_name)
    metadata = extract_short_metadata(file_text)
    quotes = m_util.get_lines_of_interest(file_text, langs, level)
    return metadata,  [quotes]

def prep_play_extract(file_name, target_langs):
    file_text = m_util.read_file(file_name)
    metadata = extract_short_metadata(file_text)
    soup = BeautifulSoup(file_text, features="xml")
    main_lang = soup.find("language")["ident"]
    scenes = soup.find_all("div", type="scene")
    quote_groups = []
    for scene in scenes:
        #act_scene
        act_n = scene.parent["n"]
        scene_n = scene["n"]
        scene["n"] = f"{act_n}_{scene_n}"
    if "met-fr" in main_lang:
        quote_groups = [m_util.fix_tei_tag(scene) for scene in scenes if scene.find("sp", attrs={"xml:lang": target_langs})]
    else:
        quote_groups = [m_util.fix_tei_tag(scene) for scene in scenes]
    return metadata, quote_groups

def prep_poem_extract(file_name):
    file_text = m_util.read_file(file_name)
    metadata = extract_short_metadata(file_text)
    play_soup = BeautifulSoup(file_text, features="xml")
    poems = play_soup.find_all("div")
    quote_groups = [m_util.fix_tei_tag(poem) for poem in poems]
    return metadata, quote_groups

def prep_all_plays(folder, target_langs):
    prepped_extracts = []
    file_names = [f"{folder}/{file}" for file in os.listdir(folder)]
    for file_name in file_names:
        #print(file_name)
        short_metadata, quote_groups = prep_play_extract(file_name, target_langs)
        #Handle whitespace and repeated names in xml:ids
        prepped_extracts.append([short_metadata, quote_groups, target_langs, None])
    all_langs = {"met-fr", "fra-dia", "fra-deu", "fra-ang"}
    return prepped_extracts, all_langs


def get_all_lines(soup, lang, primary_tags, secondary_tags):
    quotes = [q for q in soup.find_all(primary_tags) if not "xml:lang" in q.attrs or q["xml:lang"] not in ["met-fr", "eng"]]
    for q in quotes:
        q["xml:lang"] = lang
    quotes = [str(q).replace("tei:", "") for q in quotes]
    secondary_quotes = [str(q).replace("tei:", "") for q in soup.find_all(secondary_tags)
                        if not "xml:lang" in q.attrs or q["xml:lang"] not in ["met-fr", "eng"]]
    quotes += [q for q in secondary_quotes if q not in " ".join(quotes)]
    return quotes

def prep_wiki_works(wiki_works, folder):
    prepped_extracts = []
    all_langs = set()
    for work in wiki_works:
        file_name = m_util.find_converted_file(work["Title"], folder)
        if file_name:
            langs = [work["Lang"]]
            file_text = m_util.read_file(file_name)
            soup = BeautifulSoup(file_text, features="xml")
            main_lang = soup.find("text")["xml:lang"]
            short_metadata = {}
            quote_groups = []
            if "met-fr" in main_lang:
                short_metadata, quote_groups = prep_work_extract(file_name, langs, "s")

            else:
                short_metadata = extract_short_metadata(file_text)
                quote_groups = [get_all_lines(soup, main_lang, ["p"], ["NA"])]

            langs = langs + [main_lang]
            all_langs = all_langs.union(set(langs))
            prepped_extracts.append([short_metadata, quote_groups, langs, None])

    return prepped_extracts, all_langs

def prep_all_poems(folder):
    prepped_extracts = []
    all_langs = set()
    file_names = [f"{folder}/{file}" for file in os.listdir(folder)]
    for file in file_names:
        file_text = m_util.read_file(file)
        soup = BeautifulSoup(file_text, features="xml")
        main_lang = [soup.find("language")["ident"]]
        short_metadata, quote_groups = prep_poem_extract(file)
        prepped_extracts.append([short_metadata, quote_groups, set(main_lang), None])
        all_langs = all_langs.union(set(main_lang))
    return prepped_extracts, all_langs

def prep_misc_works(folder, target_langs=["fra-ang", "mau", "fra-gsc"]):
    prepped_extracts = []
    all_langs = set()
    file_names = [f"{folder}/{file}" for file in os.listdir(folder)]
    for file in file_names:
        # print(file)
        file_text = m_util.read_file(file)
        soup = BeautifulSoup(file_text, features="xml")
        #only handle completed metadata
        if soup.find("language"):
            main_lang =  [soup.find("language")["ident"]]
            short_metadata = extract_short_metadata(file_text)
            all_langs = all_langs.union(set(main_lang))
            quote_groups = []
            if "met-fr" in main_lang:
                short_metadata, quote_groups = prep_work_extract(file, target_langs, ["sp", "s"])
            else:
                quote_groups = [get_all_lines(soup, main_lang, ["sp"], ["lg", "p"])]
            prepped_extracts.append([short_metadata, quote_groups, main_lang, None])
    return prepped_extracts, all_langs

def prep_prose(folder):
    pass


#
# def test_prose():
#     wiki_title = 'Une de perdue'
#     wiki_link = "https://fr.wikisource.org/wiki/Une_de_perdue,_deux_de_trouv%C3%A9es/Tome_I"
#     test_root = wiki.convert_one_wiki_prose(wiki_link, "000", "Moliyé")
#     out = ET.tostring(test_root, encoding="unicode").replace("XMLID", "xml:id")
#     ET.ElementTree(ET.fromstring(out)).write("dataset_colaf/test.xml", xml_declaration=True, encoding="UTF-8",  pretty_print=True)
#

#If the lang date (originally written) is earlier than the publication date, use the lang date
def effective_doc_date(doc):
    effective_date = doc.find("bibl").find("date")["when"]
    lang_usage = doc.find("langUsage")
    if lang_usage:
        langs = lang_usage.find_all("language")
        for lang in langs:
            if lang.find_all("date"):
                effective_date=lang.find("date")["when"]
                #print(effective_date[:4])
    return int(effective_date[:4])

def arrange_timeline(file):
    soup = BeautifulSoup(open(file), features="xml")
    docs = soup.find_all("TEI")
    docs_sorted = sorted(docs, key=lambda x: effective_doc_date(x))
    corpus_root = ET.Element("teiCorpus", xmlns="http://www.tei-c.org/ns/1.0")
    header = m_util.fix_tei_tag(soup.find("teiHeader"))
    corpus_root.append(ET.fromstring(header))
    for doc in docs_sorted:
        corrected = m_util.fix_tei_tag(doc)
        corpus_root.append(ET.fromstring(corrected))
    m_util.write_tree(corpus_root, file)

def recache(works, annotate):
    classique_works = [w for w in works if w["Source"] == "theatre-classique"]
    wikisource_works = [w for w in works if w["Source"] == "Wikisource"]
    src_dir = "../source"
    fin_dir = "../dataset_colaf"
    tc_dir = "theatre_classique"
    wiki_dir = "wikisource"
    raw_classique_folder = f"{src_dir}/{tc_dir}"
    classique_tei_folder = f"{fin_dir}/{tc_dir}"
    raw_wiki_folder = f"{src_dir}/{wiki_dir}"
    wiki_tei_folder = f"{fin_dir}/{wiki_dir}"
    folders = [raw_classique_folder, classique_tei_folder, raw_wiki_folder, wiki_tei_folder]
    m_util.prepare_folders(folders)
    tc.save_tc_works(raw_classique_folder, classique_works)
    tc.transform_classique(raw_classique_folder, classique_tei_folder)
    if annotate:
        annotation.annotate_all_plays(classique_works, f"{fin_dir}/{classique_tei_folder}")

def main(list_file, recache=False, annotate=False):
    works = m_util.load_works(list_file)
    if recache:
        recache(annotate)

    #
    # hat.main()
    # gal.main()
    # rcf.main()
    # wiki.convert_wiki_work(wikisource_works, "Molyé", wiki_tei_folder)
    # lou.main()
    targets = ["fra-dia", "fra-ang", "fra-deu", "fra-gsc", "rcf", "hat", "lou", "gcf", "fra-nld"]
    play_extracts, play_langs = prep_all_plays("../dataset_colaf/theatre", targets)
    poem_extracts, poem_langs = prep_all_poems("../dataset_colaf/poetry")
    misc_extracts, misc_langs = prep_misc_works("../dataset_colaf/misc_works", targets)
    all_extracts = play_extracts + poem_extracts   + misc_extracts
    all_langs = play_langs.union(poem_langs).union(misc_langs)

    #print(all_langs)
    main_corpus_fol = "../main_corpus"
    corpus_file_name = f"{main_corpus_fol}/molyé20240808.xml"
    corpus_metadata = {"id" : "Molyé_000", "title": "Molyé", "author": "Rasul Dent",
                       "publisher": "CoLAF", "online_publisher": "CoLAF",  "permalien" : "https://colaf.huma-num.fr/",
                       "online_date": "2024"}
    corpus_tree = metadata_patterns.create_corpus_xml(corpus_metadata, all_langs, all_extracts)
    m_util.write_tree(corpus_tree, corpus_file_name)
    m_util.write_tree(corpus_tree, "/home/rdent/molyé20240808.xml")
    arrange_timeline(corpus_file_name)
    arrange_timeline("/home/rdent/molyé202408.xml")

if __name__ == '__main__':
    list_file = "../Molyé_list.tsv"
    main(list_file)

