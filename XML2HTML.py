import os
from lxml import etree

# Paths for your XML files, XSL file, and output HTML folder
xml_folder = 'dataset_colaf/'
xsl_file = 'XML2HTML_doc.xsl'
output_folder = 'dataset_HTML/'
index_file = os.path.join(output_folder, 'index.html')

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Load the XSLT file
xslt_root = etree.parse(xsl_file)
transform = etree.XSLT(xslt_root)

content=[]

# Iterate over each XML file in the directory
for xml_subfolder in os.listdir(xml_folder):
    for xml_filename in os.listdir(xml_folder+'/'+xml_subfolder):
        if xml_filename.endswith('.xml'):
            xml_path = os.path.join(xml_folder, xml_subfolder, xml_filename)
            html_filename = os.path.splitext(xml_filename)[0] + '.html'
            output_html_path = os.path.join(output_folder, html_filename)

            # Parse the XML file
            xml_root = etree.parse(xml_path)

            # Transform the XML to HTML using the XSL file
            result_tree = transform(xml_root)

            # Save the HTML result
            with open(output_html_path, 'wb') as f:
                f.write(etree.tostring(result_tree, pretty_print=True, method='html'))

            # Extract the title from the HTML (assuming <title> element is created)
            title = xml_root.find('.//tei:title[@type="main"]', namespaces={"tei":"http://www.tei-c.org/ns/1.0"}).text
            date = xml_root.find('.//tei:bibl[@type="PrintSource"]/tei:date', namespaces={"tei": "http://www.tei-c.org/ns/1.0"}).attrib['when']
            langue_xml = xml_root.findall('.//tei:language/tei:name', namespaces={"tei": "http://www.tei-c.org/ns/1.0"})
            langue=[]
            for lang in langue_xml:
                if 'Metropolitan France' not in lang.text:
                    langue.append(lang.text)
            keywords_xml = xml_root.findall('.//tei:term', namespaces={"tei":"http://www.tei-c.org/ns/1.0"})
            keywords = []
            for key in keywords_xml:
                keywords.append(key.text)
            # Append the title and corresponding HTML file to the list for the index
            xml_path = xml_folder+xml_subfolder+'/'+xml_filename
            content.append([title, html_filename, langue, keywords, xml_path, xml_subfolder, date])

# Create the page d'accueil (index.html)
with open(index_file, 'w', encoding='utf-8') as f:
    f.write("""<!DOCTYPE html>\n<html>\n<head>\n<title>Corpus Page d\'Accueil</title><style>
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 18px;
            font-family: Arial, sans-serif;
            text-align: left;
        }
        
        th, td {
            padding: 12px 15px;
            border: 1px solid #ddd;
        }

        th {
            background-color: #4CAF50;
            color: white;
        }

        tr:nth-child(even) {
            background-color: #f2f2f2;
        }

        tr:hover {
            background-color: #ddd;
        }

        caption {
            caption-side: top;
            font-size: 1.5em;
            margin-bottom: 10px;
            font-weight: bold;
        }
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 20px;
            background-color: #f4f4f4;
            color: #333;
        }

        h1 {
            color: #2c3e50;
            font-size: 2.5em;
            text-align: center;
            margin-bottom: 20px;
        }

        p {
            font-size: 1.2em;
            margin-bottom: 20px;
        }

        a {
            color: #2980b9;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }
                .container {
            max-width: 800px;
            margin: auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }

    </style>""")
    f.write("""<h1>Molyé Corpus</h1>\n<div class="container"><p>The Molyé corpus is a diachronic collection of stereotypical representation of French language variation during the early modern period as well as early attestations of French Creoles.</p>
<p>The goal of the project is to demonstrate that several Creole features which are posited to be the result of pidginization in French colonies can in fact be traced to Europe, both individually and in combination with each other.</p>
<p>Below is a spreadsheet detailing both <a href="https://docs.google.com/spreadsheets/d/e/2PACX-1vS43h47Gq3x6F_qt5DoByeztvZJSkifAOsuLNuVsbawh8KHlrpRbX29CAEsruipmLZd7ugA3_GoQDZk/pubhtml">the contents of the Molyé corpus proper and the full list of 250+ documents</a> that were found in the corpus creation process.</p>
 <p>This work has been done as part of the <a href="https://colaf.huma-num.fr/">COlaF</a> project, Corpus and Tools for the Languages of France, developed by <a href="https://www.inria.fr/en">Inria</a>.</p>
</div>
<table><caption>Corpus Content\n""")
    f.write("""<thead>
    <tr>
    <th>SubCorpus
    </th><th>Title</th>
    <th>Date</th>
                <th>Languages</th>
                <th>Genres</th>
                <th>Links</th>
                </tr></thead><tbody>\n""")  # Table headers

    content_sorted_by_date = sorted(content, key=lambda x: x[6])
    for sublist in content_sorted_by_date:
        f.write(f'<tr><td>{sublist[5]}</td><td>{sublist[0]}<td>{sublist[6]}</td><td>{",".join(sublist[2])}</td><td>{",".join(sublist[3])}</td><td><a href="{sublist[1]}">HTML</a>,<a href="https://github.com/DEFI-COLaF/Molye/tree/main/{sublist[4]}">XML</a></td></tr>\n')

    f.write("""<tbody></table></body>\n</html>""")
