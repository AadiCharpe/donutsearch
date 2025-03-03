import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
# starting urls
urls = ['https://www.wikipedia.org/']
# visited urls
visited = []
while urls:
    url = urls.pop()
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
    visited.append(url)
    # sleep so websites cant tell it's a bot
    time.sleep(1.5)
