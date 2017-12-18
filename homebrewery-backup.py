import urllib.request
import sys
import os
import html2text
from tqdm import tqdm
import textwrap
import codecs
import datetime

class Brew:
    def __init__(self, name=None, shareId=None):
        self.name = name
        self.shareId = shareId

    def setShareId(self, shareId):
        self.shareId = shareId

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def getShareId(self):
        return self.shareId

    def __str__(self):
        return "Name: " + str(self.name) + "\nID: " + str(self.shareId) + "\n-------------------"

    def getDescription(self):
        return self.name + " - " + self.shareId 

def getPages(user):
    response = urllib.request.urlopen('http://homebrewery.naturalcrit.com/user/' + user)
    html = response.read().decode('utf-8')

    pages = []
    if "No Brews." in html:
        return pages

    htmlSplit = html.split('"brewItem" data-reactid="')[1:]
    for brew in htmlSplit:
        reactId = int(brew.split('"')[0])
        name = brew.split('<h2 data-reactid="'+str(reactId+1)+'">')[1].split('</h2>')[0]
        shareId = brew.split("/share/")[1:][0].split('"')[0]

        brewItem = Brew(name, shareId)
        pages.append(brewItem)

    for p in pages:
        print(p)
    
##    htmlSplit = html.split("/share/")[1:]
##    for p in htmlSplit:
##        pages.append(p.split('"')[0])

    return pages

def getSource(brew):
    response = urllib.request.urlopen('http://homebrewery.naturalcrit.com/source/' + brew.getShareId())
    charset = response.headers.get_content_charset()
    html = response.read()
    html = html.decode(charset, errors='ignore')
    
    html2text.BODY_WIDTH = 0
    md = html2text.html2text(html)[1:-3]
    
    
    md = textwrap.dedent(md).strip()
    
    return md

def writeMarkdownFiles(user, brews):
    baseDir = os.getcwd()+"/backups/"+user+datetime.datetime.now().strftime('-%d.%m.%y_%H-%M-%S')
    directory = baseDir + "/"
    copy = 1
    while os.path.exists(directory):
        directory = baseDir + "(Copy " + str(copy) + ")/"
        copy += 1
    os.makedirs(directory)
    for brew in tqdm(brews):
        source = getSource(brew)
        f = codecs.open(directory+brew.getDescription()+".md", 'w', 'utf-8')
        f.write(source) 
        f.close()
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please enter your homebrewery username, like so:\n\thomebrewery-backup.py userNameHere")
        exit(1)
    else:
        user = str(sys.argv[1])

    pages = getPages(user)

    writeMarkdownFiles(user, pages)
    
        
