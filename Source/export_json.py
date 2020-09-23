import datetime
import json
from pathlib import Path
import re
import urllib.request
from bs4 import BeautifulSoup, Tag, NavigableString

site = 'https://en.wikipedia.org'

def extract_text(html):
    article = []
    soup = BeautifulSoup(html, 'html.parser')
    body = soup.find('div', id='content')
    h1 = body.find('h1')
    article.append(f'# {h1.string}')
    content = body.find('div', class_='mw-parser-output')
    # Extract headings and body text
    for child in content.contents:
        if not isinstance(child, Tag): continue
        match = re.match('h([123456789])', child.name)
        if (match):
            level = int(match.group(1)) - 1
            frags = list(child.stripped_strings)
            if frags[-3:] == ['[', 'edit', ']']:
                frags = frags[:-3]
            article.append(f'{level*"#"} {" ".join(frags)}')
        elif child.name == 'p':
            paragraph = ' '.join(child.stripped_strings)
            article.append(paragraph)
    # Clean up the text
    clean_article = []
    for item in article:
        # Remove brackets, like footnotes [1] and edit controls [editar]
        item = re.sub(' *\[[^]]*\] *', ' ', item)
        # Remove spaces around punctuation
        for punct in '.,!?)':
            item = item.replace(' '+punct, punct)
        for punct in '(':
            item = item.replace(punct+' ', punct)
        # Remove newlines
        item = item.replace('\n', ' ')
        # Remove trailing spaces
        item = item.strip()
        clean_article.append(item)
    return clean_article

def wikidata_url(html):
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        title = link.attrs.get('title')
        if not title: continue
        if title.startswith('wikidata:'):
            wikidata_id = title[9:]
            return f'https://www.wikidata.org/wiki/{wikidata_id}'
    return None

def wikipedia_categories(html):
    categories = []
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        title = link.attrs.get('title')
        if not title: continue
        if not title.startswith('Categoria:'): continue
        category = title[10:]
        if category.startswith('!'): continue
        categories.append(category)
    return categories

def export(article):
    html = article.read_bytes()
    data = {
        'extraction-date': timestamp,
        'wikidata-url': wikidata_url(html),
        'wikipedia-url': f'https://pt.wikipedia.org/wiki/{article.stem}',
        'wikipedia-title': article.stem,
        'wikipedia-categories': wikipedia_categories(html),
        'page-content': extract_text(html)
    }
    json_path = Path('../Data/JSON') / f'{article.stem}.json'
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=4))

timestamp = datetime.date.today().isoformat()
articles = list(Path('../Data/HTML').glob('*.html'))
progress = len(articles)
for article in articles:
    progress -= 1
    print(f'\r{progress} ', end='', flush=True)
    export(article)
