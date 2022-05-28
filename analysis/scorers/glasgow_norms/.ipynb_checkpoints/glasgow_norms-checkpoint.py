import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import nltk
import math
nltk.download('wordnet')

def generate_score_dict(csv_name, word_colname, score_colnames, drop_first_row=False):
    df = pd.read_csv(os.path.join(os.path.dirname(__file__),csv_name))
    df = df[[word_colname]+score_colnames]
    if drop_first_row:
        df = df.drop(0, axis=0)
    score_dict = {word:dict() for word in df[word_colname]}
    dims = df.drop(word_colname, axis=1).columns
    for row in df.iterrows():
        score_dict[row[1][word_colname]] = {dim:row[1][dim] for dim in dims}
    return score_dict

# Glasgow Norms (denoted by the suffix '_glasnorm') are taken from Scott, et al. (2019) 'The Glasgow Norms: Ratings of 5,500 words on nine scales'
glasgow_dict = generate_score_dict('glasgow.csv', 'Words', ['AROU','VAL','DOM','CNC','IMAG','FAM','AOA','SIZE','GEND'])
    
# Brysbaert ratings (denoted by the suffix '_brys') are taken from Brysbaert, et al. (2014) 'Concreteness ratings for 40 thousand generally known English word lemmas'
brysbaert_dict = generate_score_dict('brysbaert.csv', 'Word', ['Conc.M'])

# Warriner ratings (suffice '_warr') are taken from Warriner, et al. (2013) 'Norms of valence, arousal, and dominance for 13,915 English lemmas'
warriner_dict = generate_score_dict('warriner.csv', 'Word', ['A.Mean.Sum','V.Mean.Sum','D.Mean.Sum'])

def measure_norms(text_list, threshold=4):
    
    # Set-up lemmatiser
    from nltk.stem import WordNetLemmatizer
    wnl = WordNetLemmatizer()
    # We need a lemmatised text list for matching with the sentiment dict
    lemmatised_text_list = [wnl.lemmatize(word) for word in text_list]
    
    # The score dimensions are stored as keys in the dictionary
    ## Glasgow Norms
    score_dims_glasnorm = [score_dict.keys() for score_dict in glasgow_dict.values()][0]
    score_text_lists_glasnorm = {score_dim:[float(glasgow_dict[word][score_dim]) if word in glasgow_dict.keys() else np.nan for word in lemmatised_text_list] for score_dim in score_dims_glasnorm}
    ## Brysbaert, et al.
    score_dims_brys = [score_dict.keys() for score_dict in brysbaert_dict.values()][0]
    score_text_lists_brys = {score_dim:[float(brysbaert_dict[word][score_dim]) if word in brysbaert_dict.keys() else np.nan for word in lemmatised_text_list] for score_dim in score_dims_brys}
    ## Warriner, et al.
    score_dims_warr = [score_dict.keys() for score_dict in warriner_dict.values()][0]
    score_text_lists_warr = {score_dim:[float(warriner_dict[word][score_dim]) if word in warriner_dict.keys() else np.nan for word in lemmatised_text_list] for score_dim in score_dims_warr}
    
    arousal_avg_glasnorm = np.nanmean(score_text_lists_glasnorm['AROU'])
    valence_avg_glasnorm = np.nanmean(score_text_lists_glasnorm['VAL'])
    dominance_avg_glasnorm = np.nanmean(score_text_lists_glasnorm['DOM'])
    concreteness_avg_glasnorm = np.nanmean(score_text_lists_glasnorm['CNC'])
    imageability_avg_glasnorm = np.nanmean(score_text_lists_glasnorm['IMAG'])
    familiarity_avg_glasnorm = np.nanmean(score_text_lists_glasnorm['FAM'])
    ageacquisition_avg_glasnorm = np.nanmean(score_text_lists_glasnorm['AOA'])
    semanticsize_avg_glasnorm = np.nanmean(score_text_lists_glasnorm['SIZE'])
    genderassociation_avg_glasnorm = np.nanmean(score_text_lists_glasnorm['GEND'])
    
    concreteness_avg_brys = np.nanmean(score_text_lists_warr['Conc.M'])
    
    arousal_avg_warr = np.nanmean(score_text_lists_warr['A.Mean.Sum'])
    valence_avg_warr = np.nanmean(score_text_lists_warr['V.Mean.Sum'])
    dominance_avg_warr = np.nanmean(score_text_lists_warr['D.Mean.Sum'])
    
    
    feature_dict = {'arousal_avg_glasnorm':arousal_avg_glasnorm,
                    'arousal_avg_warr':arousal_avg_warr,
                    'valence_avg_glasnorm':valence_avg_glasnorm,
                    'valence_avg_warr':valence_avg_warr,
                    'dominance_avg_glasnorm':dominance_avg_glasnorm,
                    'dominance_avg_warr':dominance_avg_warr,
                    'concreteness_avg_glasnorm':concreteness_avg_glasnorm,
                    'concreteness_avg_brys':concreteness_avg_brys,
                    'imageability_avg_glasnorm':imageability_avg_glasnorm,
                    'familiarity_avg_glasnorm':familiarity_avg_glasnorm,
                    'ageacquisition_avg_glasnorm':ageacquisition_avg_glasnorm,
                    'semanticsize_avg_glasnorm':semanticsize_avg_glasnorm,
                    'genderassociation_avg_glasnorm':genderassociation_avg_glasnorm}
    
    return feature_dict