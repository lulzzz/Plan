
# coding: utf-8

# train the model given dataset

# In[1]:


import os
import sys

import numpy as np
import pandas as pd
import gzip
import gensim
from gensim.models import Word2Vec
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s’, level=logging.INFO')


# In[2]:


data_dir = r'''C:\Users\Gary\OneDrive - Datacrag Limited\Datacrag\datasets\made_up_data\retrainnlp\retail'''
model_dir = r'''C:\Users\Gary\OneDrive - Datacrag Limited\Datacrag\development\train\project\autoETL\ckpt'''

data_name = 'retail_glossary.txt'
data_gz_name = 'retail_glossary.txt.gz'
model_name = 'model'


# In[3]:


data_path = os.path.join(data_dir, data_name)
data_gz_path = os.path.join(data_dir, data_gz_name)
model_path = os.path.join(model_dir, model_name)


# In[4]:


def read_input(input_file):
    """This method reads the input file which is in gzip format"""
    
    logging.info("reading file {0}...this may take a while".format(input_file))
    with gzip.open(input_file, 'rb') as f:
        for i, line in enumerate(f):
            if (i % 10000 == 0):
                logging.info("read {0} reviews".format(i))
            # do some pre-processing and return list of words for each review
            # text
            yield gensim.utils.simple_preprocess(line.lower())

# read the tokenized reviews into a list
# each review item becomes a serries of words
# so this becomes a list of lists


# In[7]:


def train(data_gz_path, model_path):
    documents = list (read_input (data_gz_path))
    logging.info ("Done reading data file")
    model = gensim.models.Word2Vec (documents, size=150, window=10, min_count=1, workers=10)
    model.train(documents,total_examples=len(documents),epochs=10)
    model.save(model_path)
    print('finished')


# In[8]:


# train(data_gz_path, model_path)


# ### Export

# In[ ]:


if __name__ == '__main__':
    try:
        __file__
    except:
        get_ipython().system(' jupyter nbconvert --to=python "C:\\Users\\Gary\\OneDrive - Datacrag Limited\\Datacrag\\development\\train\\project\\autoETL\\train.ipynb"')


# ### testing

# In[ ]:


#  with gzip.open (data_gz_path, 'rb') as f:
#         for i,line in enumerate (f):
#             print(line)
#             break
 


# In[ ]:


# model = gensim.models.Word2Vec (documents, size=150, window=10, min_count=1, workers=10)
# model.train(documents,total_examples=len(documents),epochs=10)


# In[ ]:


# w1 = "quantity"
# model.wv.most_similar (positive=w1)


# In[ ]:


# print(model.wv.similarity('quantity','retail'))
# print(model.wv.similarity('quantity','unit'))
# print(model.wv.similarity('quantity','country'))
# print(model.wv.similarity('quantity','margin'))


# In[ ]:


# model.save(model_path)


# In[ ]:


# new_model = gensim.models.Word2Vec.load(model_path)

