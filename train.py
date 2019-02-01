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
from preprocess import get_bag, get_classes
import re
from collections import Counter

create_class_count_query = 'CREATE TABLE IF NOT EXISTS class_count (class VARCHAR(20), count INTEGER);'
insert_class_count_query = "insert into  class_count(class, count) values('{}' ,{});"

database_file_path_ ='database.db'
data_file_ = 'out.jsonl'
class_key_name_ = 'newsPath'

def frequency_map(data_file, class_key_name, class_filter):
    '''returns a dictinary {key1:{word:freq,...}, key2:{word:freq},...} in which 
    keys are text classes and words are words in each class and freq is their count'''
    data_dict = dict()
    with open(data_file) as f:
        for line in f:
            bag, tag = get_bag(line, class_key_name, class_filter)
            try:
                data_dict[tag] = bag + data_dict[tag]
            except:
                data_dict[tag ]= bag
    return data_dict

def train(data_file, database_file_path, class_key_name, class_filter):
    classes = get_classes(data_file, class_key_name, class_filter)
    with sqlite3.connect(database_file_path) as conn:
        cur = conn.cursor()
        cur.execute(create_class_count_query)
        for clazz, count in classes.items():
            cur.execute(insert_class_count_query.format(clazz, count))
        
        create_freq_query ="CREATE TABLE IF NOT EXISTS frequency (word VARCHAR(20) PRIMARY KEY"
        for i in classes.keys():
            create_freq_query+=(",`"+i+"` INTEGER DEFAULT 0 ")
        create_freq_query+=');'
        #print(create_freq_query)
        cur.execute(create_freq_query)

        insert_freq_query = "INSERT INTO frequency (word) VALUES('{}');"

        f_map = frequency_map(data_file, class_key_name, class_filter)

        k = Counter()
        for i,j in f_map.items():
            k = j + k

        for i in k.keys():
            #print(i)
            #print(insert_freq_query.format(i).format(i))
            cur.execute(insert_freq_query.format(i))
        conn.commit()
        for clazz, bag in f_map.items():
            for word, count in bag.items():
                #print("UPDATE frequency SET `{}` = {} WHERE word='{}';".format(clazz, count, word))
                cur.execute("UPDATE frequency SET `{}` = {} WHERE word='{}';".format(clazz, count, word))

        conn.commit()

if __name__ == '__main__':
    #def filter0(x):
    #    ((a1,b1),(a2,b2)) = x.items()
    #    return a1 if len(b1) > len(b2) else a2

    def filter0(x):
        '''filters out news class from newsPathLinks'''
        max_len = float('-inf')
        res =''
        for key, val in  x.items():
            if len(val) > max_len:
                res = key
        return res

    train('newscorpus/asriran.jsonl', 'task1.db', 'newsPathLinks', filter0)
    train('newscorpus/all.jsonl', 'task3.db', 'NewsAgency', lambda x:x)
    
    #print(frequency_map()[classes.popitem()[0]]
