# -*- coding: utf-8 -*-
import urllib3
import requests
import json

from bs4 import BeautifulSoup, NavigableString, Tag
from html.parser import HTMLParser
from html.entities import name2codepoint
import urllib

def GetAllDocsForOrg(org_name, court_type="vsrf", date_from="", date_to=""):
    csrftoken = None
    docs = []

    def MakeUrl(org_name, court_type, date_from, date_to, page=1):
        return 'https://sudact.ru/{court_type}/doc_ajax/?{court_type}-txt={text}&{court_type}-date_from={date_from}&{court_type}-date_to={date_to}&page={page}#searchResult'.format(
                court_type=court_type, text=urllib.quote(org_name), date_from=date_from, date_to=date_to, page=page)

    class VSRFParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            for attr in attrs:
                if (attr[0] == "href" and attr[1].find("_blank") != -1):	
            	    docs.append("https://sudact.ru" + attr[1].split("?")[0].strip("\\\""))

    def SendRequest(url, csrftoken):
        print(url)
        client= requests.session()
        client.get(url)

        if ((csrftoken is None) and ('csrftoken' in client.cookies)):
            csrftoken = client.cookies['csrftoken']

        http = urllib3.PoolManager()
        headers = {"Cookie": "csrftoken={}".format(csrftoken)}

        soup = None
        for i in range(10):  #rerequest
            r = http.request('GET', url, headers=headers)
            if (r.status == "404"):
                continue
            soup = BeautifulSoup(r.data, "html.parser")
            break

        return soup

    def ParseDoc(document, csrftoken):
        soup = SendRequest(document, csrftoken)

        text = ""
        for e in soup.recursiveChildGenerator():
            flag = True
            if isinstance(e, basestring):
                if ("Yandex" in e):
                    flag = False
                    break;
                text += e.strip()
            elif e.name == 'br':
                text += '\n'
            if (not flag):
                break
        return text

    for i in range(1, 2):
        soup = SendRequest(MakeUrl(org_name, court_type, date_from, date_to, i), csrftoken)
        if (soup == None):
            print("Error. Cannot send request")
            return

        parser = VSRFParser()
        parser.feed(soup.prettify())
    
    results = []
    for doc in docs:
        results.append(ParseDoc(doc, csrftoken))
    return results

import io
court_types = ["vsrf", "arbitral", "regular", "magistrate", "law"]
texts = GetAllDocsForOrg('газпром', court_type="arbitral")
with io.open('data.json', 'w', encoding='utf8') as outfile:
    data = json.dumps(texts, ensure_ascii=False, indent=4)
    outfile.write(unicode(data))

texts = []
with io.open('data.json', 'r', encoding='utf8') as infile:
    data = json.load(infile)
    for elem in data:
        raw_data = json.dumps(elem, ensure_ascii=False)
        #print(raw_data)
        if (u"Именем" in raw_data):
            raw_data = raw_data.split(u"Именем")[1]

        if (u"ИМЕНЕМ" in raw_data):
            raw_data = raw_data.split(u"ИМЕНЕМ")[1]

        texts.append(raw_data)

with io.open('data2.json', 'w', encoding='utf8') as outfile:
    data = json.dumps(texts, ensure_ascii=False, indent=4)
    data = data.replace('\\n', ' ').replace('\\\\n', ' ')

    outfile.write(unicode(data))

#for text in texts:

