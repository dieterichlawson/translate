#!/usr/bin/env python
from collections import defaultdict
from nltk import tag
import re
import text

tobe_list = ['am','are','is','was','were']

def get_definition_with_rules(currIndex,words):
  currWord = words[currIndex]
  nextWord = ''
  if currIndex < len(words) -1: nextWord = words[currIndex+1]
  prevWords = words[:currIndex]
  if currWord=='dan':
    if prevWords[-1][-2:]=='er':
      return 'than'
    else:
      return 'then'
  elif currWord=='mis':
    lowerPrev = prevWords[-1]
    if lowerPrev =='de':
      return 'mass'
    elif lowerPrev == 'ik':
      return 'miss'
    else:
      return 'wrong'
  elif currWord=='een':
    if nextWord!='' and isVowel(get_definition_with_rules(0,[currWord])[0]):
      return 'an'
    else:
      return 'a'
  elif (currWord=='de' or currWord=='het') and len(prevWords)> 0 and prevWords[-1]=='van':
    if len(prevWords) > 1 and prevWords[-2][-4:]=='heid':
      return ''
    else:
      return 'the'
  elif currWord=='iets':
    if nextWord !='' and nextWord[-2:]=='er':
      return 'a little'
    else:
      return 'something'
  else:
    return get_definitions(currWord)[0]

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

def rearrange_modals(tagged_sentence):
  tags = [x[1] for x in tagged_sentence]
  if 'MD' in tags:
    nouns_before, nouns_after = search_for_noun_phrase(tags,tags.index('MD'))
    if (nouns_before and nouns_after) or (not nouns_before and not nouns_after):
      return tagged_sentence
    elif nouns_before and not nouns_after:
      left = get_noun_phrase(tags,-1,tags.index('MD'))
      word = tagged_sentence.pop(tags.index('MD'))
      tagged_sentence.insert(left+1,word)
    elif nouns_after and not nouns_before:
      right = get_noun_phrase(tags,1,tags.index('MD'))
      word = tagged_sentence.pop(tags.index('MD'))
      tagged_sentence.insert(right-1,word)
  return tagged_sentence

def search_for_noun_phrase(tags,start):
  punctuation = [',','.','?']
  pre_punctuation = [(i,punc) for i,punc in enumerate(tags[:start]) if punc in punctuation]
  post_punctuation = [(i+start,punc) for i,punc in enumerate(tags[start:]) if punc in punctuation]
  pre = 0
  post = len(tags) -1
  if pre_punctuation != []:
    pre = pre_punctuation[-1][0]
  if post_punctuation != []:
    post = post_punctuation[0][0]
  nouns_before = 'NN' in tags[pre:start] or 'NNS' in tags[pre:start]
  nouns_after = 'NN' in tags[start:post] or 'NNS' in tags[start:post]
  return (nouns_before,nouns_after)

def get_noun_phrase(tags,direction,start):
  left_tags = ['PRP','NN','NNS','IN','CD']
  right_tags = ['NN','NNS','CD','PRP']
  punctuation = [',','.','?']
  phrase_tags = left_tags if direction == -1 else right_tags
  index = start + direction
  while index >= 0 and index < len(tags) and tags[index] in phrase_tags and tags[index] not in punctuation:
    index += direction
  if index == start + direction:
    return -1
  else:
    return index

def rearrange_modal_verbs(tagged_sentence):
  tags = [x[1] for x in tagged_sentence]
  if 'MD' in tags:
    modal_i = tags.index('MD')
    if tags[modal_i+1] != 'VB' and 'VB' in tags[modal_i:]:
      verb_index = tags[modal_i:].index('VB') + modal_i
      verb = tagged_sentence.pop(verb_index)
      tags.pop(verb_index)
      after_verb = None
      if verb_index < len(tags) and tags[verb_index] in ['JJ','VB']:
        after_verb = tagged_sentence.pop(verb_index)

      if after_verb != None:
        tagged_sentence.insert(modal_i+1,after_verb)
      tagged_sentence.insert(modal_i+1,verb)
  return tagged_sentence

def disamb_become(tagged_sentence):
  words = [x[0] for x in tagged_sentence]
  if ('should','become') in zip(words,words[1:]):
    should_index = zip(words,words[1:]).index(('should','become'))
    tagged_sentence[should_index +1] = ('be','VB')
  return tagged_sentence

#if you don't want to use the cache, use this line:
#text.load('text.txt','dict.txt',True,False)

#otherwise, just do this:
text.load()

#grab the tagged words from the text module
tagged = text.tagged

print "Reordering..."
print tagged
reordered = []
for i,sentence in enumerate(tagged):
  tagged[i] = fix_question(sentence)
  tagged[i] = reorder_subclause(tagged[i])
  tagged[i] = reorder_adverb_verb(tagged[i])
  tagged[i] = disamb_which(tagged[i])
  tagged[i] = rearrange_modals(tagged[i])
  tagged[i] = rearrange_modal_verbs(tagged[i])
  tagged[i] = disamb_become(tagged[i])
  not_tagged = []
  for tup in tagged[i]:
    not_tagged.append(tup[0])
  reordered.append(not_tagged)

print "******* TRANSLATION *******"
print_text(reordered)
