import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from nltk.stem import WordNetLemmatizer

# Deictic words taken from Culpeper and Haugh (2014) Pragmatics and the English Language
deictic_word_list = ['the','this','these','that','those','they','them']

# Hedges taken from Hyland (2019) Metadiscourse: Exploring Interaction in Writing
approximator_word_list = ['about','almost','approximately','around','broadly','essentially','fairly',
                          'frequently','generally','largely','mainly','mostly','often','quite','rather',
                          'relatively','roughly','sometimes','somewhat','typical','typically','usually']
shield_word_list = ['apparent','apparently','appear','appeared','appears','argue','argued','argues',
                    'assume','assumed','claim','claimed','claims','could','couldn','doubt','doubtful',
                    'estimate','estimated','feel','feels','felt','guess','indicate','indicated','indicates',
                    'likely','may','maybe','might','opinion','ought','perhaps','perspective','plausible',
                    'plausibly','possible','possibly','postulate','postulated','postulates','presumable',
                    'presumably','probable','probably','seems','should','suggest','suggested','suggests',
                    'suppose','supposed','supposes','suspect','suspects','tend','tended','tends','uncertain',
                    'uncertainly','unclear','unclearly','unlikely','would','wouldn','view']

# Boosters taken from Hyland (1998) Boosting, Hedging and the Negotiation of Academic Knowledge
booster_word_list = ['actually','always','argue','assuredly','certain','certainly','certainty','clear',
                     'clearly','conclude','conclusive','confirm','convincing','course','decidedly','deduce',
                     'definitely','demonstrate','determine','discern','doubtless','essential','establish',
                     'evidence','evident','evidently','fact','formally','impossible','inconceivable',
                     'incontrovertible','inevitable','know','known','manifest','most','must','necessarily',
                     'never','obvious','obviously','patently','precisely','prove','should','show','sure',
                     'surely','true','unambiguously','unarguably','undeniably','undoubtedly','unequivocal',
                     'unmistakably','unquestionably','will','wrong']

# Semantic size lexicon taken from Scott, et al. (2019) 'The Glasgow Norms: Ratings of 5,500 words on nine scales'
df = pd.read_csv(os.path.join(os.path.dirname(__file__),'lexicon_data/glasgow.csv'))
df = df[['Words','SIZE']]
df = df.drop(0, axis=0)
df.SIZE = df.SIZE.apply(lambda x: float(x)/10) # Size is originally on a 0-10 scale - so rescale to 0-1
semantic_size_lexicon = dict()
for row in df.iterrows():
    semantic_size_lexicon[row[1]['Words']] = row[1]['SIZE']

def measure_vagueness(text_list, 
                       deictic_word_list=deictic_word_list,
                       approximator_word_list=approximator_word_list,
                       shield_word_list=shield_word_list,
                       booster_word_list=booster_word_list,
                       semantic_size_lexicon=semantic_size_lexicon):
    
    def measure_inverse_deictic_word_freq(text_list, deictic_word_list=deictic_word_list):
        deictic_word_count = sum([word in deictic_word_list for word in text_list])
        return 1-(deictic_word_count/len(text_list))
    
    def measure_approximator_word_freq(text_list, approximator_word_list=approximator_word_list):
        approximator_word_count = sum([word in approximator_word_list for word in text_list])
        return approximator_word_count/len(text_list)

    def measure_inverse_shield_word_freq(text_list, shield_word_list=shield_word_list):
        shield_word_count = sum([word in shield_word_list for word in text_list])
        return 1-(shield_word_count/len(text_list))

    def measure_booster_word_freq(text_list, booster_word_list=booster_word_list):
        booster_word_count = sum([word in booster_word_list for word in text_list])
        return booster_word_count/len(text_list)

    def measure_avg_semantic_size(text_list, semantic_size_lexicon=semantic_size_lexicon):
        wnl = WordNetLemmatizer()
        lemmatised_text_list = [wnl.lemmatize(word) for word in text_list]
        lemma_score_list = [float(semantic_size_lexicon[word]) if word in semantic_size_lexicon.keys() else np.nan for word in lemmatised_text_list]
        return np.nanmean(lemma_score_list)
    
    vagueness_feature_dict = {'inverse_deictic_word_freq':measure_inverse_deictic_word_freq(text_list),
                              'approximator_word_freq':measure_approximator_word_freq(text_list),
                              'inverse_shield_word_freq':measure_inverse_shield_word_freq(text_list),
                              'booster_word_freq':measure_booster_word_freq(text_list),
                              'avg_semantic_size':measure_avg_semantic_size(text_list)}
    
    return vagueness_feature_dict