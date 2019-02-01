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

import classifier
import preprocess
import train
import pandas as pd
import json
import sqlite3
class Measurer():
    def __init__(self, test_file, class_key_name, filter, database,):
        self.__classifier = classifier.Classifier(database)
        self.__test_file = test_file
        self.__class_key_name = class_key_name
        self.__filter = filter
        self.__database = database
        self.__true_classes = preprocess.get_classes(test_file,class_key_name,filter)
        classes = []
        with sqlite3.connect(database) as conn: 
            cur = conn.cursor()
            cur.execute("SELECT class FROM class_count")
            for i in cur:
                classes.append(i[0])
        self.measurments = pd.DataFrame({'true':list([self.__true_classes[x] for x in classes])}, index = classes, columns = ['true','right','all'])
        self.measurments.fillna(0, inplace=True)


    def run(self):
        '''Runs classification on jsonl line be line for task1 and task2
        @pram db must be task1.db'''
        clsfier = self.__classifier
        classify = clsfier.classify
        all_count = 0
        right_count = 0
        test_file = self.__test_file
        db = self.__database
        class_key_name = self.__class_key_name
        with open(test_file) as f:
            for line in f:
                obj = json.loads(line)
                doc = obj['title'] + obj['body']
                all_count += 1
                predicted_label = classify(doc)[0] 
                self.measurments.loc[predicted_label, 'all']+=1
                true_label = self.__filter(obj[class_key_name])
                print('predicted: '+predicted_label,'true label: '+ true_label)
                if  true_label== predicted_label:
                    self.measurments.loc[predicted_label, 'right']+=1
                    right_count+=1
                if all_count > 5:
                    break 
        return right_count, all_count

    def run_multiclass(self):
        '''Runs classification on jsonl line be line for task3
        @pram db must be task3.db'''
        clsfier = self.__classifier
        classify = clsfier.multi_classify
        all_count = 0
        right_count = 0
        test_file = self.__test_file
        db = self.__database
        class_key_name = self.__class_key_name
        with open(test_file) as f:
            for line in f:
                obj = json.loads(line)
                doc = obj['title'] + obj['body']
                all_count += 1
                predicted_label = classify(doc)[0]
                for i in predicted_label:
                    self.measurments.loc[i, 'all']+=1
                true_label = self.__filter(obj[class_key_name])
                print('predicted: '+predicted_label,'true label: '+ true_label)
                if  true_label in predicted_label:
                    self.measurments.loc[true_label, 'right']+=1
                    right_count+=1

        return right_count, all_count

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
    m = Measurer('mini_test.jsonl', 'newsPathLinks', filter0, 'task1.db')
    m.run()
    print(m.measurments)
