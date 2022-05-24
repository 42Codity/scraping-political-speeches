import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import nltk
import math
nltk.download('wordnet')

def __init__():

# Sentiment polarity trained on data from UK Hansard contributions
# See Rheault, et al. (2016) 'Measuring emotion in parliamentary debates with automated text analysis'
sentiment = pd.read_csv('https://raw.githubusercontent.com/lrheault/emotion/master/lexicon-polarity.csv')
sentiment_dict = {lemma:sentiment.polarity[idx] for idx,lemma in enumerate(sentiment.lemma)}

# Hedges taken from Hyland (2019) Metadiscourse: Exploring Interaction in Writing
hedge_list = ['about','almost','apparent','apparently','appear','appeared','appears','approximately',
              'argue','argued','argues','around','assume','assumed','broadly','claim','claimed','claims',
              'could','couldn','doubt','doubtful','essentially','estimate','estimated','fairly','feel',
              'feels','felt','frequently','generally','guess','indicate','indicated','indicates','largely',
              'likely','mainly','may','maybe','might','mostly','often','opinion','ought','perhaps',
              'perspective','plausible','plausibly','possible','possibly','postulate','postulated',
              'postulates','presumable','presumably','probable','probably','quite','rather','relatively',
              'roughly','seems','should','sometimes','somewhat','suggest','suggested','suggests','suppose',
              'supposed','supposes','suspect','suspects','tend','tended','tends','typical','typically',
              'uncertain','uncertainly','unclear','unclearly','unlikely','usually','would','wouldn','view']

def measure_persuasion(text_list, 
                       sentiment_dict=sentiment_dict, hedge_list=hedge_list, 
                       pos_threshold=0.5,neg_threshold=-0.5):
    
    # Set-up lemmatiser
    from nltk.stem import WordNetLemmatizer
    wnl = WordNetLemmatizer()
    # We need a lemmatised text list for matching with the sentiment dict
    lemmatised_text_list = [wnl.lemmatize(word) for word in text_list]
    
    # Number of definite articles, i.e. 'the', in the text
    num_definite_articles = sum([1 for word in text_list if word=='the'])
    share_definite_articles = num_definite_articles/len(text_list)
    
    # Number of positive/negative words
    sentiment = [sentiment_dict[lemma] if lemma in sentiment_dict.keys() else np.nan for lemma in lemmatised_text_list]
    num_positive_words = sum([1 for word_sent in sentiment if word_sent >= pos_threshold])
    share_positive_words = num_positive_words/len(text_list)
    num_negative_words = sum([1 for word_sent in sentiment if word_sent <= neg_threshold])
    share_negative_words = num_negative_words/len(text_list)
    
    # Number of personal pronouns (1st and 2nd person)
    num_personal_pronouns = sum([1 for word in text_list if word in ['i','you','we','us']])
    share_personal_pronouns = num_personal_pronouns/len(text_list)
    
    # Number of impersonal pronouns (3rd person)
    num_impersonal_pronouns = sum([1 for word in text_list if word in ['they','them']])
    share_impersonal_pronouns = num_impersonal_pronouns/len(text_list)
    
    # Number of hedges
    num_hedges = sum([1 for word in text_list if word in hedge_list])
    share_hedges = num_hedges/len(text_list)
    
    # Foreword length
    length = len(text_list)
    
    # TO DO: Add scalar word-level attributes (arousal, concreteness, dominance, valence)
    # Add word entropy/type-to-token ratio
    
    feature_dict = {'length':length,
                    'share_definite_articles':share_definite_articles,
                    'share_positive_words':share_positive_words,
                    'share_negative_words':share_negative_words,
                    'share_personal_pronouns':share_personal_pronouns,
                    'share_impersonal_pronouns':share_impersonal_pronouns,
                    'share_hedges':share_hedges}
    
    return feature_dict