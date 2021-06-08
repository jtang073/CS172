import sys
import os
import re
import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import urllib.parse
import urllib.robotparser

seedFile = ""
seedUrl = ""
maxPages = 0
maxHops = 0
outputFile = ""

if (len(sys.argv) == 5):
    seedFile = sys.argv[1]
    maxPages = int(sys.argv[2])
    maxHops = int(sys.argv[3])
    outputFile = sys.argv[4]
else:
    print("Please enter the following format: python3 crawler.py <seed-file> <number-of-pages> <number-of-hops> <output-file>")
    sys.exit()

with open(seedFile) as f:
    seedUrls = f.readlines()
    f.close()

fff = open(outputFile, "w")     #create/replace new output file
fff.close()

jsonData = []
urlQueue = []
duplicateList = []
currPage = 0

for seeds in seedUrls:
    urlQueue.append(seeds.rstrip())
    duplicateList.append(seeds.rstrip())
    currHop = 0
    while (currPage < maxPages) and (currHop < maxHops) and len(urlQueue) > 0:      #3 limits: exceeding max total pages, exceeding max seed hops, or empty url queue from seed
        print("Crawling: " + str(urlQueue[0]))
        duplicateList.append(urlQueue[0])
        try:
            ########### Reading Robots.txt ###########
            numSlashes = 0
            robotUrl = ""
            for chars in urlQueue[0]:
                if numSlashes < 3:
                    if chars in '/':
                        numSlashes += 1
                    robotUrl += chars
            if robotUrl[-1] not in '/':
                robotUrl += '/'
            robotUrl = robotUrl + "robots.txt"
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robotUrl)
            rp.read()
            """
            ### DEBUG ###
            print("Reading: " + str(robotUrl))
            #############
            """
            ##########################################
            if rp.can_fetch("*", urlQueue[0]):
                try:
                    domain = urllib.parse.urlparse(urlQueue[0]).netloc
                    page = requests.get(urlQueue[0])
                    soup = BeautifulSoup(page.content, 'html.parser')
                    text = soup.get_text().replace("\n", " ").replace("\t", " ").replace("\r", " ")
                    text = " ".join(re.findall(r'\w+(?:\.?\w+)*', text))
                    title = str(soup.title).replace("<title>", "").replace("</title>", "")
                    tempJson = {"html": "<html> <body> " + str({"title": title, "url": urlQueue[0], "text": text}) + " </body> </html>"}
                    realJson = json.dumps(tempJson)
                    indexJson = json.dumps({"index": {}})
                    with open(outputFile, 'a') as ff:
                        ff.writelines(indexJson + "\n")
                        ff.writelines(realJson + "\n")
                        ff.close()
                    currPage += 1
                    currHop += 1
                    for link in soup.find_all('a'):
                        try:
                            if "http://" in link.get('href') or "https://" in link.get('href'):     #some links don't contain full url but http/s does
                                if link.get('href') not in duplicateList:
                                    urlQueue.append(link.get('href'))
                                    #duplicateList.append(link.get('href'))
                        except:
                            pass        #skip over all <a> headers with no href links
                except:
                    print("Error with crawling: " + str(urlQueue[0]))       #Errors with requests.get (ie: uncrawlable page or 404 etc)
                time.sleep(1)       #Delay 1 second so we don't access sites too fast
            else:
                print("Warning: Robots.txt disallowed crawling: " + str(urlQueue[0]))
        except:
            print("Error: Skipping URL because there was an error with with loading " + urlQueue[0])      #skip to be safe
        urlQueue.pop(0)     #remove first in queue whether crawl was successful or not
    """
    ### DEBUG ###
    for urls in urlQueue:
        print(urls)
    print(len(urlQueue))
    #############
    """
    urlQueue = []       #empty urlQueue to restart

print("DONE")
