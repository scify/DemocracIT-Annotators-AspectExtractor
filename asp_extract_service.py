#!/usr/bin/python
# -*- coding: utf-8 -*-

# asp extractor service.py #
# =================================================================================== #
# this file is a simple web service wrapper that utilizes the logic in asp_extract.py,
# with minor modifications, in order to server one document at a time.
#
# The service requires Flask installed in the system, and may be invoked with
# a POST request on http://<host>:<port>/aspect_extractor/extract_aspects
# with parameter text=text_to_extract_aspects_on
#
# e.g.
# curl --data "text=Τεχνικές Προδιαγραφές έργου «Επέκταση Εγκατάστασης Αυτοματοποιημένου Συστήματος Επιτήρησης στην περιοχή του Έβρου" http://127.0.0.1:5001/aspect_extractor/extract_aspects

# response (json)
# { "content": [ "Τεχνικές Προδιαγραφές έργου" ] }
#
# __author__ = George Kiomourtzis <gkiom@scify.org>
# =================================================================================== #

import subprocess, collections, sys, getopt
from flask import Flask, request

app = Flask(__name__)
app.secret_key = "this is a super secret key."


# Parse <URL\tTEXT\tABSTRACT> texts (even when \n and \t exist breaking the format)
def read(filepath):
    with open(filepath) as i: data = i.read()
    lines = data.split('http')  # assuming no links exist but the first from each line
    records = [l.split('\t') for l in lines if len(l) > 2]  # various tabs might exist within the text
    proper_records = [('http' + r[0], ' '.join(' '.join(r[1:len(r) - 1]).split()), r[len(r) - 1]) for r in records]
    return proper_records


# Detone Greek
def detone(text): return text.upper().replace(u'Ά', u'Α').replace(u'Έ', u'Ε').replace(u'Ή', u'Η').replace(u'Ί',
                                                                                                          u'Ι').replace(
    u'Ό', u'Ο').replace(u'Ύ', u'Υ').replace(u'Ώ', u'Ω').lower()


# POS tag a text
# WARNING: Include in the same folder the tagger.jar, along with the smallTagSetFiles
def postag(text):
    ttext = subprocess.check_output(['java', '-jar', 'tagger.jar', '-text', text])
    records = [tterm.split() for tterm in ttext.strip().split('\n')]
    return records


# POS tag and return as a string
postag2txt = lambda text: ' '.join([t[1] for t in postag(text)])

# Find a sublist pattern in a list
subfinder = lambda thalist, sublist: [range(i, i + len(sublist)) for i in range(len(thalist)) if
                                      thalist[i] == sublist[0] and thalist[i:i + len(sublist)] == sublist]


# Find POS patterns within text and return the text's position
def get_POS_text(text, top_patterns):
    text_tokens, text_pos = map(lambda c: c[0], text), map(lambda c: c[1], text)
    matches = []
    for top_pos in top_patterns:
        if len(matches) > 0: return matches  # pattrn3 is in pattrn2 which is in pattrn1 --> return only the longest sequence
        match = subfinder(text_pos, top_pos)
        for m in match:
            matches.append([text_tokens[i] for i in m])
    return matches


# Hard code patterns (or uncomment in case you like peaking:)
'''abstracts = [postag2txt(r[2]) for r in records if len(r[2])>0]
count_abstracts = collections.Counter(abstracts)
top_pos_patterns = count_abstracts.most_common(3)
print 'How many times did the top-3 POS patterns occur in the abstracts (i.e., upper bound)?\nCorrect answer: %.2f'%(float(sum([a[1] for a in top_pos_patterns]))/sum(count_abstracts.values()))
#top_pos_patterns = map(lambda couple:couple[0].split(), top_pos_patterns)'''

top_pos_patterns = [['noun', 'noun', 'adjective', 'noun'], ['noun', 'adjective', 'noun'], ['adjective', 'noun']]


def extract_aspects(filepath, mode):
    try:
        records = read(filepath)
    except:
        sys.exit('#badword! Something went wrong reading the texts...')
    texts = [postag(r[1]) for r in records if len(r[1]) > 0]
    predicted_tags = []
    for t in texts:
        pos_matches = get_POS_text(t, top_pos_patterns)
        prediction = [' '.join(m) for m in pos_matches]  # if pos_matches else None
        predicted_tags.append(prediction)
    if mode == 0:
        for prediction in predicted_tags:
            print ', '.join(prediction)
    elif mode == 1:
        gold_tags = [r[2] for r in records]  # WARNING: This should exist!
        # Strict accuracy (1 if the predictions is absolutely correct)
        strict_tp = [i for i in range(len(texts)) if gold_tags[i] in predicted_tags]
        print 'Acc(strict): ', len(strict_tp) / float(len(texts))
        # Lenient accuracy (1 if the predictions is part of the gold or vice versa)
        lenient_match = lambda predictions, gold: True if [1 for p in predictions if p in gold or gold in p] else False
        lenient_tp = [i for i in range(len(texts)) if lenient_match(predicted_tags[i], gold_tags[i])]
        print 'Acc(lenient): ', len(lenient_tp) / float(len(texts))
    return


def main(argv):
    mode = 0
    inputfile = ''
    message = 'asp_extract.py --input <filepath with urls, texts, abstracts> --mode <0: print aspects, 1: evaluate extracted aspects based on given abstracts>'
    try:
        opts, args = getopt.getopt(argv, "hi:m:", ["textsfile=", "mode="])
    except getopt.GetoptError:
        print message
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(message)
            sys.exit()
        elif opt in ('-i', '--input'):
            inputfile = arg
        elif opt in ('-m', '--mode'):
            mode = int(arg)
    extract_aspects(inputfile, mode)


def extract_aspects_from_text(text):
    predicted_tags = []
    text = postag(text)
    pos_matches = get_POS_text(text, top_pos_patterns)
    prediction = [' '.join(m) for m in pos_matches]  # if pos_matches else None
    predicted_tags.append(prediction)
    return predicted_tags


@app.route("/aspect_extractor/extract_aspects", methods=["POST"])
def extract_aspects_method():
    data = request.form
    predicted_tags = []

    if data['text']:
        predicted_tags = extract_aspects_from_text(data['text'])

    results = []
    if predicted_tags:
        for prediction in predicted_tags:
            tmp = ', '.join(prediction)
            results.append(tmp.decode('utf-8'))

    content = {'content': results}
    return json.dumps(content, ensure_ascii=False, separators=(',', ': '), indent=4)

if __name__ == '__main__':
    import json
    # app.run(host="127.0.0.1", debug=True)
    app.run(host="127.0.0.1",port=5001, threaded=True)
