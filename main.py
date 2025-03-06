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
words = {}
for i in range(2, len(lines)):
    line = lines[i].split('|')
    words[line[0]] = line[1]
pages = 1
while urls:
    url = urls.pop(0)
    print('crawling: ' + url)
    # check robots.txt file to see if I can visit url
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
        continue
    # find hyperlinks on website
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    for link in soup.find_all('a'):
        if link.get('href') is not None:
            if link.get('href').startswith('//'):
                if 'https:' + link.get('href') not in visited:
                    urls.append('https:' + link.get('href'))
            elif link.get('href').startswith('http'):
                if link.get('href') not in visited:
                    urls.append(link.get('href'))
    # scrape the text on the website
    texts = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])
    for t in texts:
        text = t.get_text(strip=True)
        if text in words and url not in words[text].split(','):
            words[text] += ',' + url
        else:
            words[text] = url
    # save to file every 25 pages
    if pages % 25 == 0:
        pages = 1
        f = open('index.txt', 'w', encoding="utf-8")
        f.write('|'.join(urls) + '\n')
        f.write('|'.join(visited) + '\n')
        for key in words.keys():
            f.write(key + '|' + words[key] + '\n')
        print('data saved')
        f.close()
    visited.append(url)
    # sleep so websites cant tell it's a bot
    time.sleep(1.5)
    pages += 1
