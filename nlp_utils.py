#!/usr/bin/env python

import nltk
import numpy as np
import pandas as pd
import re

# Define stopwords
STOPWORDS = map(str, nltk.corpus.stopwords.words('english'))

def alpha_level(string):
    '''
    Checks % of alphas in a string.
    Args:
        string = string to test alpha level
    '''
    return np.sum([x.isalpha() for x in string]) / len(string)

def text_tokenize(string, min_len=0, alphas_only=False):
    '''
    Tokenize a string. Leaves periods (if btwn digits) and ampersands (if btwn chars). Remove strings <50% alpha chars.
    Ars:
        string = string to be tokenized
        min_len = minimum length of words to keep
        alphas_only = set True to remove ALL digits
    '''
    string = re.sub(r'[^A-Za-z0-9\.\&]+', ' ', string) # only alphanums + periods + amps
    string = re.sub(r'(?<!\d)[.](?!\d)', ' ', string) # only periods btwn digits
    string = re.sub(r'(?<!\w)[&](?!\d)', ' ', string) # only amps btwn chars
    string = ' '.join([x for x in string.split() if not x in STOPWORDS]) # remove stopwords
    if min_len > 0: string = ' '.join([x for x in string.split() if len(x) >= min_len]) # len>=3
    if alphas_only: 
        string = re.sub('r\d+','', string)
    else:
        string = ' '.join([x for x in string.split() if alpha_level(x) >= 0.5]) # >=50% alphas

    return string

def text_normalize(string, delim='', stem=False, lem=False):
    '''
    Normalize, stem and lemmatize a string.
    Args:
        string = string to be normalized
        delim = string delimiter separating words (if exists)
        stem = set True to stem words
        lem = set True to lemmatize words
    '''
    snow = nltk.stem.SnowballStemmer('english')
    wnl = nltk.stem.WordNetLemmatizer()
    string = string.replace(delim, '')
    string = string.lower()
    if stem: string = ' '.join([snow.stem(x) for x in string.split()])
    if lem: string = ' '.join([wnl.lemmatize(x) for x in string.split()])
    
    return string

def get_topics(model, feature_names, n_top_words, output=False):
    '''
    Get topics, topic terms, and name each topic as 3 most relevant terms.
    Args:
        model = sklearn model
        feature_names = feature names returned by CountVectorizer().get_feature_names()
        n_top_words = # of top words to include per document
        output = set True to print topic # and the top words + weights
    '''
    topics = []
    topic_terms = []
    topic_names = []
    for topic_ix, topic in enumerate(model.components_):
        if output:
            print("Topic #%d: " % (topic_ix))
            print(" ".join([feature_names[ix] + " (" + str(round(topic[ix], 2)) + ")" for ix in topic.argsort()[:-n_top_words - 1:-1]]))
        topics.append(topic_ix)
        topic_terms.append(" ".join([feature_names[ix] + " (" + str(round(topic[ix], 2)) + ")" for ix in topic.argsort()[:-n_top_words - 1:-1]]))
        topic_names.append('{} {} {}'.format(topic_terms[-1].split()[0], topic_terms[-1].split()[2], topic_terms[-1].split()[4]))
    
    df_topics = pd.DataFrame(data=zip(topics, topic_terms, topic_names), columns=['Topic_Num', 'Topic_Terms', 'Topic_Names'])
    
    return df_topics

def best_doc_topics(model, tf, output=False):
    '''
    Grab best topic for each document.
    Args:
        model = sklearn model
        tf = term-document matrix from fit_transform() applied to CountVectorizer()
        output = set True to print doc # and best topic
    '''
    doc_topic_scores = model.transform(tf)
    doc_topics = []
    for ix in range(doc_topic_scores.shape[0]):
        high_score_topic = doc_topic_scores[ix].argmax()
        doc_topics.append(high_score_topic)
        if output: print("doc: {} topic: {}\n".format(ix, high_score_topic))
    
    return doc_topics

def build_topics_df(files, paths, doc_topics, df_topics):
    '''
    Build topics dataframe from files, doc topic, and dataframe of topics (#, terms, name).
    Args:
        files = list of filenames
        paths = list of filepaths
        doc_topics = list output from best_doc_topics()
        df_topics = dataframe output of get_topics()
    '''
    df_cols = ['File_Name', 'File_Path', 'Topic_Num']
    df = pd.DataFrame(data=zip(files, paths, doc_topics), columns=df_cols)
    df = df.merge(df_topics, on='Topic_Num', how='left')
    
    return df
