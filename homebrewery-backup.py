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

    def getSummary(self):
        return self.name + " - " + self.shareId 

def getPages(user):
    response = urllib.request.urlopen('http://homebrewery.naturalcrit.com/user/' + user)
    html = response.read().decode('utf-8')

    pages = []
    if "No Brews." in html:
        return pages

    htmlSplit = html.split('"brewItem" data-reactid="')[1:] #separate each brew's html text into one list item
    for brew in htmlSplit:
        reactId = int(brew.split('"',1)[0]) #internal html react id, only useful for constructing the next string
        name = brew.split('<h2 data-reactid="'+str(reactId+1)+'">',1)[1].split('</h2>')[0] #gets the brew name from the user page
        shareId = brew.split("/share/")[1:][0].split('"',1)[0] #get share id for current brew

        brewItem = Brew(name, shareId)
        pages.append(brewItem)
    return pages

def getSource(brew):
    response = urllib.request.urlopen('http://homebrewery.naturalcrit.com/source/' + brew.getShareId()) 
    charset = response.headers.get_content_charset()
    html = response.read()
    html = html.decode(charset, errors='ignore')
    
    html2text.BODY_WIDTH = 0
    md = html2text.html2text(html)[1:-3] #remove whitespace
    
    
    md = textwrap.dedent(md).strip() #remove indentation
    
    return md

def writeMarkdownFiles(user, brews):
    baseDir = os.getcwd()+"/backups/"+user+datetime.datetime.now().strftime('-%d.%m.%y_%H-%M-%S') #folder name based on user name and date
    directory = baseDir + "/"
    copy = 1
    while os.path.exists(directory): #make 100% sure folder doesn't overwrite current files
        directory = baseDir + "(Copy " + str(copy) + ")/" 
        copy += 1
    os.makedirs(directory)
    for brew in tqdm(brews):
        source = getSource(brew)
        f = codecs.open(directory+brew.getSummary()+".md", 'w', 'utf-8')
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
    
        
