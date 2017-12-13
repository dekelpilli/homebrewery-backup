import urllib.request
import sys
import os
import html2text
from tqdm import tqdm
import textwrap
import codecs
import datetime

def getPages(user):
    response = urllib.request.urlopen('http://homebrewery.naturalcrit.com/user/' + user)
    html = response.read().decode('utf-8')

    pages = []
    if "No Brews." in html:
        return pages

    htmlSplit = html.split("/share/")[1:]
    for p in htmlSplit:
        pages.append(p.split('"')[0])

    return pages

def getSource(page):
    response = urllib.request.urlopen('http://homebrewery.naturalcrit.com/source/' + page)
    charset = response.headers.get_content_charset()
    html = response.read()
    html = html.decode(charset, errors='ignore')
    
    html2text.BODY_WIDTH = 0
    md = html2text.html2text(html)[1:-3]
    
    
    md = textwrap.dedent(md).strip()
    
    return md

def writeMarkdownFiles(user, pages):
    baseDir = os.getcwd()+"/backups/"+user+datetime.datetime.now().strftime('-%d.%m.%y_%H-%M-%S')
    directory = baseDir + "/"
    copy = 1
    while os.path.exists(directory):
        directory = baseDir + "(Copy " + str(copy) + ")/"
        copy += 1
    os.makedirs(directory)
    for page in tqdm(pages):
        source = getSource(page)
        f = codecs.open(directory+page+".md", 'w', 'utf-8')
        f.write(source) 
        f.close()
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please enter your homebrewery username, like so:\n\thomebrewery-backup.py userNameHere")
    else:
        user = sys.argv[1]

    pages = getPages(user)

    writeMarkdownFiles(user, pages)
    
        
