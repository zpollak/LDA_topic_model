#!/usr/bin/env python

from __future__ import print_function, division
import datetime
import logging
import nlp_utils as nlp
import os
import sys
import time
import xlrd
from logging.handlers import RotatingFileHandler
from nltk.corpus import stopwords
from pysql import SQL

# Force UTF-8
reload(sys)
sys.setdefaultencoding('UTF8')

# NLTK stopwords
STOPWORDS = map(str, stopwords.words('english'))

# SQL connection info
DRIVER, SERVER, USER = '{SQL Server Native Client 11.0}', 'SERVER_NAME', 'DOMAIN\USERNAME'
DB_NAME, DB_SCHEMA, TABLE_NAME = 'DATABASE_NAME', 'SCHEMA', 'TABLE_NAME'

def clean_datetime():
    '''
    Trim colons and periods from datetime.datetime.now(). 
    '''
    return str(datetime.datetime.now().replace(second=0, microsecond=0)).replace(':', '').replace(' ', '_')[:-2]

def colnum_string(n):
    '''
    Convert number to Excel column header (e.g. 1 = A, 27 = AA)
    Args:
        n = column number to convert
    '''
    string = ""
    while n > 0:
        n, remainder = divmod(n-1, 26)
        string = chr(65 + remainder) + string
    
    return string

def xl_word_count():
    '''
    This function will:
        1. Recursively traverse directory and read in (most) Excel file variants
        2. Transform Excel file into 1 set per tab containing:
            a. Words in the file
            b. Tab in which the words appear
            c. Cells in which each word appears
            d. Filename
            e. File path
                e.g. 
                ('Example of word text contents', 'Sheet1', 'A1, B1, C1, A2, B2', 'Example_File.xlsx', 'C:\...\Example.File.xlsx')
        3. Write to SQL table (at tab level)
    '''
    
    with SQL(DRIVER, SERVER, USER) as db:
        # Walk the directory
        cur_file = 0
        # Grab files that are already in table
        db.query('SELECT DISTINCT [File_Name] FROM ' + DB_NAME + '.' + DB_SCHEMA + '.[' + TABLE_NAME + ']')
        complete_files = [row[0] for row in db.fetchall()]
        # Get rough file count (rough because of .py files and non-xlrd compatitble files)
        rough_file_count = sum([len(files) for root, dirs, files in os.walk(os.getcwd())])
        for root, dirs, files in os.walk(os.getcwd()):
            for filename in files:
                # Skip files that already appear in table
                if filename in complete_files:
                    cur_file += 1
                    print(os.path.join(root,filename))
                    print('File {} of {} (~{:.2f}%)'.format(cur_file, rough_file_count, 100*cur_file/rough_file_count))
                    print('File already loaded.')
                    continue
                # Only check xlrd compatible files
                if filename.lower().endswith('.xls') or filename.lower().endswith('xlsx') or filename.lower().endswith('xlsm') or filename.lower().endswith('xlk') or filename.lower().endswith('xltx'):
                    filepath = os.path.join(root, filename)
                    cur_file += 1
                    print(filepath)
                    print('File {} of {} (~{:.2f}%)'.format(cur_file, rough_file_count, 100*cur_file/rough_file_count))
                    # Timer to skip file if longer than N seconds
                    timeout = time.time() + 10
                    # Open book; if error, log and skip
                    try:
                        book = xlrd.open_workbook(filepath)
                    except Exception as e:
                        print('Error opening file: ' + filepath)
                        print(e)
                        logging.error('Path = ' + filepath + '; Error = ' + str(e))
                        continue
                    # Loop through sheets and all cells; append values and locations to lists
                    sheets = [book.sheet_by_name(x) for x in book.sheet_names()]
                    for sheet in sheets:
                        values = []
                        cells = []
                        if time.time() > timeout:
                            print('File timed out. Moving to next.')
                            logging.info('Path = ' + filepath + '; Sheet = ' + str(sheet.name) + '; Error = TIMEOUT.')
                            break
                        for row in range(sheet.nrows):
                            for col in range(sheet.ncols):
                                try:
                                    value = str(sheet.cell(row,col).value)
                                except:
                                    value = sheet.cell(row,col).value
                                    value = value.encode('utf-8', 'ignore')
                                if value in ['', ' ', '\n']:
                                    continue
                                try:
                                    sheet_name = str(sheet.name)
                                except:
                                    sheet_name = sheet.name
                                    sheet_name = sheet_name.encode('utf-8', 'ignore')
                                if any(x in value for x in [' ', '\n', '_', '-']):
                                    for word in value.replace('\n', ' ').replace('_', ' ').split(' '):
                                        values.append(nlp.text_tokenize(word, min_len=3))
                                        cells.append('{}{}'.format(colnum_string(col+1), row+1))
                                else:
                                    values.append(nlp.text_tokenize(value, min_len=3))
                                    cells.append('{}{}'.format(colnum_string(col+1), row+1))
                        # Concat list into strings
                        values = ', '.join([x for x in values if x != ''])
                        cells = ', '.join([x for x in cells if x != ''])
                        # If no words, log and skip else write to SQL
                        if len(values) == 0:
                            logging.info('Path = ' + filepath + '; Error = No cell values available.')
                            continue
                        else:
                            sql = "INSERT INTO " + DB_NAME + "." + DB_SCHEMA + ".[" + TABLE_NAME + \
                            "] ([Words], [File_Name], [Tab_Name], [Cells], [File_Path])" \
                            " VALUES ('" + values + "', '" + filename + "', '" + sheet_name + "', '" + \
                            cells + "', '" + filepath + "')"
                            try:
                                db.query(sql)
                            except Exception as e:
                                print(e)
                                logging.error('Path = ' + filepath + '; Error = ' + str(e))

def main():
    log_name = 'excel_search_' + clean_datetime() + '.log'
    logging.basicConfig(filename=log_name, filemode='w', level=logging.DEBUG)
    log = logging.getLogger()
    handler = RotatingFileHandler(log_name, maxBytes=5*1024*1024, backupCount=100000)
    log.addHandler(handler)
    xl_word_count()

if __name__ == '__main__':
    main()