import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import tensorflow as tf
import regex as re
import os
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize
from scorers.cleaning import *

# Load pre-trained TensorFlow models
# ...Anger
saved_anger_path = os.path.join(os.path.dirname(__file__),'classifiers/anger_classifier')
anger_estimator = tf.saved_model.load(saved_anger_path)
# ...Fear
saved_fear_path = os.path.join(os.path.dirname(__file__),'classifiers/fear_classifier')
fear_estimator = tf.saved_model.load(saved_fear_path)
# ...Joy
saved_joy_path = os.path.join(os.path.dirname(__file__),'classifiers/joy_classifier')
joy_estimator = tf.saved_model.load(saved_joy_path)
# ...Sadness
saved_sadness_path = os.path.join(os.path.dirname(__file__),'classifiers/sadness_classifier')
sadness_estimator = tf.saved_model.load(saved_sadness_path)

# Arousal and valence lexicon taken from Scott, et al. (2019) 'The Glasgow Norms: Ratings of 5,500 words on nine scales'
df = pd.read_csv(os.path.join(os.path.dirname(__file__),'lexicon_data/glasgow.csv'))
df = df[['Words','AROU','VAL']]
df = df.drop(0, axis=0)
df.AROU = df.AROU.apply(lambda x: float(x)/10) # Arousal is originally on a 0-10 scale - so rescale to 0-1
df.VAL = df.VAL.apply(lambda x: abs(float(x)-5)/5) # Valence is on a 0-10 scale - rescale to give absolute distance from 5 on a 0-1 scale (i.e. 5:=0, 10:=1, 0:=1)
a_glasgow_lexicon,v_glasgow_lexicon = dict(),dict()
for row in df.iterrows():
    a_glasgow_lexicon[row[1]['Words']] = row[1]['AROU']
    v_glasgow_lexicon[row[1]['Words']] = row[1]['VAL']

# Arousal and valence lexicon from from Warriner, et al. (2013) 'Norms of valence, arousal, and dominance for 13,915 English lemmas'
df = pd.read_csv(os.path.join(os.path.dirname(__file__),'lexicon_data/warriner.csv'))
df = df[['Word','A.Mean.Sum','V.Mean.Sum']]
df['A.Mean.Sum'] = df['A.Mean.Sum'].apply(lambda x: float(x)/10) # Arousal is originally on a 0-10 scale - so rescale to 0-1
df['V.Mean.Sum'] = df['V.Mean.Sum'].apply(lambda x: abs(float(x)-5)/5) # Valence is on a 0-10 scale - rescale to give absolute distance from 5 on a 0-1 scale (i.e. 5:=0, 10:=1, 0:=1)
a_warriner_lexicon,v_warriner_lexicon = dict(),dict()
for row in df.iterrows():
    a_warriner_lexicon[row[1]['Word']] = row[1]['A.Mean.Sum']
    v_warriner_lexicon[row[1]['Word']] = row[1]['V.Mean.Sum']
    
# Valence lexicon from Rheault, et al. (2016)
df = pd.read_csv('https://raw.githubusercontent.com/lrheault/emotion/master/lexicon-polarity.csv')
df = df[['lemma','polarity']]
df['polarity'] = df['polarity'].apply(lambda x: abs(float(x))) # Valence is on a -1 - 1 scale - rescale to give absolute distance from 5 on a 0-1 scale (i.e. 5:=0, 10:=1, 0:=1)
v_rheault_lexicon = dict()
for row in df.iterrows():
    v_rheault_lexicon[row[1]['lemma']] = row[1]['polarity']

