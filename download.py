# -*- coding: utf8 -*-
import urllib
import os
import sys
import re
import time
from BeautifulSoup import BeautifulSoup

defaulterror = "Ooooops!\nPlease Check Arguments.\npython download.py url|id.\n"

def download_photo(photoURL, savepath='.' + os.sep + 'default'):
    """
    Download the photo by the 'photoURL',
    save it into 'savepath'
    """
    photostream = urllib.urlopen(photoURL)
    photoname = str(photoURL.split('/')[-1:][0])

    if os.path.exists(savepath) == False:
        os.makedirs(savepath)
    savepath = savepath + os.sep + photoname
    with open(savepath, 'wb') as stream:
        stream.write(photostream.read())


def get_html(URL):
    """
    Get html source code form the 'URL'
    """
    htmlreader = urllib.urlopen(URL)
    html = htmlreader.read()
    return html

def get_albumname():
    """
    Get album's name that use for the directory's name(current time)
    """
    albumname = time.strftime("%H_%M_%S", time.localtime())
    return albumname

def parse_html(html):
    """
    Get next page and every photo's url
    """

    soup = BeautifulSoup(html)
    nextURL = str(soup.findAll(attrs={"class": "next"}))
    regex = re.compile("href=\"(.*)\"")
    nextURL = regex.findall(nextURL)
    
    if(len(nextURL) != 0):
        nextURL = nextURL[0]
    else:
        nextURL = None
    photolist = []
    for photoitem in soup.findAll(attrs={"class": "photo_wrap"}):
        photoitem = str(photoitem)
        regex = re.compile("img src=\"(.*)\"")
        photoURL = regex.findall(photoitem)[0]
        photolist.append(photoURL)
    return nextURL, photolist

def error_report(error):
    """
    Some argument or URL maybe wrong and report an error.
    """
    sys.stderr.write(error)
    sys.exit(1)

def check_URL(albumURL):
    """
    Check the URL if it is right.
    """
    regex = re.compile('[0-9]*$')
    if regex.match(albumURL):
        albumURL = 'http://www.douban.com/photos/album/%s/' % albumURL
    regex = re.compile('http://www.douban.com/photos/album/[0-9]*/')
    if regex.match(albumURL) == None:
        error_report("the URL '%s' is wrong." % albumURL)

    html = get_html(albumURL)
    soup = BeautifulSoup(html)
    if soup.html.title.string == u'页面不存在':
        error_report("the album '%s' does not exist." % albumURL)
    return albumURL

def main(albumURL):
    html = get_html(albumURL)
    albumname = get_albumname()
    savepath = '.' + os.sep + albumname

    allphotolist = []

    while True:
        nextURL, photolist = parse_html(html)
        for photoURL in photolist:
        	allphotolist.append(photoURL)
        if(nextURL == None):
            break
        html = get_html(nextURL)
    count, total = 1, len(allphotolist)
    for photoURL in allphotolist:
        download_photo(photoURL, savepath)
        print count, '/', total, '\tDone\n'
        count += 1
        time.sleep(0.8)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        error_report(defaulterror)
    albumURL = sys.argv[1]
    albumURL = check_URL(albumURL)
    main(albumURL)
