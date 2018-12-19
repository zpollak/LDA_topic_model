# LDA_topic_modeling

### Overview
Build a Latent Dirichlet Allocation (LDA) model to discover topics that exist across a corpus of documents and assign a topic to each document.

### Instructions
1. Place the 3 files from this repository in a directory.<br>
    a. If you are using a SQL table as your input, the files can go in any directory.<br>
    b. If you are using a local file as your input, the files must be placed in a directory with that file.<br>
2. Navigate to the directory via the command line and run with `python lda_run_model.py`.

#### Modules
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
