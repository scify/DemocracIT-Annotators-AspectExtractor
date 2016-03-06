# Aspect Extractor module
# asp_extract.py V1.0
This software receives texts (annotated from opengov) and outputs a suggested abstract of the text.
To run:
>>> python asp_extract.py -i <textsfilepath> -m <0|1>

> -i: a file including texts in the form URL\tTEXT\tABSTRACT (ABSTRACT is used for evaluation only)

> -m: 0 to print the suggested abstracts or 1 to evaluate the generated abstracts 

Nuts & bolts:

Read a text and select any parts of it that are POS tagged with one of the following sequences: 
['noun noun adjective noun', 'noun adjective noun', 'adjective noun']
Exclude texts which are parts of longer texts in the list and return the final list.
The hard coded POS sequences have been resulted after studying the POS tags of manually labelled text abstracts. Note that more data may lead to more POS sequences which might improve the efficiency. Included (but commented) is source code which automatically generates suggested POS sequences from texts (manually labelled with abstracts: URL\tTEXT\tABSTRACT) 

WARNING: Don't forget to inlude the tagger.jar, this is a slightly changed code of the POS tagger (http://nlp.cs.aueb.gr/software_and_datasets/AUEB_POS_tagger_2_2_alpha.tar.gz) in order for the jar to play with Python. If migration to Java is wanted one may use directly the source code found on the link above. 

__author__: Ioannis Pavlopoulos - 16 July 2015
# Aspect Extractor Service
# asp_extractor_service.py

This file is a simple web service wrapper that utilizes the logic in asp_extract.py,
with minor modifications, in order to server one document at a time. The service requires Flask installed in the system, and may be invoked with a POST request on 
>       http://<host>:<port>/aspect_extractor/extract_aspects
with parameter text=text_to_extract_aspects_on

e.g.

>       curl --data "text=Τεχνικές Προδιαγραφές έργου «Επέκταση Εγκατάστασης Αυτοματοποιημένου Συστήματος Επιτήρησης στην περιοχή του Έβρου" http://127.0.0.1:5001/aspect_extractor/extract_aspects

response (in json format)

>       { "content": [ "Τεχνικές Προδιαγραφές έργου" ] }

__author__: George Kiomourtzis <gkiom@scify.org>
