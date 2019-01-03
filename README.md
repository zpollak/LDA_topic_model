# LDA_topic_modeling

### Overview
Build a Latent Dirichlet Allocation (LDA) model to discover topics that exist across a corpus of documents and assign a topic to each document.

### Instructions
1. To extract the text from your corpus of Excel files, place the `excel_corpus_to_sql.py` file in the top directory containing all of your Excel files. The script will recursively traverse the directory looking for all xlrd-compatible Excel files and write the information to a SQL table.<br>
    a. You will have to create an empty SQL table beforehand with the following columns:<br>
    **[Words, File_Name, Tab_Name, Cells, File_Path]**
2. Place the remaining 3 files from this repository in a directory together.<br>
    a. If you are using a SQL table as your input, the files can go in any directory.<br>
    b. If you are using a local file as your input, the files must be placed in a directory with that file.<br>
3. Navigate to the directory via the command line and run with `python lda_run_model.py`.
4. Follow the instructions in your terminal to build your model.

#### Modules
  - `excel_corpus_to_sql` will extract text in all tabs and cells from a corpus of Excel files and write to a preexisting SQL table
  - `lda_run_model` is where the model is built; it leverages the `pysql` and `nlp_utils` modules
  - `pysql` contains a SQL class in the event your input table is stored in a database
  - `nlp_utils` contains some helper functions for cleaning text and extracting topics from the LDA model

#### Inputs
`lda_run_model` will not extract all of the words from the documents that you wish to model. You will need to create a table that contains:
1. File names with column name **[File_Name]**
2. File paths with column name **[File_Path]**
3. All of the words in each document as a string with column name **[Words]**

##### Example Inputs
| File_Name | File_Path | Words |
| --- | --- | --- |
| file1.xlsx | C:\..\file1.xlsx | The contents of file1 are here |
| file2.csv | C:\..\file2.csv | This is found in file2 |
| file3.txt | C:\..\file3.txt | And this is the text from file3 |

#### Output
The model output will be a CSV file containing the file names, file paths, top N terms (and their weights) for each documents's assigned topic, and the name of the highest-scoring topic. The topic names are built by concatenating the top 3 terms.
