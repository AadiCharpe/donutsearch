import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
# read info from file
f = open('index.txt', 'r')
lines = f.readlines()
f.close()
urls = lines[0].split('|')

visited = lines[1].split('|')
if visited[0] == '\n':
    visited.clear()
words = {}
for i in range(2, len(lines)):
    aline = lines[i].split('|')
    words[aline[0]] = aline[1]
pages = 1
cd = ''

def crawlable(url):
    canVisit = True
    relevant = False
    response = requests.get(urlparse(url).scheme + '://' + urlparse(url).netloc + '/robots.txt')
    disallowed = []
    for line in response.text.splitlines():
        if line == 'User-agent: *':
            relevant = True
        elif line.startswith('User-agent:') and line != 'User-agent: *':
            relevant = False
        if line.startswith('Disallow') and len(line.split()) > 1 and relevant:
            disallowed.append(line.split()[1])
    for path in disallowed:
        if urlparse(url).path.startswith(path):
            canVisit = False
            break
    if not canVisit:
        print('cant crawl ' + url + ' because of robots.txt')
    return canVisit

def index(url):
    # find all hyperlinks on page
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    for link in soup.find_all('a'):
        if link.get('href') is not None:
            if link.get('href').startswith('//'):
                if 'https:' + link.get('href') not in visited:
                    urls.append('https:' + link.get('href'))
            elif link.get('href').startswith('http'):
                if link.get('href') not in visited:
                    urls.append(link.get('href'))
    # scrape the text on the page
    texts = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])
    for t in texts:
        text = t.get_text(strip=True)
        for word in text.split():
            lower = word.lower()
            if len(lower) > 0 and lower.isalpha():
                if lower in words and url not in words[lower].split(','):
                    words[lower] += ',' + url
                else:
                    words[lower] = url

# limit of 100 pages per domain so my pc doesn't explode
while urls and pages <= 100:
    url = urls.pop(0)
    print('crawling: ' + url)
    # check robots.txt file to see if I can visit url
    if not crawlable(url):
        continue
    # reset page limit if new domain
    if urlparse(url).netloc != cd:
        pages = 1
    # index the page
    index(url)
    # save to file every 25 pages
    if pages % 25 == 0:
        f = open('index.txt', 'w', encoding="utf-8")
        f.write('|'.join(urls))
        f.write('|'.join(visited))
        for key in words.keys():
            f.write(key + '|' + words[key] + '\n')
        print('data saved')
        f.close()
    visited.append(url)
    cd = urlparse(url).netloc
    # sleep so websites cant tell it's a bot
    time.sleep(1.5)
    pages += 1
