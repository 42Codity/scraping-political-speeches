import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import nltk
import math
nltk.download('wordnet')

glasgow = pd.read_csv(os.path.join(os.path.dirname(__file__),'glasgow.csv'))
glasgow = glasgow[['Words','AROU','VAL','DOM','CNC','IMAG','FAM','AOA','SIZE','GEND']]
glasgow = glasgow.drop(0, axis=0)

glasgow_dict = {word:dict() for word in glasgow.Words}
dims = glasgow.drop('Words', axis=1).columns
for row in glasgow.iterrows():
    glasgow_dict[row[1].Words] = {dim:row[1][dim] for dim in dims}

def measure_norms(text_list, threshold=4):
    
    # Set-up lemmatiser
    from nltk.stem import WordNetLemmatizer
    wnl = WordNetLemmatizer()
    # We need a lemmatised text list for matching with the sentiment dict
    lemmatised_text_list = [wnl.lemmatize(word) for word in text_list]
    
    # The score dimensions are stored as keys in the dictionary
    score_dims = [score_dict.keys() for score_dict in glasgow_dict.values()][0]
    score_text_lists = {score_dim:[float(glasgow_dict[word][score_dim]) if word in glasgow_dict.keys() else np.nan for word in lemmatised_text_list] for score_dim in score_dims}
    
    arousal_avg = np.nanmean(score_text_lists['AROU'])
    valence_avg = np.nanmean(score_text_lists['VAL'])
    dominance_avg = np.nanmean(score_text_lists['DOM'])
    concreteness_avg = np.nanmean(score_text_lists['CNC'])
    imageability_avg = np.nanmean(score_text_lists['IMAG'])
    familiarity_avg = np.nanmean(score_text_lists['FAM'])
    ageacquisition_avg = np.nanmean(score_text_lists['AOA'])
    semanticsize_avg = np.nanmean(score_text_lists['SIZE'])
    genderassociation_avg = np.nanmean(score_text_lists['GEND'])
    
    arousal_pct = 100*np.sum([score>=threshold if not pd.isna(score) else False for score in score_text_lists['AROU']])/len(score_text_lists['AROU'])
    valence_pct = 100*np.sum([score>=threshold if not pd.isna(score) else False for score in score_text_lists['VAL']])/len(score_text_lists['VAL'])
    dominance_pct = 100*np.sum([score>=threshold if not pd.isna(score) else False for score in score_text_lists['DOM']])/len(score_text_lists['DOM'])
    concreteness_pct = 100*np.sum([score>=threshold if not pd.isna(score) else False for score in score_text_lists['CNC']])/len(score_text_lists['CNC'])
    imageability_pct = 100*np.sum([score>=threshold if not pd.isna(score) else False for score in score_text_lists['IMAG']])/len(score_text_lists['IMAG'])
    familiarity_pct = 100*np.sum([score>=threshold if not pd.isna(score) else False for score in score_text_lists['FAM']])/len(score_text_lists['FAM'])
    ageacquisition_pct = 100*np.sum([score>=threshold if not pd.isna(score) else False for score in score_text_lists['AOA']])/len(score_text_lists['AOA'])
    semanticsize_pct = 100*np.sum([score>=threshold if not pd.isna(score) else False for score in score_text_lists['SIZE']])/len(score_text_lists['SIZE'])
    genderassociation_pct = 100*np.sum([score>=threshold if not pd.isna(score) else False for score in score_text_lists['GEND']])/len(score_text_lists['GEND'])
    
    feature_dict = {'arousal_avg':arousal_avg,
                    'arousal_pct':arousal_pct,
                    'valence_avg':valence_avg,
                    'valence_pct':valence_pct,
                    'dominance_avg':dominance_avg,
                    'dominance_pct':dominance_pct,
                    'concreteness_avg':concreteness_avg,
                    'concreteness_pct':concreteness_pct,
                    'imageability_avg':imageability_avg,
                    'imageability_pct':imageability_pct,
                    'familiarity_avg':familiarity_avg,
                    'familiarity_pct':familiarity_pct,
                    'ageacquisition_avg':ageacquisition_avg,
                    'ageacquisition_pct':ageacquisition_pct,
                    'semanticsize_avg':semanticsize_avg,
                    'semanticsize_pct':semanticsize_pct,
                    'genderassociation_avg':genderassociation_avg,
                    'genderassociation_pct':genderassociation_pct}
    
    return feature_dict