#MIT License
#
#Copyright (c) 2019 Saeid
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import hazm
import json
import re
from collections import Counter
from typing import Callable
stop_words = []
with open('stop_words.txt') as sw_file:
    for line in sw_file:
        stop_words.append(line.rstrip())
# print(stop_words)


def bagify(doc):
    normalizer = hazm.Normalizer()
    tokenize = hazm.word_tokenize
    word_list = re.sub(r"(&...;|&....;|(\d))|'|{|}|!", " ", doc)
    #stemmer = hazm.Stemmer()
    tokens = tokenize(normalizer.normalize(word_list))
    #tokens = [stemmer.stem(x) for x in tokens ]
    doc_list = [x for x in tokens if x not in stop_words]
    doc_set = set(doc_list)
    doc_bag = Counter({k:doc_list.count(k) for k in doc_set})
    return doc_bag

def get_bag(news_object, class_key_name , filter:Callable):
    obj = json.loads(news_object)
    doc = obj['title'] + obj['body']
    return bagify(doc), filter(obj[class_key_name]).rstrip().lstrip()

def get_classes(file, class_key_name, filter:Callable):
    tags = Counter()
    with open(file) as f:
        for line in f:
            obj = json.loads(line)
            try:
                res = obj[class_key_name]
            except:
                res=""
            tags += Counter({filter(res).rstrip().lstrip():1})
    return tags

