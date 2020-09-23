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

def download(title):
    url = html_encode(f'{site}/wiki/{title}')
    try:
        with urllib.request.urlopen(url) as connection:
            html = connection.read()
            target = Path('../Data/HTML') / f'{title}.html'
            target.write_bytes(html)
    except urllib.error.HTTPError:
        print(title)

# Setup
articles = Path('../Data/articles.txt').read_text().splitlines()

# Download all articles
progress = len(articles)
for article in articles:
    progress -= 1
    print(f'\r{progress} ', end='', flush=True)
    download(article)
