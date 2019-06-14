#-*- coding: utf-8 -*-
import json
import io
import pandas as pd
import numpy as np
import string
from textblob import TextBlob

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.set_option('display.expand_frame_repr', False)

data = {}
with io.open('data2.json', 'r', encoding='utf8') as infile:
    texts = json.load(infile)
    data["text"] = np.array(texts)

import nltk

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


stop_words = set(stopwords.words('russian'))
data["without_punct"] = []
for text in data["text"]:
    tokens = word_tokenize(text.strip())
    data["without_punct"].append([i for i in tokens if not i in stop_words])

def Shtraf(tokens):
    result = []
    for i, token in enumerate(tokens):
        if (i > 0 and token == u"""руб"""):
            summa = 0
            j = i
            step = 1
            while(j > 0 and tokens[j - 1].isdigit() and int(tokens[j - 1]) < 1000):
                summa = summa + step * int(tokens[j - 1])
                step *= 1000
                j -= 1
            result.append(summa)
    return result

#df['char_count'] = df['text'].str.len()
data["shtraf"] = []
for ind, i in enumerate(data["without_punct"]):
    data["shtraf"].append(Shtraf(i))

import re
p = [
    re.compile(u".взыск.+(неуст|штраф)."),
    re.compile(u".нарушен.+(договор|соглашение|решение)."),
    re.compile(u"\d{2}\.\d{2}\.\d{4}")    
]

data["factors"] = {}
from datetime import date,datetime
for i, text in enumerate(data["text"]):
#    print(text)
    
    data["factors"][i] = []
    for j in range(len(p)):
        founded = p[j].findall(text)
        if (len(founded) > 0):
            if (j == 0):
                data["factors"][i].append(max(data["shtraf"][i]))
            if (j == 1):
                data["factors"][i].append(1)
            if (j == 2):
                dates = []
                for date_f in founded:
                    date_convert =datetime.strptime(date_f, "%d.%m.%Y").strftime("%Y-%m-%d")
                    if int(date_convert[:4]) < 2010:
                        dates.append("2010-01-01")
                    else:
                        dates.append(datetime.strptime(date_f, "%d.%m.%Y").strftime("%Y-%m-%d"))
                if dates:
                    data["factors"][i].append((
                        datetime.strptime(max(dates), "%Y-%m-%d")-
                        datetime.strptime(min(dates), "%Y-%m-%d")).days)
                else:
                    data["factors"][i].append(0)
        else:
            data["factors"][i].append(0) 

print(data["factors"])


#    print(data["shtraf"][i])
