#!/usr/bin/env python
from collections import defaultdict
from nltk import tag
import re
import text

tobe_list = ['am','are','is','was','were']

def print_text(sentences):
  for s in sentences:
    sentence = ' '.join(s)
    sentence = re.sub('\s,\s',', ',sentence)
    sentence = re.sub('\s\.','.',sentence)
    sentence = re.sub('\s\?','?',sentence)
    sentence = sentence[0].upper() + sentence[1:]
    print sentence

def reorder_subclause(tagged_sentence):
  in_subclause = False
  prev_is_noun_or_verb = False
  subject_index = -1
  verb_index = -1
  for index,tup in enumerate(tagged_sentence):
    if prev_is_noun_or_verb and tup[1] == 'IN':
      in_subclause = True
      subject_index = -1
      verb_index = -1
    if tup[1] == 'NN' or tup[1] == 'NNS' or tup[1][:2] == 'VB':
      prev_is_noun_or_verb = True
    else:
      prev_is_noun_or_verb = False
    if in_subclause:
      if subject_index != -1 and verb_index==-1 and (tup[1][:2]=='VB' or tup[1] == 'MD'):
        verb_index = index
      elif subject_index == -1 and (tup[1][:2]=='NN' or tup[1]=='PRP'):
        subject_index = index
    if subject_index != -1 and verb_index  != -1:
      result = tagged_sentence
      verb = result.pop(verb_index)
      result.insert(subject_index+1,verb)
      return result
  return tagged_sentence

def reorder_adverb_verb(tagged_sentence):
  if len(tagged_sentence) > 2 and tagged_sentence[0][1]=='RB' and tagged_sentence[1][1][:2]=='VB' and (tagged_sentence[2][1] == 'PRP' or tagged_sentence[2][1] == 'EX' or tagged_sentence[2][1][:2] == 'NN'):
    result = tagged_sentence
    verb = result.pop(1)
    result.insert(2,verb)
    return result
  else:
    return tagged_sentence

def is_part_of_tobe(word):
	return word in tobe_list

def fix_question(sentence):
  if sentence[-1][0] == '?':
    if sentence[0][1] == "VBD" and not is_part_of_tobe(sentence[0][0]):
      for i, word in enumerate(sentence):
        #print word
        if len(word[1]) > 1 and word[1][1] == 'N':
          newsent = [sentence[i-1], sentence[i]]
          newsent = newsent+sentence[i:i-2]
          newsent.append(sentence[0])
          sentence = newsent + sentence[i+1:]
          break
  return sentence

def disamb_it(tagged_sentence):
  sentence_len = len(tagged_sentence)
  result = []
  for i,tup in enumerate(tagged_sentence):
    result_tup = tup
    if i < sentence_len-1 and tup[0]=='it' and tagged_sentence[i+1][1][:2] == 'NN':
      result_tup = ('the','DT')
    result.append(result_tup)
  return result

def disamb_which(tagged_sentence):
  sentence_len = len(tagged_sentence)
  result = []
  for i,tup in enumerate(tagged_sentence):
    result_tup = tup
    if i > 0 and tup[0]=='which' and tagged_sentence[i-1][1] == 'PRP':
      result_tup = ('who','WPRO')
    result.append(result_tup)
  return result

#if you don't want to use the cache, use this line:
#text.load('text.txt','dict.txt',True,False)

#otherwise, just do this:
text.load()

#grab the tagged words from the text module
tagged = text.tagged

for i,sentence in enumerate(tagged):
  print sentence
  tagged[i] = disamb_it(sentence)

print "Reordering..."

reordered = []
for i,sentence in enumerate(tagged):
  tagged[i] = fix_question(sentence)
  tagged[i]= reorder_subclause(tagged[i])
  tagged[i]= reorder_adverb_verb(tagged[i])
  tagged[i]= disamb_which(tagged[i])
  not_tagged = []  
  for tup in tagged[i]:
    not_tagged.append(tup[0])
  reordered.append(not_tagged)

print_text(reordered)

