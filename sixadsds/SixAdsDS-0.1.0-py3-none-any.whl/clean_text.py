"""
Functions for text preprocesing
"""

# Additional packages

from nltk.corpus import stopwords
import string
import re
import inflection
from nltk.stem import WordNetLemmatizer
from tqdm import tqdm

def lemmatize_word(string_list, engine = WordNetLemmatizer()):
    """
    Lemmatize words using word net
    """
    lemma_engine = engine
    cleaned_string = []
    
    for text in string_list:
        text = [lemma_engine.lemmatize(word) for word in text.split()]
        text = ' '.join(text)
        cleaned_string.append(text)     
        
    return cleaned_string    

def to_str(string_list):
    """
    Converts an object to string
    """
    cleaned_string = [str(x) for x in string_list]
    return cleaned_string

def rm_short_words(string_vec):
    """
    Removes words that are of length 2 or lower
    """
    cleaned_string = [re.sub(r'\b\w{1,2}\b', '', x) for x in string_vec]
    return cleaned_string
    
def to_single(string_list):
    """
    Converts a string to singular form
    """
    cleaned_string = []
    for text in string_list:
        text = [inflection.singularize(word) for word in text.split()]
        text = ' '.join(text)
        cleaned_string.append(text)
    return cleaned_string 

def to_lower(string_list):
    """
    Makes every word in a string vector lowercase
    """
    cleaned_string = [string.lower() for string in string_list]
    return cleaned_string
    
def rm_stop_words(string_list):
    """
    Removes common stop words from a string vector
    """
    cleaned_string = []
    stop_words = stopwords.words("english")   
    for text in string_list:
        text = [word for word in text.split() if word not in stop_words]
        text = ' '.join(text)
        cleaned_string.append(text)
    return cleaned_string    

def rm_punctuations(string_list):
    """
    Removes punctuations and other special characters from a string vector
    """
    cleaned_string = [re.sub(r"[^a-zA-Z0-9 ]","",s) for s in string_list]
    return cleaned_string

def rm_digits(string_list):
    """
    Removes digits from a string vector
    """
    regex = re.compile('[%s]' % re.escape(string.digits))
    cleaned_string = [regex.sub('', s) for s in string_list]
    return cleaned_string

def stem_words(string_list, stemmer):
    """
    A function to stemm the words in a given string vector
    """
    cleaned_string = []
    for text in string_list:
        text = [stemmer.stem(word) for word in text.split()]
        text = ' '.join(text)
        cleaned_string.append(text)
    return cleaned_string  

def clean_ws(string_list):
    """
    Cleans whitespaces
    """
    cleaned_string = [re.sub('\s+', ' ', s).strip() for s in string_list]
    return cleaned_string

def build_vocab(string_list, verbose =  True):
    """
    A function that creates a term frequency vocabulary from the text
    """
    vocab = {}
    for sentence in tqdm(string_list, disable = (not verbose)):
        for word in sentence.split():
            try:
                vocab[word] += 1
            except KeyError:
                vocab[word] = 1
    return vocab

def get_items_with_text(char, string_list, verbose = False):
    """
    A function that creates a term frequency vocabulary from the text
    """
    vocab = {}
    for sentence in tqdm(string_list, disable = (not verbose)):
        for word in sentence.split():
            try:
                vocab[word] += 1
            except KeyError:
                vocab[word] = 1
    return vocab