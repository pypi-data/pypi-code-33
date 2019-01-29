#!python

import json
import sys
import os 
import pprint
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize.casual import casual_tokenize
from spellchecker import SpellChecker
from termcolor import cprint

def print_highlight(line, words):
    '''Print the line, highlighting mis-spelled words'''
    for word in line.split():
        # if word in words:
        printed = False
        for msword in words:
            if msword in word.lower():
                cprint(word, 'blue', end=' ')
                printed = True
                break 
        if not printed:
            # uword = word.encode('utf8')
            # sys.stdout.buffer.write(uword)
            sys.stdout.write(word)
            sys.stdout.write(' ')
    sys.stdout.write('\n')
            
def handle_word(word):
    '''Deal with a mispelled workd.

    One can either: 
    - ignore the word
    - learn the word
    - accept the suggested word
    - propose a new word
    - stop processing
    '''
    if word in ignored_words:
        return
    if len(word)>10:
        spell.distance = 1
    cprint('Word:', 'red', end=' ')
    cprint(word, 'blue')
    suggested = spell.correction(word)
    print('suggested :', suggested)
    # candidates = spell.candidates(word)
    # if len(candidates)>1:
    #     print('candidates:')
    #     for i, candidate in enumerate(candidates):
    #         print('[{}] : {}'.format(i, candidate))
    spell.distance = 2
    answer = None
    while answer not in list('ilcsa'):
        answer = input('(i)gnore (l)earn, (a)ccept suggested, (c)hange, (s)top : ')
    if answer == 's':
        exit()
    elif answer == 'i':
        ignored_words.append(word)
        return None
    elif answer == 'l':
        spell.word_frequency.load_words([word])
        learnt_words.append(word)
        return None
    elif answer == 'c':
        confirmed = None
        new_word = None
        while confirmed != 'y': 
            new_word = input('change word to:')
            print(new_word)
            confirmed = input('are you sure? [y/n]')
        spell.word_frequency.load_words([word])
        learnt_words.append(new_word)
        return new_word
    elif answer == 'a':
        return suggested 


def update_line(line, word, new_word):
    '''Update the line by changing word by new_word.'''
    notebook_updated = True
    if word.isupper():
        new_word = new_word.upper()
    newline = line.replace(word, new_word)
    return newline


def check(cell):
    '''Spell check one markdown cell'''
    lines = cell['source']
    for i, line in enumerate(lines):
        # using casual tokenize to get rid of urls and emojis
        words = casual_tokenize(line)
        words = [word for word in words if not word.startswith('http')]
        newline = ' '.join(words)
        # this handles e.g. contractions: you're, etc
        words = tokenizer.tokenize(newline)
        misspelled = spell.unknown(words)
        if len(misspelled):
            print_highlight(line, misspelled)
            for word in misspelled:
                new_word = handle_word(word)
                # learnt_words.append(new_word)
                if new_word:
                    line = update_line(line, word, new_word)
            cell['source'][i] = line

def exit():
    '''Exit the program. 
    
    The user is offered the possibility to save the dictionary, 
    and the modified notebook. Please note that the notebook 
    is modified in place
    '''
    done_something = False
    if len(learnt_words):
        done_something = True
        answer = None
        while answer not in list('yn'):
            answer = input('Save dictionnary? [y/n]')
            if answer == 'y':
                with open(dict_fname, 'a') as dict_file:
                    for word in learnt_words: 
                        dict_file.write(word + '\n')
    # save modified file
    if notebook_updated:
        done_something = True
        answer = None
        while answer not in list('yn'):
            answer = input('Save file? [y/n]')
            if answer == 'y':
                fname = input_fname
                print('saving file')
                with open(fname, 'w') as output_file:
                    json.dump(notebook, output_file)
            elif answer == 'n':
                print('discarding changes')
    if not done_something:
        print('nothing to do!')
    sys.exit(0)
    

if __name__ == '__main__':
    '''Run spell checking on an ipython notebook 
'''
    from optparse import OptionParser
    parser = OptionParser()
    parser.set_usage('''usage: %prog [options] <jupyter_notebook>

Spell check jupyter notebook.
''')

    parser.add_option("-l", "--language",
                          dest="language", default='en',
                          help="specify language (fr or en for now, but others can be added easily)")
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_usage()
        sys.exit(1)
    
    if options.language not in ['fr','en']:
        print('language should be set to fr or en')
        sys.exit(1)

    notebook = None
    input_fname = args[0]
    with open(input_fname) as finput:
        notebook = json.load(finput)

    spell = SpellChecker(options.language)
    tokenizer = RegexpTokenizer(r'\w+')
    if options.language == 'en':
        dict_fname = os.path.expandvars('$HOME/.spellchecker_en.txt')
    else:
        dict_fname = os.path.expandvars('$HOME/.spellchecker_fr.txt')        
    with open(dict_fname, 'a'):
        os.utime(dict_fname, None)
    spell.word_frequency.load_text_file(dict_fname)

    learnt_words = []
    ignored_words = []
    notebook_updated = False
    
    cells = notebook['cells']
    cells_md = [cell for cell in cells if cell['cell_type'] == 'markdown']

    for cell in cells_md:
        check(cell)

    exit()
