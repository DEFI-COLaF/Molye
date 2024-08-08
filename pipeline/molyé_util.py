# -*- coding: utf-8 -*-
from lxml import etree
from lxml import etree as ET
import csv
import os
import io
import glob
import json
import ast
import regex as re
import pandas as pd

import requests
from bs4 import BeautifulSoup
import roman
import PyPDF2

import nltk
import metadata_patterns
nltk.download('punkt')

def load_works(list_file):
    works = []
    with open(list_file) as f:
        lines = csv.DictReader(f, delimiter="\t", quotechar='"')
        for line in lines:
            works.append(line)
    return works

def read_file(filename, mode="r"):
    file_text = ""
    with open(filename, mode=mode) as f:
        file_text = f.read()
    return file_text


def create_directory(directory_path):
    """
    Verify the existence of a directory. If it does not exist, create it.

    Parameters:
    - directory_path (str): The path of the directory to be checked/created.
    """
    try:
        # Check if the directory exists
        if not os.path.exists(directory_path):
            # If not, create the directory
            os.makedirs(directory_path)
        else:
            pass
    except Exception as e:
        print(f"Error: {str(e)}")

def handle_web_error(response):
    # Print an error message if the request was not successful
    error_message = response.status_code
    print(f"Error: {error_message}")
    log_filename = "errors.txt"
    with open(log_filename, "a") as log_file:
        # Append the error message along with the current timestamp
        log_file.write(f"{error_message}\n")
        print(f"Error logged to '{log_filename}'.")
    return None

def get_html_content(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        # Check if the request was successful (status code 200)

        if response.status_code == 200:
            # Return the web content
            return str(response.text)

        else:
            return handle_web_error(response)
    except Exception as e:

        # Print an error message if an exception occurs
        print(f"Exception: {str(e)}")
        return None


def divide_xml_content(full_file):
    soup = BeautifulSoup(full_file, 'xml')
    header = str(soup.find("teiHeader"))
    text = str(soup.find("text"))
    front = str(soup.find("front"))
    body = str(soup.find("body"))
    return header, text, front, body

def remove_tags(s):
    return re.sub("<.*?>", "", s)
"""Extract the tags"""

def convert_roman_year(raw_date):
    numeral_pattern = r"[MDLCXVI\.\s]+"
    roman_year = re.search(numeral_pattern, raw_date)[0]
    roman_year = re.sub(r"\W", "", roman_year)
    return roman.fromRoman(roman_year)

def extract_date(raw_date):
    date = ""
    try:
        if raw_date["value"]:
            date = str(raw_date["value"])
        else:
            date = str(convert_roman_year(remove_tags(str(raw_date.text))))
    except Exception as e:
        print(f"{raw_date.text} has a {e}")
        date = "date_error"
    return date
#clear multiple folders (useful for changing names/ids)
def clear_folders(folders):
    for folder in folders:
        files = glob.glob(f"{folder}/*")
        for file in files:
            os.remove(file)


#create multiple folders at once
def create_folders(folders):
    for folder in folders:
        create_directory(folder)


def prepare_folders(folders):
    create_folders(folders)
    clear_folders(folders)

def read_pdf_object(pdfReader, start=0, end=-1):
    all_text = ""
    for page in pdfReader.pages[start:end]:
        all_text = all_text + page.extract_text()
    return all_text

def extract_web_pdf(url, pages=(0,-1)):
    doc_obj = requests.get(url, headers = {'User-Agent': 'Me 2.0'})
    doc_bytes = doc_obj.content
    pdfReader = PyPDF2.PdfReader(io.BytesIO(doc_bytes), "rb")
    all_text = read_pdf_object(pdfReader, start=pages[0], end=pages[1])
    return all_text

#TODO consider rewriting with a parser at some point
def simple_tag_replace(s, old, new):
    return re.sub(fr"(</?){old}>", fr"\1{new}>", s)

def remove_attrs(s, tag):
    return re.sub(fr"<{tag}.*?>", fr"<{tag}>", s)

def remove_tag(s, tag):
    return re.sub(fr"(</?){tag}.*?>", fr"", s)


#Titles should not have whitespace or punctuation
def format_title(title_string):
    title_string=title_string.strip()
    title_string = re.sub(r"\W", "_", title_string)
    title_string = re.sub(r"_{2,}", "_", title_string)
    return title_string

#Checks that a pattern does not use reserved characters requring special treatment
def is_basic_ngram(disjunctive_ngram):
    reserved = "$^"
    return len([c for c in disjunctive_ngram if not c in reserved]) == len(disjunctive_ngram)

#Convert a plain text disjunctive ngram into a bounded regex pattern
def expand_disjunctive(disjunctive_ngram):
    disjunctive_regex = ""
    if is_basic_ngram(disjunctive_ngram):
        first = disjunctive_ngram[0]
        disjunctive_regex = fr"\b[{first.upper()}{first}]{disjunctive_ngram[1:]}[\b\W]"
    return disjunctive_regex

def check_string(text, disjunctive_list):
    for n_gram in disjunctive_list:
        if n_gram in text:
            return True
    return False

def check_string_regex(text, disjunctive_list):
    for n_gram in disjunctive_list:
        if re.search(n_gram, text):
            return True
    return False

#basic unit of text in TEI
def check_paragraphs(paragraphs, disjunctive):
    interesting_paragraphs = []
    for paragraph in paragraphs:
        text = paragraph.text
        if check_string_regex(text, disjunctive):
            interesting_paragraphs.append(paragraph)
    return interesting_paragraphs

def check_lines(interesting_paragraphs, disjunctive_regex):
    interesting_lines = []
    for paragraph in interesting_paragraphs:
        p_text = paragraph.text
        lines = nltk.tokenize.sent_tokenize(p_text, "french")
        for line in lines:
            if check_string_regex(line, disjunctive_regex):
                interesting_lines.append(line)

    return interesting_lines

#Extract lines by language at either <sp> or <p> level
def get_lines_of_interest(file_text, langs, level="p"):
    soup = BeautifulSoup(file_text, features="xml")
    matches = soup.find_all(level, attrs={"xml:lang": langs})
    #trick to get an ordered set
    matches = list(dict.fromkeys([match.parent if match.name == "s" else match for match in matches ]))
    #inserts namespace unnecessarily
    return [ str(m).replace("tei:", "") for m in matches]

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
def check_lines_direct(text, disjunctive):
    soup = BeautifulSoup(text, features="xml")
    paragraphs = soup.find_all("p")
    expanded_disjunctive = [expand_disjunctive(n) for n in disjunctive]
    interesting_paragraphs = check_paragraphs(paragraphs, expanded_disjunctive)
    interesting_lines = check_lines(interesting_paragraphs, expanded_disjunctive)
    return interesting_lines

def fix_tei_tag(soup):
    return str(soup).replace("tei:", "")


#A trick to handle xml namespace
def write_tree(tree, out_name):
    out = ET.tostring(tree, encoding="unicode").replace("XMLID", "xml:id")
    ET.ElementTree(ET.fromstring(out)).write(out_name, xml_declaration=True, encoding="UTF-8", pretty_print=True)

def find_converted_file(title, folder):
    filename = f"{format_title(title)}.xml"
    if filename in os.listdir(folder):
        return f"{folder}/{filename}"
    else:

        print(f"{filename} not found")

#Get a subnode arbitrarily deep
def get_et_node(root, node_name):
    for n in root.iter(node_name):
        return n