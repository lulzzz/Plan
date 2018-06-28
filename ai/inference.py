
# coding: utf-8

# ### doc
# AI component
# 
# The ultimate goal of the AI is to help to find out the one-to-one mapping between the columns of the base file and the columns of the new file.
# 
# A. learning-based (for cases where we have more datasets) (to be developed in phase2)
# The main phases of our model can be summarized as follow:
# 1. extract the features of a column
# 2. feed the features into the classifier
# 3. the classifier output the most probable column index of the base file for the input column
# 
# Extracting the features of a column
# <br>We use not only the basic statistics of the column but also Natural Language Processing (NLP) techniques to understand the semantic meaning of the column name. The model is a Google's pre-trained Word2Vec model, which we can use the trained word embedding to compare the similarity of words. The model can be trained on a different dataset so that the model can be tailor-made for users from different industry. For details of word2vec model, please see [here.](https://en.wikipedia.org/wiki/Word2vec)
# 
# Feeding the features into the classifier
# <br>After extracting the features, we can then pass the data to train a classifier. The choice of multi-class classifier is flexible in our case, a simple logistic regression or even neural network will do the job, as long as the data we input fulfill the requirement of the classifier.
# 
# 
# B. Rule-based (for cases where we have only very few datasets, and we know the rules)
# Using distance and meaning(NLP to understand the semantic meaning of the column name) of words to determine the mapping

# ### import

# In[13]:


import os
import sys
import random 

import scipy
import numpy as np
import pandas as pd
import gensim
import editdistance


# In[14]:


base_path = r'''C:\Users\Gary\OneDrive - Datacrag Limited\Datacrag\datasets\IBM_Watsons_Sales_Data\dataset.xlsx'''
new_path = r'''C:\Users\Gary\OneDrive - Datacrag Limited\Datacrag\datasets\made_up_data\data.xlsx'''
model_path_self = r'''C:\Users\Gary\OneDrive - Datacrag Limited\Datacrag\development\train\project\autoETL\ckpt\model'''
model_path_google = r'''C:\Users\Gary\OneDrive - Datacrag Limited\Datacrag\development\train\project\autoETL\ckpt\GoogleNews-vectors-negative300.bin'''


# In[15]:


# base = pd.read_excel(base_path, 'dataset')
# new = pd.read_excel(new_path, 'dataset')
# model_self = gensim.models.Word2Vec.load(model_path_self)
# model_google = gensim.models.KeyedVectors.load_word2vec_format(model_path_google, binary=True)


# ### B. rule-based inference

# In[17]:


# if column names are the same, assumed they are the same columns
def same_colname(new_cols, base_cols, mapping):
    for col_n in new_cols[:]:
        col_n = col_n.lower()
        for col_b in base_cols[:]:
            col_b = col_b.lower()
            if editdistance.eval(col_n,col_b) == 0:
                mapping[col_n] = col_b
                new_cols.pop(new_cols.index(col_n))
                base_cols.pop(base_cols.index(col_b))
    return new_cols, base_cols, mapping


# In[18]:


def draw_similarity_matrix(new_cols, base_cols, model):
    # init
    master_dict = {}
    for col_n in new_cols:
        master_dict[col_n] = {}
        
    # draw the matrix
    for col_n in new_cols:
        try:
            model[col_n.replace(' ','_')]
            for col_b in base_cols:
                try:
                    model[col_b.replace(' ','_')]
                    s_score = model.wv.similarity(col_n.replace(' ','_'), col_b.replace(' ','_'))
                    master_dict[col_n][col_b] = s_score
                except:
                    print('The col_b word {} not in model. Skip.'.format(col_b))
        except:
             print('The col_n word {} not in model. Try next word.'.format(col_n))
    
    master_dict = {k:v for k,v in master_dict.items() if len(v)!=0}
    return master_dict


# In[46]:


def find_highest(master_dict):
    h = -float('Inf')
    n,b = '',''
    for d in master_dict:
        for k, v in master_dict[d].items():
            if v > h:
                h = v
                b = k
                n = d
    return n, b, h

def find_lowest(master_dict):
    l = float('Inf')
    n,b = '',''
    for d in master_dict:
        for k, v in master_dict[d].items():
            if v < l:
                l = v
                b = k
                n = d
    return n, b, l


# In[47]:


# assign the mapping according to the value of the similarity score (high to low)
def assign_similar_meaning(master_dict, new_cols, base_cols, mapping):
    while len(master_dict) != 0:
        print('master dict',master_dict)
        n, b, h = find_highest(master_dict)
        print('n, b, h :',n, b, h )
        mapping[n] = b
        new_cols.pop(new_cols.index(n))
        base_cols.pop(base_cols.index(b))
        master_dict = {k:v for k,v in master_dict.items() if k != n}
        master_dict.pop(n, None)
        for d in master_dict:
            master_dict[d] = { k : v for k,v in master_dict[d].items() if k != b}
    return new_cols, base_cols, mapping
    


# In[52]:


def draw_distance_matrix(new_cols, base_cols):
    master_dict = {}
    for col_n in new_cols:
        master_dict[col_n] = {}
        
    for col_n in new_cols[:]:
        col_n = col_n.lower()
        for col_b in base_cols[:]:
            col_b = col_b.lower()
            dist = editdistance.eval(col_n,col_b)
            master_dict[col_n][col_b] = dist
    return master_dict


# In[53]:


# assign the mapping according to the value of the distance score (low to high)
def assign_close_distance(master_dict, new_cols, base_cols, mapping):
    while len(master_dict) != 0:
        n, b, h = find_lowest(master_dict)
        mapping[n] = b
        new_cols.pop(new_cols.index(n))
        base_cols.pop(base_cols.index(b))
        master_dict = {k:v for k,v in master_dict.items() if k != n}
        master_dict.pop(n, None)
        for d in master_dict:
            master_dict[d] = { k : v for k,v in master_dict[d].items() if k != b}
    return new_cols, base_cols, mapping


# In[57]:


def init_op(new_path, base_path, model_path_google, model_path_self=None):
    new = pd.read_excel(new_path, 'dataset')
    base = pd.read_excel(base_path, 'dataset')
    model_google = gensim.models.KeyedVectors.load_word2vec_format(model_path_google, binary=True)
    if model_path_self != None:
        model_self = gensim.models.Word2Vec.load(model_path_self)
    else:
        model_self=None
        
    new_cols = new.columns.tolist()
    new_cols = [c.lower() for c in new_cols]
    base_cols = base.columns.tolist()
    base_cols = [c.lower() for c in base_cols]
    mapping = {c:'' for c in new_cols}
    return new_cols, base_cols, mapping, model_google, model_self


# In[58]:


def infer(new_path, base_path, model_path_google, model_path_self=None):
    # init
    print('init')
    new_cols, base_cols, mapping, model_google, model_self = init_op(new_path, base_path, model_path_google, model_path_self)

    print('find same col_name')
    new_cols, base_cols, mapping = same_colname(new_cols, base_cols, mapping)
    print('remaing new_name: {}; remainin base_name: {}'.format(new_cols, base_cols))
    
    print('comparing meaning of col_name using pretrained google model')
    master_dict = draw_similarity_matrix(new_cols, base_cols, model_google)
    print('assign columns')
    new_cols, base_cols, mapping = assign_similar_meaning(master_dict, new_cols, base_cols, mapping)
    print('remaing new_name: {}; remainin base_name: {}'.format(new_cols, base_cols))
    
    if model_self == None:
        print('comparing distance of col_name')
        master_dict = draw_distance_matrix(new_cols, base_cols)
        print('assign columns')
        new_cols, base_cols, mapping = assign_close_distance(master_dict, new_cols, base_cols, mapping)
        print('remaing new_name: {}; remainin base_name: {}'.format(new_cols, base_cols))
    else:
        print('comparing meaning of col_name using pretrained google model')
        master_dict = draw_similarity_matrix(new_cols, base_cols, model_self)
        print('assign columns')
        new_cols, base_cols, mapping = assign_similar_meaning(master_dict, new_cols, base_cols, mapping)
        print('remaing new_name: {}; remainin base_name: {}'.format(new_cols, base_cols))
    return mapping


# In[59]:


# m = infer(new_path, base_path, model_path_google, model_path_self=None)
# m


# ### A. classifier

# ### Export

# In[ ]:


if __name__ == '__main__':
    try:
        __file__
    except:
        get_ipython().system(' jupyter nbconvert --to=python "C:\\Users\\Gary\\OneDrive - Datacrag Limited\\Datacrag\\development\\inference\\project\\autoETL\\inference.ipynb"')