def measure_emotionality(text_list, raw_text,
                       a_glasgow_lexicon=a_glasgow_lexicon,
                       v_glasgow_lexicon=v_glasgow_lexicon,
                       a_warriner_lexicon=a_warriner_lexicon,
                       v_warriner_lexicon=v_warriner_lexicon,
                       v_rheault_lexicon=v_rheault_lexicon, 
                       anger_estimator=anger_estimator,
                       fear_estimator=fear_estimator,
                       joy_estimator=joy_estimator,
                       sadness_estimator=sadness_estimator):
    
    def measure_avg_anger_sentence_score(sent_list, anger_estimator=anger_estimator):
        anger_scores = []
        # For each sentence:
        for sent in sent_list:
            example = tf.train.Example() # ...prepare an example for the sentence to be wrapped in
            example.features.feature['sentence'].bytes_list.value.extend([bytes(sent, "utf-8")]) # ...encode the sentence as UTF-18
            anger_scores.append(anger_estimator.signatures['predict'](examples=tf.constant([example.SerializeToString()]))['predictions'][0][0].numpy()) # ...append anger score to list
        return np.nanmean(anger_scores)

    def measure_avg_fear_sentence_score(sent_list, fear_estimator=fear_estimator):
        fear_scores = []
        # For each sentence:
        for sent in sent_list:
            example = tf.train.Example() # ...prepare an example for the sentence to be wrapped in
            example.features.feature['sentence'].bytes_list.value.extend([bytes(sent, "utf-8")]) # ...encode the sentence as UTF-18
            fear_scores.append(fear_estimator.signatures['predict'](examples=tf.constant([example.SerializeToString()]))['predictions'][0][0].numpy()) # ...append fear score to list
        return np.nanmean(fear_scores)
    
    def measure_avg_joy_sentence_score(sent_list, joy_estimator=joy_estimator):
        joy_scores = []
        # For each sentence:
        for sent in sent_list:
            example = tf.train.Example() # ...prepare an example for the sentence to be wrapped in
            example.features.feature['sentence'].bytes_list.value.extend([bytes(sent, "utf-8")]) # ...encode the sentence as UTF-18
            joy_scores.append(joy_estimator.signatures['predict'](examples=tf.constant([example.SerializeToString()]))['predictions'][0][0].numpy()) # ...append fear score to list
        return np.nanmean(joy_scores)
    
    def measure_avg_sadness_sentence_score(sent_list, sadness_estimator=sadness_estimator):
        sadness_scores = []
        # For each sentence:
        for sent in sent_list:
            example = tf.train.Example() # ...prepare an example for the sentence to be wrapped in
            example.features.feature['sentence'].bytes_list.value.extend([bytes(sent, "utf-8")]) # ...encode the sentence as UTF-18
            sadness_scores.append(sadness_estimator.signatures['predict'](examples=tf.constant([example.SerializeToString()]))['predictions'][0][0].numpy()) # ...append fear score to list
        return np.nanmean(sadness_scores)

    def measure_avg_arousal_glasgow(text_list, a_glasgow_lexicon=a_glasgow_lexicon):
        wnl = WordNetLemmatizer()
        lemmatised_text_list = [wnl.lemmatize(word) for word in text_list]
        lemma_score_list = [float(a_glasgow_lexicon[word]) if word in a_glasgow_lexicon.keys() else np.nan for word in lemmatised_text_list]
        return np.nanmean(lemma_score_list)
                      
    def measure_avg_arousal_warriner(text_list, a_warriner_lexicon=a_warriner_lexicon):
        wnl = WordNetLemmatizer()
        lemmatised_text_list = [wnl.lemmatize(word) for word in text_list]
        lemma_score_list = [float(a_warriner_lexicon[word]) if word in a_warriner_lexicon.keys() else np.nan for word in lemmatised_text_list]
        return np.nanmean(lemma_score_list)
                      
    def measure_avg_valence_glasgow(text_list, v_glasgow_lexicon=v_glasgow_lexicon):
        wnl = WordNetLemmatizer()
        lemmatised_text_list = [wnl.lemmatize(word) for word in text_list]
        lemma_score_list = [float(v_glasgow_lexicon[word]) if word in v_glasgow_lexicon.keys() else np.nan for word in lemmatised_text_list]
        return np.nanmean(lemma_score_list)
                      
    def measure_avg_valence_warriner(text_list, v_warriner_lexicon=v_warriner_lexicon):
        wnl = WordNetLemmatizer()
        lemmatised_text_list = [wnl.lemmatize(word) for word in text_list]
        lemma_score_list = [float(v_warriner_lexicon[word]) if word in v_warriner_lexicon.keys() else np.nan for word in lemmatised_text_list]
        return np.nanmean(lemma_score_list)
    
    def measure_avg_valence_rheault(text_list, v_rheault_lexicon=v_rheault_lexicon):
        wnl = WordNetLemmatizer()
        lemmatised_text_list = [wnl.lemmatize(word) for word in text_list]
        lemma_score_list = [float(v_rheault_lexicon[word]) if word in v_rheault_lexicon.keys() else np.nan for word in lemmatised_text_list]
        return np.nanmean(lemma_score_list)
    
    sent_list = sent_tokenize(raw_text)
    
    emotionality_feature_dict = {'avg_arousal_glasgow':measure_avg_arousal_glasgow(text_list),
                                 'avg_arousal_warriner':measure_avg_arousal_warriner(text_list),
                                 'avg_valence_glasgow':measure_avg_valence_glasgow(text_list),
                                 'avg_valence_warriner':measure_avg_valence_warriner(text_list),
                                 'avg_valence_rheault':measure_avg_valence_rheault(text_list),
                                 'avg_anger_sentence_score':measure_avg_anger_sentence_score(sent_list),
                                 'avg_fear_sentence_score':measure_avg_fear_sentence_score(sent_list),
                                 'avg_joy_sentence_score':measure_avg_joy_sentence_score(sent_list),
                                 'avg_sadness_sentence_score':measure_avg_sadness_sentence_score(sent_list)}
    
    return emotionality_feature_dict