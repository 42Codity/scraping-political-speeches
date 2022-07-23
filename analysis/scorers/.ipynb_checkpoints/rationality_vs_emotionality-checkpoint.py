import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import tensorflow as tf
import regex as re
import os
from nltk.stem import WordNetLemmatizer
from scorers.cleaning import *

# Load pre-trained TensorFlow model
saved_model_path = os.path.join(os.path.dirname(__file__),'objectivity_vs_subjectivity\subjectivity_classifier')
subjectivity_estimator = tf.saved_model.load(saved_model_path)

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

def measure_subjectivity(text_list,raw_text,
                         subjectivity_estimator=subjectivity_estimator,
                         speculative_cues=speculative_cues,
                         modal_verb_list=modal_verb_list,
                         subjective_adjective_list=subjective_adjective_list):
    
    def measure_subjective_sentence_freq(sent_list, subjectivity_estimator=subjectivity_estimator):
        subjectivity_predictions = []
        # For each sentence:
        for sent in sent_list:
            example = tf.train.Example() # ...prepare an example for the sentence to be wrapped in
            example.features.feature['sentence'].bytes_list.value.extend([bytes(sent, "utf-16")]) # ...encode the sentence as UTF-18
            subjectivity_predictions.append(subjectivity_estimator.signatures['predict'](examples=tf.constant([example.SerializeToString()]))['class_ids'][0][0].numpy()) # ...append subjectivity prediction to list
        return sum(subjectivity_predictions)/len(subjectivity_predictions)

    def measure_avg_subjective_sentence_score(sent_list, subjectivity_estimator=subjectivity_estimator):
        subjectivity_scores = []
        for sent in sent_list:
            example = tf.train.Example() # ...prepare an example for the sentence to be wrapped in
            example.features.feature['sentence'].bytes_list.value.extend([bytes(sent, "utf-16")]) # ...encode the sentence as UTF-18
            subjectivity_scores.append(subjectivity_estimator.signatures['predict'](examples=tf.constant([example.SerializeToString()]))['probabilities'][0][1].numpy()) # ...append subjectivity score to list
        return np.nanmean(subjectivity_scores)

    def measure_speculative_sentence_freq(sent_list, speculative_cues=speculative_cues):
        wnl = WordNetLemmatizer()
        cleaned_sent_list = [clean(sent) for sent in sent_list]
        lemmatised_sent_list = [[wnl.lemmatize(word) for word in sent] for sent in cleaned_sent_list]
        speculative_sent_count = sum([1 for lemma_sent in lemmatised_sent_list if any([lemma in speculative_cues for lemma in lemma_sent])])
        return speculative_sent_count/len(sent_list)

    def measure_modal_verb_freq(text_list, modal_verb_list=modal_verb_list):
        modal_verb_count = sum([word in modal_verb_list for word in text_list])
        return modal_verb_count/len(text_list)

    def measure_subjective_adjective_freq(text_list, subjective_adjective_list=subjective_adjective_list):
        subjective_adjective_count = sum([word in subjective_adjective_list for word in text_list])
        return subjective_adjective_count/len(text_list)
    
    sent_list = re.sub('\s+',' ',raw_text).split('. ')
    
    subjectivity_feature_dict = {'subjective_sentence_freq':measure_subjective_sentence_freq(sent_list),
                                 'avg_subjective_sentence_score':measure_avg_subjective_sentence_score(sent_list),
                                 'speculative_sentence_freq':measure_speculative_sentence_freq(sent_list),
                                 'modal_verb_freq':measure_modal_verb_freq(text_list),
                                 'subjective_adjective_freq':measure_subjective_adjective_freq(text_list)}
    
    return subjectivity_feature_dict