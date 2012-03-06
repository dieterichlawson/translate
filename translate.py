#!/usr/bin/env python
from collections import defaultdict 
import re

dictionary = defaultdict(list)
text = []

def load_text(filename):
  #loads the source text in Dutch from file 'filename'
  sentence_delim = '(\?|\.)\s?'
  comma_sub = '\s?,\s?'
  textfile = open(filename)
  for line in textfile:
    line = re.sub(comma_sub,' , ',line)
    line = line.lower()
    sentences = re.split(sentence_delim,line)
    for sentence, delim in zip(sentences[::2],sentences[1::2]):
      words = sentence.split(' ')
      if len(words) == 1 and words[0] == '\n': continue
      words.append(delim[0])
      text.append(words)
  textfile.close()

def load_dict(filename):
  #loads the dictionary from file 'filename'
  dictfile = open(filename)
  for line in dictfile:
    word = line.split(":")[0].lower()
    deftext = line.split(":")[1].lower()
    definitions = []
    for definition in deftext.split(","):
      definitions.append(definition.strip())
    dictionary[word] = definitions
    if '_' in word:
      dictionary[word.split('_')[0]].extend(definitions)
  dictfile.close()

def get_definitions(word,pos=None):
  if pos != None and len(dictionary[word+'_'+pos]) > 0:
    return dictionary[word+'_'+pos]
  else:
    return dictionary[word]

def get_pos(word,index,sentence):
  return None

def translate(source,dictionary):
  punctuation = '.,?'
  translated = []
  for sentence in source:
    trans_sentence = []
    for i,word in enumerate(sentence):
      if len(word) == 1 and word in punctuation:
        trans_sentence.append(word)
        continue
      pos = get_pos(word,i,sentence)
      if pos != None:
        trans_sentence.append(get_definitions(word,pos)[0])
      else:
        trans_sentence.append(get_definitions(word)[0])
    translated.append(trans_sentence)
  return translated

def print_text(sentences):
  for s in sentences:
    sentence = ' '.join(s)
    sentence = re.sub('\s,\s',', ',sentence)
    sentence = re.sub('\s\.','.',sentence)
    sentence = re.sub('\s\?','?',sentence)
    sentence = sentence[0].upper() + sentence[1:]
    print sentence

load_text('text.txt')
load_dict('dict.txt')

translated = translate(text,dictionary)
print_text(translated)
#for sentence in text:
#  print sentence
#for item in dictionary.items():
#  print "%s: %s" % item
