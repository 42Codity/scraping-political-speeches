import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from nltk.stem import WordNetLemmatizer

# Speculative cues taken from 
speculative_cues = ['may','might','can','would','should','could',
                    'think','suggest','question','presume',
                    'suspect','indicate','suppose','seem','appear','expect',
                    'probable','likely','possible','apparently','unsure',
                    'if','or','and/or','either','versus','vs']

# Modal verbs taken from Cambridge Dictionary (2022) 'Modal verbs and modality'
modal_verb_list = ['can','could','may','might','will','shall','would','should','must',
                   'dare','need','ought','used','going','able']

# Subjective adjectives taken from Wiebe (2000) 'Learning subjective adjectives from corpora'
subjective_adjective_list = pd.read_csv('https://people.cs.pitt.edu/~wiebe/pubs/aaai00/adjsMPQA', header=None)[0].to_list()
subjective_adjective_list = [word.strip() for word in subjective_adjective_list]

def measure_subjectivity(text_list,sent_list,
                         speculative_cues=speculative_cues,
                         modal_verb_list=modal_verb_list,
                         subjective_adjective_list=subjective_adjective_list):
    
    def measure_subjective_sentence_freq(sent_list):
        subjective_sent_count = None
        return subjective_sent_count/len(sent_list)

    def measure_speculative_sentence_freq(sent_list, speculative_cues=speculative_cues):
        wnl = WordNetLemmatizer()
        lemmatised_sent_list = [[wnl.lemmatize(word) for word in sent] for sent in sent_list]
        speculative_sent_count = sum([1 for lemma_sent in lemmatised_sent_list if any([lemma in speculative_cues for lemma in lemma_sent])])
        return speculative_sent_count/len(sent_list)

    def measure_modal_verb_freq(text_list, modal_verb_list=modal_verb_list):
        modal_verb_count = sum([word in modal_verb_list for word in text_list])
        return modal_verb_count/len(text_list)

    def measure_subjective_adjective_freq(text_list, subjective_adjective_list=subjective_adjective_list):
        subjective_adjective_count = sum([word in subjective_adjective_list for word in text_list])
        return subjective_adjective_count/len(text_list)
    
    subjectivity_feature_dict = {'subjective_sentence_freq':measure_subjective_sentence_freq(sent_list),
                                 'speculative_sentence_freq':measure_speculative_sentence_freq(sent_list),
                                 'modal_verb_freq':measure_modal_verb_freq(text_list),
                                 'subjective_adjective_freq':measure_subjective_adjective_freq(text_list)}
    
    return subjectivity_feature_dict