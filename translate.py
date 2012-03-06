#!/usr/bin/env python
from collections import defaultdict 
import re

dictionary = defaultdict(list)
text = []

def load_dict(filename):
  dictfile = open(filename)
  for line in dictfile:
    word = line.split(":")[0].lower()
    deftext = line.split(":")[1].lower()
    definitions = []
    for definition in deftext.split(","):
      definitions.append(definition.strip())
    dictionary[word] = definitions
  dictfile.close()

def get_definitions(word,pos):
  if pos in locals():
    return dictionary[word+'_'+pos]
  else:
    return dictionary[word]

def load_text(filename):
  sentence_delim = '(\?|\.)\s?'
  textfile = open(filename)
  for line in textfile:
    sentences = re.split(sentence_delim,line)
    for sentence, delim in zip(sentences[::2],sentences[1::2]):
      words = sentence.split(' ')
      if len(words) == 1 and words[0] == '\n': continue
      words.append(delim[0])
      text.append(words)
  textfile.close()

load_text('text.txt')
load_dict('dict.txt')

