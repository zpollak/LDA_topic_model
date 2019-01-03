#!/usr/bin/env python

from __future__ import print_function, division
import datetime
import nlp_utils as nlp
import pandas as pd
from pysql import SQL
import sys
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

def clean_datetime():
    '''
    Trim colons and periods from datetime.datetime.now(). 
    '''
    return str(datetime.datetime.now().replace(second=0, microsecond=0)).replace(':', '').replace(' ', '_')[:-2]

def run_type(ins):
    '''
    Prompt user for LDA model run type.
    Args:
        ins = LDA model inputs
    '''
    print('Please note that your data must be a table containing the following columns (named accordingly):')
    print('\t[File_Name]\n\t[File_Path]\n\t[Words]\n')
    print('Currently, the following hyperparameters are set. If you wish to change, please see line '\
          '86 of `lda_run_model.py`')
    print('\tNumber of features = '+str(ins.n_feats)+'\n\tTerm freq upper bound = '+str(ins.max_df)+ \
          '\n\tTerm freq lower bound = '+str(ins.min_df)+'\n\tNumber of topics = '+str(ins.n_topics))
    print('\tMax iterations = '+str(ins.max_iter)+'\n\tLearning method = '+str(ins.method)+'\n\tLearning offset = '+str(ins.offset))
    print('\tRandom state = '+str(ins.r_state)+'\n\tNumber of top words per doc = '+str(ins.n_top_words)+'\n')
    print('To bypass SQL credentials input:\n\t- Comment out line 89\n\t- Uncomment lines 93-96\n\t- ' \
          'Update credentials in line 93\n\t- Update DB, schema, and table in line 95\n')
    print('Please input the number indicating where your corpus is being loaded from:')
    print('\t(1) SQL\n\t(2) Excel\n\t(3) CSV\n\t(4) Exit the program')
    choice = str(raw_input().lower().strip())
    if choice == '1':
        print('Input SQL credentials and query to run')
        driver = str(raw_input('\tDriver:\t'))
        server = str(raw_input('\tServer:\t'))
        user = str(raw_input('\tUsername:\t'))
        query = str(raw_input('\tQuery:\t'))
        with SQL(driver, server, user) as db:
            db.query(query)
            df = pd.DataFrame([tuple(row) for row in db.fetchall()], columns=[col[0] for col in db.description()])
    elif choice == '2':
        print('Input Excel/CSV file name (including extension)')
        filename = str(raw_input('\tFile name:\t'))
        try:
            df = pd.read_excel(filename)
        except Exception as e:
            sys.exit(e)
    elif choice == '3':
        print('Input CSV file name (including extension)')
        filename = str(raw_input('\tFile name:\t'))
        try:
            df = pd.read_csv(filename)
        except Exception as e:
            sys.exit(e)
    elif choice == '4':
        sys.exit('Quitting the program.')
    else:
        sys.exit('Invalid choice. Quitting the program.')
        
    return df

class LDAinputs():
    def __init__(self, n_feats=None, max_df=1.0, min_df=1, n_topics=10, max_iter=10, 
                 method='online', offset=10.0, r_state=0, n_top_words=10):
        self.n_feats = n_feats
        self.max_df = max_df
        self.min_df = min_df
        self.n_topics = n_topics
        self.max_iter = max_iter
        self.method = method
        self.offset = offset
        self.r_state = r_state
        self.n_top_words = n_top_words
    
def main():
    print('``````````````````````````````````````````````````````````````')
    print('````````````````````LDA for Topic Modeling````````````````````')
    print('``````````````````````````````````````````````````````````````')
    
    # TF, LDA and Topic inputs
    ins = LDAinputs(100, 0.9, 0.1, 20, 5, 'online', 50.0, 0, 10)
    
    # Prompt user for info to pull corpus as dataframe
    df = run_type(ins)
    
    # COMMENT OUT LINE 86 AND USE THE FOLLOWING TO BYPASS SQL CREDENTIAL INPUT
    # Read SQL table to dataframe
#    driver, server, user = '{SQL Server Native Client 11.0}', 'SERVER_NAME', 'DOMAIN\USERNAME'
#    with SQL(driver, server, user) as db:
#        db.query('SELECT * FROM DB_NAME.DB_SCEHMA.[TABLE_NAME]')
#        df = pd.DataFrame([tuple(row) for row in db.fetchall()], columns=[col[0] for col in db.description()])
    
    # df is at a tab level so need to concat words for each file
    fns = df['File_Name'].unique().tolist()
    paths = df['File_Path'].unique().tolist()
    docs = [' '.join(df[df['File_Name'] == fn]['Words'].tolist()) for fn in fns]
    
    # Clean up docs (already tokenized)
    docs = [nlp.text_tokenize(x, min_len=4) for x in docs]
    docs = [nlp.text_normalize(x, ',', stem=False, lem=False) for x in docs]   
    
    # TF matrix
    tf_vectorizer = CountVectorizer(max_df=ins.max_df, min_df=ins.min_df, 
                                    max_features=ins.n_feats, stop_words='english')
    tf = tf_vectorizer.fit_transform(docs)
    tf_feature_names = tf_vectorizer.get_feature_names()
    
    # LDA model
    lda = LatentDirichletAllocation(n_components=ins.n_topics, max_iter=ins.max_iter, learning_method=ins.method, 
                                    learning_offset=ins.offset,random_state=ins.r_state).fit(tf)
    
    # LDA results
    df_topics = nlp.get_topics(lda, tf_feature_names, ins.n_top_words, True)
    
    # Best topic per doc
    doc_topics = nlp.best_doc_topics(lda, tf, True)
    
    # Join file info and topics
    df_fin = nlp.build_topics_df(fns, paths, doc_topics, df_topics)

    # Write to CSV    
    df_fin.to_csv('lda_topic_model_' + clean_datetime() + '.csv', index=False)

if __name__ == '__main__':
    main()
