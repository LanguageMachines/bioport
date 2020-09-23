import csv
import urllib.request
from bs4 import BeautifulSoup, Tag, NavigableString
from pathlib import Path

site = 'https://pt.wikipedia.org'

def html_encode(text):
    letters = []
    for byte in text.encode('utf-8'):
        if byte == 0x20:  # Space
            letter = '_'
        elif 0x20 <= byte <= 0x7E:  # Printable ASCII range
            letter = chr(byte)
        else:  # Non-ASCII
            letter = f'%{byte:02X}'
        letters.append(letter)
    return ''.join(letters)

# Extract all subcategories from the given category
def scan(category):
    if category in categories: return  # Has the category been scanned before?
    categories.add(category)
    url = f'{site}/wiki/Categoria:{category}'
    with urllib.request.urlopen(html_encode(url)) as connection:
        html = connection.read()
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):  # Iterate over all hyperlinks
        title = link.attrs.get('title')
        if not title: continue
        if title == 'Especial:Categorias': break
        if not title.startswith('Categoria:'): continue
        subcat = title[10:]
        if subcat.startswith('!'): continue
        if subcat.startswith('Imagens'): continue
        if subcat.endswith('(página não existe)'): continue
        todo.append(subcat)

# Setup
categories = set()  # The set of category titles we are building
todo = ['Portugueses_por_ocupação']  # Categories we need to scan for subcategories

# Scan all categories
while todo:
    print(len(categories), end='\r', flush=True)  # Progress indicator
    category = todo.pop()  # Get an unscanned category
    scan(category)         # ... and scan it for subcategories

# Write the output file
with open('../Data/categories.txt', 'w') as target:
    for category in sorted(categories):
        target.write(category)
        target.write('\n')
