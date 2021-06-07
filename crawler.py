import sys
import os
import re
import requests
from bs4 import BeautifulSoup
import csv
import json
import time


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

fff = open(outputFile, "w") #open brackets for json data
fff.write("[\n")
fff.close()

jsonData = []
urlQueue = []
duplicateList = []
currPage = 0

for seeds in seedUrls:
    urlQueue.append(seeds.rstrip())
    duplicateList.append(seeds.rstrip())
    currHop = 0
    while (currPage < maxPages) and (currHop < maxHops) and len(urlQueue) > 0:          #3 limits: exceeding max pages, exceeding max hops, empty url queue
        print("Crawling: " + str(urlQueue[0]))
        try:
            page = requests.get(urlQueue[0])
            soup = BeautifulSoup(page.content, 'html.parser')
            text = soup.get_text().replace("\n", " ").replace("\t", " ").replace("\r", " ")
            text = " ".join(re.findall(r'\w+(?:\.?\w+)*', text))
            title = str(soup.title).replace("<title>", "").replace("</title>", "")
            tempJson = {"title": title, "url": urlQueue[0], "text": text}
            realJson = json.dumps(tempJson)
            with open(outputFile, 'a') as ff:
                ff.writelines(realJson + "\n")
                ff.close()
            currPage += 1
            currHop += 1
            urlQueue.pop(0)
            for link in soup.find_all('a'):
                try:
                    if "http://" in link.get('href') or "https://" in link.get('href'):     #some links don't contain full url but http/s does
                        if link.get('href') not in duplicateList:
                            urlQueue.append(link.get('href'))
                            duplicateList.append(link.get('href'))
                except:
                    pass
        except:
            print("Error with crawling: " + str(urlQueue[0]))
            urlQueue.pop(0)
        time.sleep(1)
    """
    ### DEBUG ###
    for urls in urlQueue:
        print(urls)
    print(len(urlQueue))
    #############
    """
    urlQueue = []   #empty urlQueue to restart

with open(outputFile, 'a') as ffff: #close brackets for json data
    ffff.write("]")
    ffff.close()

print("DONE")
