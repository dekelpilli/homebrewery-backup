import urllib.request
import sys
import os
import html2text
from tqdm import tqdm
import textwrap
import codecs
from datetime import datetime


class Brew:
    def __init__(self, name=None, share_id=None):
        self.name = name
        self.shareId = share_id

    def set_share_id(self, share_id):
        self.shareId = share_id

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def get_share_id(self):
        return self.shareId

    def __str__(self):
        return "Name: " + str(self.name) + "\nID: " + str(self.shareId) + "\n-------------------"

    def get_summary(self):
        return self.name + " - " + self.shareId 


def get_pages(user):
    response = urllib.request.urlopen('http://homebrewery.naturalcrit.com/user/' + user)
    html = response.read().decode('utf-8')

    pages = []
    if "No Brews." in html:
        return pages

    # separate each brew's html text into one list item
    html_split = html.split('"brewItem">')[1:]
    for brew in html_split:
        # gets the brew name from the user page
        name = brew.split("<h2>")[1].split("</h2>")[0]
        # get share id for current brew
        share_id = brew.split("/share/")[1:][0].split('"', 1)[0]

        brew_item = Brew(name, share_id)
        pages.append(brew_item)
    return pages


def get_source(brew):
    response = urllib.request.urlopen('http://homebrewery.naturalcrit.com/source/' + brew.get_share_id())
    charset = response.headers.get_content_charset()
    html = response.read()
    html = html.decode(charset, errors='ignore')

    html2text.BODY_WIDTH = 0
    md = html2text.html2text(html)[1:-3]  # remove whitespace
    md = textwrap.dedent(md).strip()  # remove indentation

    return md


def write_markdown_files(user, brews):
    # folder name based on user name and date
    base_dir = os.getcwd() + "/backups/" + user + datetime.now().strftime('-%d.%m.%y_%H-%M-%S')
    directory = base_dir + "/"
    copy = 1
    while os.path.exists(directory):  # make 100% sure folder doesn't overwrite current files
        directory = base_dir + "(Copy " + str(copy) + ")/"
        copy += 1
    os.makedirs(directory)
    for brew in tqdm(brews):
        source = get_source(brew)
        f = codecs.open(directory + brew.get_summary() + ".md", 'w', 'utf-8')
        f.write(source)
        f.close()


if __name__ == "__main__":
    user_name = None
    if len(sys.argv) < 2:
        print("Please enter your homebrewery username, like so:\n\thomebrewery-backup.py userNameHere")
        exit(1)
    else:
        user_name = str(sys.argv[1])

    pages = get_pages(user_name)

    write_markdown_files(user_name, pages)
