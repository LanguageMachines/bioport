from bs4 import BeautifulSoup, Tag, NavigableString
from pathlib import Path
import urllib.request

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

# Extract articles from the given category
def scan(category):
    url = html_encode(f'{site}/wiki/Categoria:{category}')
    with urllib.request.urlopen(url) as connection:
        html = connection.read()
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('div', class_='mw-content-ltr')
    for link in content.find_all('a'):  # Iterate over all hyperlinks
        title = link.attrs.get('title')
        if not title: continue
        if ':' in title: continue
        if '/' in title: continue
        if title.endswith('(página não existe)'): continue
        articles.add(title)

# Setup
articles = set()  # The set of article titles we are building
categories = Path('../Data/categories.txt').read_text().splitlines()  # The categories to scan

# Scan all categories for articles
progress = len(categories)
for category in categories:
    progress -= 1
    print(f'\r{progress} ', end='', flush=True)
    scan(category)
print('\r')

# Write the output file
with open('../Data/articles.txt', 'w') as target:
    for article in sorted(articles):
        target.write(article)
        target.write('\n')
