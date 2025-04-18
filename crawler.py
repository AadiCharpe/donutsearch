import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
import threading
import re
# read info from file
fl = open('index.txt', 'r')
lines = fl.readlines()
fl.close()
tlist1 = lines[0].split('|')[0].split(',')
tlist2 = lines[0].split('|')[1].split(',')
tlist3 = lines[0].split('|')[2].split(',')
tlist4 = lines[0].split('|')[3].split(',')

visited = {}
u = ''
for value in lines[1].split('~'):
    if value.startswith('http'):
        u = value
    else:
        visited[u] = value
        u = ''
if '' in visited:
    del visited['']
words = {}
for i in range(2, len(lines)):
    aline = lines[i].split('|')
    words[aline[0]] = aline[1]

def valid(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except AttributeError:
        return False

def crawlable(url):
    canVisit = True
    relevant = False
    response = requests.get('https://' + urlparse(url).netloc + '/robots.txt')
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

def index(url, urlist):
    # find all hyperlinks on page
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    for link in soup.find_all('a'):
        if link.get('href') is not None:
            newlink = link.get('href')
            if newlink.startswith('//'):
                newlink = 'https:' + newlink
            elif newlink.startswith('/'):
                newlink = urlparse(url).netloc + newlink
            elif not newlink.startswith('http'):
                continue
            if '.wikipedia.org' in newlink and 'en.wikipedia.org' not in newlink:
                continue
            if newlink not in visited and valid(newlink):
                urlist.append(newlink)
    # scrape the text on the page
    texts = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a'])
    for t in texts:
        text = t.get_text(strip=True)
        for word in text.split():
            lower = word.lower()
            if len(lower) > 0 and re.fullmatch(r'^[a-zA-Z]+$', lower):
                if lower in words and url not in words[lower].split(','):
                    words[lower] += ',' + url
                else:
                    words[lower] = url
    meta = soup.find('meta', attrs={'name': 'description'})
    tt = soup.find('title')
    title = tt.get_text().strip() if tt else 'No Title'
    description = ''
    if meta and 'content' in meta.attrs:
        description = meta['content']
    return f'{title}`{description}'

def crawl(urlist, id):
    pages = 1
    cd = ''
    # limit of 15 pages per domain
    while urlist and pages <= 15:
        url = urlist.pop(0)
        print(f'thread {id} crawling: {url}')
        # check robots.txt file to see if I can visit url
        if not crawlable(url):
            continue
        # reset page limit if new domain
        if urlparse(url).netloc != cd:
            pages = 1
        # index the page
        visited[url] = index(url, urlist)
        cd = urlparse(url).netloc
        # sleep so websites cant tell it's a bot
        time.sleep(2)
        pages += 1
        # save to file every 5 pages
        if pages % 2 == 0:
            f = open('index.txt', 'w', encoding="utf-8")
            f.write('|'.join([','.join(tlist1), ','.join(tlist2), ','.join(tlist3), ','.join(tlist4)]) + '\n')
            string = ''
            for k, v in visited.items():
                string += f'{k}~{v}~'
            f.write(string[:-1] + '\n')
            for key in words.keys():
                f.write(key + '|' + words[key] + '\n')
            print('data saved')
            f.close()

t1 = threading.Thread(target=crawl, args=(tlist1, 1,))
t2 = threading.Thread(target=crawl, args=(tlist2, 2,))
t3 = threading.Thread(target=crawl, args=(tlist3, 3,))
t4 = threading.Thread(target=crawl, args=(tlist4, 4,))

t1.start()
t2.start()
t3.start()
t4.start()

t1.join()
t2.join()
t3.join()
t4.join()