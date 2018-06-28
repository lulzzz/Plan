
# coding: utf-8

# script to make glossary for the columns of the data by checking the dictionary

# In[1]:


import os
import sys

import pandas as pd
from PyDictionary import PyDictionary
from nltk.corpus import wordnet
import gzip
import shutil


# In[2]:


new_data_path = r'''C:\Users\Gary\OneDrive - Datacrag Limited\Datacrag\datasets\made_up_data\data.xlsx'''
base_data_path = r'''C:\Users\Gary\OneDrive - Datacrag Limited\Datacrag\datasets\IBM_Watsons_Sales_Data\dataset.xlsx'''
out_txt_path = r'''C:\Users\Gary\OneDrive - Datacrag Limited\Datacrag\datasets\made_up_data\retrainnlp\retail\retail_glossary.txt'''
out_gz_path = r'''C:\Users\Gary\OneDrive - Datacrag Limited\Datacrag\datasets\made_up_data\retrainnlp\retail\retail_glossary.txt.gz'''


# In[5]:


def make_data(
    base_data_path,
    new_data_path,
    out_txt_path,
    out_gz_path,
    Remove=True,
    dictionary_meaning=False,
    synonyms=False,
    glossary=True
):
    if Remove:
        try:
            print('Removing old txt and txt.gz file ')
            open(out_txt_path, 'w').close()
            os.remove(out_gz_path)
        except FileNotFoundError:
            print('file does not exist')
    
    data_path_list = [new_data_path, base_data_path]
    
    for path in data_path_list:
        print('working on path:', path)
        df = pd.read_excel(path, 'dataset')
        
        if (dictionary_meaning or synonyms):
            dictionary = PyDictionary()         
            for col_name in df.columns:
                for single_word in col_name.split(" "):
                    
                    if dictionary_meaning:
                        print('dictionary meaning of the single word')
                        meaning_dict = dictionary.meaning(single_word)
                        print(meaning_dict)
                        for part_of_speech in meaning_dict:
                            meaning_list = meaning_dict[part_of_speech]
                            for each_meaning in meaning_list:
                                result = single_word + ' ' + each_meaning
                                with open(out_txt_path, "a") as text_file:
                                    text_file.write(result)
                                    text_file.write('\n')
                    else:
                        print('Not writing dictionary_meaning')
                                    
                    if synonyms:
                        print('synonyms  of the single word')
                        l,s = [],single_word
                        for ss in wordnet.synsets(single_word):
                            l.extend(ss.lemma_names())
                        l = list(set(l))
                        for i in l:
                            s += ' ' + i
                        with open(out_txt_path, "a") as text_file:
                            text_file.write(s)
                            text_file.write('\n')
                    else:
                        print('Not writing synonyms')
                        
        if glossary:
            df_glossary = pd.read_excel(path, 'glossary')
            for i,row in df_glossary.iterrows():
                s = row[0].replace(' ','_') + ' ' + row[1]
                with open(out_txt_path, "a") as text_file:
                    text_file.write(s)
                    text_file.write('\n')
        else:
            print('Not writing glossary')
    
    print('zipping the txt into txt.gz')
    with open(out_txt_path, 'rb') as f_in, gzip.open(out_gz_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


# In[6]:


# make_data(
#     base_data_path,
#     new_data_path,
#     out_txt_path,
#     out_gz_path,
#     Remove=True,
#     dictionary_meaning=False,
#     synonyms=False,
#     glossary=True
# )


# ### testing

# In[7]:



# if Remove:
#     try:
#         open(out_txt_path, 'w').close()
#         os.remove(out_gz_path)
#     except FileNotFoundError:
#         print('file does not exist')


# In[8]:


# dictionary = PyDictionary()
# data_path_list = [new_data_path, base_data_path]
# df = pd.read_excel(new_data_path, 'dataset')


# #### data from word's english meaning

# In[9]:


# for col_name in df.columns:
#     for single_word in col_name.split(" "):
        
#         print('dictionary meaning of the single word')
#         meaning_dict = dictionary.meaning(single_word)
#         print(meaning_dict)
#         for part_of_speech in meaning_dict:
#             meaning_list = meaning_dict[part_of_speech]
#             for each_meaning in meaning_list:
#                 result = single_word + ' ' + each_meaning
#                 with open(out_txt_path, "a") as text_file:
#                     text_file.write(result)
#                     text_file.write('\n')
        
#         print('synonyms  of the single word')
#         l,s = [],single_word
#         for ss in wordnet.synsets(single_word):
#             l.extend(ss.lemma_names())
#         l = list(set(l))
#         for i in l:
#             s += ' ' + i
#         with open(out_txt_path, "a") as text_file:
#             text_file.write(s)
#             text_file.write('\n')


# #### data from glossary

# In[10]:


# for p in data_path_list:
#     df_glossary = pd.read_excel(p, 'glossary')
#     for i,row in df_glossary.iterrows():
#         s = row[0].replace(' ','_') + ' ' + row[1]
#         with open(out_txt_path, "a") as text_file:
#             text_file.write(s)
#             text_file.write('\n')


# #### remove useless word
# need imporvement

# In[11]:


# out_txt_path


# In[12]:


# f = open(out_txt_path,'r')
# a = ['of ','is ','a ', 'the ', 'it ', 'was ', 'to ',
#     'or ', 'and ', 'for ', 'as ', 'in ', 'on ', 'from ']
# lst = []
# for line in f:
#     for word in a:
#         if word in line:
#             line = line.replace(word,'')
#     lst.append(line)
# f.close()
# f = open(out_txt_path,'w')
# for line in lst:
#     f.write(line)
# f.close()


# #### zip

# In[13]:


# with open(out_txt_path, 'rb') as f_in, gzip.open(out_gz_path, 'wb') as f_out:
#     shutil.copyfileobj(f_in, f_out)

