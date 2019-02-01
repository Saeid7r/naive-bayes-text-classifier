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

import sqlite3
from math import log
#database = 'task3.db'
from preprocess import bagify
import json
import re
class Classifier():
    def __init__(self, database):
        self.__database = database
        self.__classes = self.__get_classes()
 
    def __get_classes(self):
        classes = []
        with sqlite3.connect(self.__database) as conn: 
            cur = conn.cursor()
            cur.execute("SELECT class FROM class_count")
            for i in cur:
                classes.append(i[0])
        return classes

    def likelihood(self, word, clazz):
        with sqlite3.connect(self.__database) as conn:
            cur = conn.cursor()
            #print("SELECT {} FROM frequency WHERE word='{}';".format( clazz, word))
            cur.execute("SELECT `{}` FROM frequency WHERE word='{}';".format(clazz, word))
            x = cur.fetchone()
            x = (0,) if x==None else x
            cur.execute("SELECT SUM(`{}`) FROM frequency;".format(clazz))
            c = cur.fetchone()
            cur.execute("SELECT COUNT(word) FROM frequency")
            v = cur.fetchone()
            return log((x[0]+1)/(c[0] + v[0]))

    def prior(self, clazz):
        with sqlite3.connect(self.__database) as conn:
            cur = conn.cursor()
            cur.execute("SELECT count FROM class_count WHERE class='{}';".format(clazz))
            c = cur.fetchone()
            cur.execute("SELECT SUM(count) FROM class_count")
            d = cur.fetchone()
            return log(c[0]/d[0])

    def posterior(self, clazz, doc):
        bag = bagify(doc)
        p = 0
        for word, count in bag.items():
            p += self.likelihood(word, clazz) * count
        return p

    def classify(self, doc):
        max_class = ""
        max_prob = float('-inf')
        for i in self.__classes:
            p = self.posterior(i, doc)
            if p > max_prob:
                max_class = i
                max_prob = p
        return max_class, max_prob

    def multi_classify(self, doc):
        max_class = ""
        max_prob = float('-inf')
        clist=[]
        plist=[]
        for i in self.__classes:
            p = self.posterior(i, doc)
            if p > max_prob:
                max_class = i
                clist.append(max_class)
                max_prob = p
                plist.append(p)
        return clist[0:3], plist[0:3]

def run(test_file, db, class_key_name, filter):
    '''Runs classification on jsonl line be line for task1 and task2
    @pram db must be task1.db'''
    clsfier = Classifier(db)
    all_count = 0
    right_count = 0
    with open(test_file) as f:
        for line in f:
            obj = json.loads(line)
            doc = obj['title'] + obj['body']
            all_count += 1
            predicted_label = clsfier.classify(doc)[0] 
            true_label = filter(obj[class_key_name])
            print(predicted_label, true_label)
            if  true_label== predicted_label:
                print('correct')
                right_count+=1
            else:
                print('wrong')
            if all_count > 20:
                break 
    print("#docs:{}".format(all_count), "#right:{}".format(right_count))

def run_multiclass(test_file, db, class_key_name, filter):
    '''runs line by line multi classification @pram db must be task3.db'''
    clsfier = Classifier(db)
    all_count = 0
    right_count = 0
    with open(test_file) as f:
        for line in f:
            obj = json.loads(line)
            doc = obj['title'] + obj['body']
            all_count += 1
            labels = clsfier.multi_classify(doc)[0]
            print(labels , filter(obj[class_key_name]))
            if filter(obj[class_key_name]) in labels:
                print('correct')
                right_count+=1
            else:
                print('wrong')
            if all_count > 20:
                break 
    print("#docs:{}".format(all_count), "#right:{}".format(right_count))

if __name__ == '__main__':
    def filter0(x):
        '''filters out news class from newsPathLinks'''
        max_len = float('-inf')
        res =''
        for key, val in  x.items():
            if len(val) > max_len:
                max_len = len(val)
                res = key
        return res
 
    #task1:
    #run('out.jsonl', 'task1.db', 'newsPathLinks', filter0)

    #task2:
    run_multiclass('test/test_for_task1_and_2.jsonl', 'task1.db', 'newsPathLinks', filter0)

    #task3:
    #run('out.jsonl', 'task3.db', 'NewsAgency', lambda x:x)
