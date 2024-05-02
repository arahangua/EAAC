import stanza

# stanza.download('en')  # download English model

def extract_triplets(nl_eaac_report):
    nlp = stanza.Pipeline('en')  # initialize English neural pipeline
    # doc = nlp("Apple acquired Beats for $3 billion in 2014.")
    doc = nlp(nl_eaac_report)

    triplets = []
    for sent in doc.sentences:
        for word in sent.words:
            if word.deprel in ('nsubj', 'nsubj:pass') and sent.words[word.head-1].upos == 'VERB':
                subject = word.text
                predicate = sent.words[word.head-1].text
                object = None
                for child in sent.words:
                    if child.head == word.head and child.deprel in ('obj'):
                        object = child.text
                        print(f'{object}, {child.deprel}')

                if object:
                    triplets.append((subject, predicate, object))

    print(f"extracted triplets:")
    print(triplets)






