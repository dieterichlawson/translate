#!/usr/bin/env python
from collections import defaultdict
from nltk import tag
import re
import text

tobe_list = ['am','are','is','was','were']
punctuation = [',','.','?']


def print_text(sentences):
  startgorule = re.compile("of start (goes|go)")
  becomerule = re.compile("should become", re.IGNORECASE)

  for s in sentences:
    sentence = ' '.join(s)
    sentence = re.sub('\s,\s',', ',sentence)
    sentence = re.sub('\s\.','.',sentence)
    sentence = re.sub('\s\?','?',sentence)
    sentence = sentence[0].upper() + sentence[1:]
    sentence = re.sub(startgorule, 'starts', sentence) 
    sentence = re.sub(becomerule, "should be", sentence)

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
    for i,tup in enumerate(tagged_sentence):
	if i > 3 and i < len(tagged_sentence)-1 and tagged_sentence[i-1][1]=='CC' and tagged_sentence[i][1][:2]=='VB' and (tagged_sentence[i+1][1] == 'PRP' or tagged_sentence[i+1][1] == 'EX' or tagged_sentence[i+1][1][:2] == 'NN'):
		print "moving later in sentence"
    		verb = result.pop(i)
    		result.insert(i+1,verb)
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


def rewrite_than(tagged_sentence):
	sent_len = len(tagged_sentence)
	result = tagged_sentence
	for i, tup in enumerate(tagged_sentence):
		if i < sent_len-1 and tagged_sentence[i][0]=='than' and tagged_sentence[i+1][1] != 'JJR':
			result[i] = ('then','CC')
	return result
		
def rewrite_something(tagged_sentence):
	sent_len = len(tagged_sentence)
	result = tagged_sentence
	for i, tup in enumerate(tagged_sentence):
		if i < sent_len-1 and tagged_sentence[i][0]=='something' and tagged_sentence[i+1][1] == 'JJR':
			result[i] = ('a little','JJ')
	return result

def disamb_it(tagged_sentence):
  sentence_len = len(tagged_sentence)
  result = tagged_sentence
  for i,tup in enumerate(tagged_sentence):
    if i < sentence_len-1 and tup[0]=='it' and (tagged_sentence[i+1][1][:2] == 'NN' or tagged_sentence[i+1][1][:2] == 'JJ') :
      result[i] = ('the','DT')
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
  left_tags = ['DT','PRP','NN','NNS','IN','CD']
  right_tags = ['NN','NNS','CD','PRP','VBG']
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

def replace_needto(sentence):
  for i, word in enumerate(sentence):
    if word[0] == "need" and i < len(sentence)-2:
      if sentence[i-1][0] == "have" and sentence[i+1][0] == "to":
        sentence = sentence[0:i-1] + sentence[i:i+1] + sentence[i+2:]
        break
  return sentence

def fix_to(sentence):
  for i, word in enumerate(sentence):
    if word[0] == 'to' and i != 0 and  sentence[i-1][0] == 'need':
      if (sentence[i+1][1] == 'NN' or sentence[i+1][1] == 'JJ'):
         sentence[i] = ('for','IN')
  return sentence
vowels = "a|e|o|i|u|A|E|I|O|U"
def change_a_to_an(sentence):
  for i, word in enumerate(sentence):
    if word[0] == 'a' and i < len(sentence) and (sentence[i+1][1] == 'NN' or sentence[i+1][1]) and re.search(vowels, sentence[i+1][0][0]):
      sentence[i] = ('an', 'DT')
  return sentence

def wpronoun_verb_fix(sentence):
  for i, word in enumerate(sentence):
    if word[1] == 'WP' and i < len(sentence) and sentence[i+1][1] == 'VBP':# and : #if WP word followed by Verb present tense ie. "Who care", add s to verb.
      sentence[i+1] = (sentence[i+1][0]+'s', 'VBP') # change tag to plural?
  return sentence

def fix_seen(sentence):
  words = [x[0] for x in sentence]
  if (',','seen') not in zip(words,words[1:]): return sentence
  tags = [x[1] for x in sentence]
  seen_index = zip(words,words[1:]).index((',','seen')) + 1
  found_verb = False
  for i in range(seen_index+1,len(tags)):
    if words[i] in punctuation: break
    if tags[i][0:2] == 'VB':
      found_verb = True
      break
  sentence.pop(seen_index)
  if not found_verb:
    sentence.insert(seen_index,('of','IN'))
  sentence.insert(seen_index,('because','IN'))
  return sentence

def drop_modal_infinitive(sentence):
  words = [x[0] for x in sentence]
  if 'should' not in words: return sentence
  tags = [x[1] for x in sentence]
  should_index = words.index('should')
  if ('TO','VB') in zip(tags[should_index+1:],tags[should_index+2:]):
    to_index = zip(tags[should_index+1:],tags[should_index+2:]).index(('TO','VB'))
    print 'TO INDEX: %d' % to_index
    sentence.pop(to_index+ should_index + 1)
  return sentence

#if you don't want to use the cache, use this line:
#text.load('text.txt','dict.txt',True,False)

#otherwise, just do this:
text.load()

#grab the tagged words from the text module
tagged = text.tagged
print tagged
print_text(text.translated)
print "Reordering..."
reordered = []
for i,sentence in enumerate(tagged):
  tagged[i] = drop_modal_infinitive(tagged[i])
  tagged[i] = fix_question(sentence)
  tagged[i] = reorder_subclause(tagged[i])
  tagged[i] = reorder_adverb_verb(tagged[i])
  tagged[i] = disamb_which(tagged[i])
  tagged[i] = disamb_it(tagged[i])
  tagged[i] = rewrite_than(tagged[i])
  tagged[i] = rewrite_something(tagged[i])
  tagged[i] = rearrange_modals(tagged[i])
  tagged[i] = rearrange_modal_verbs(tagged[i])
  tagged[i] = replace_needto(tagged[i])
  #tagged[i] = fix_to(tagged[i]) This rule may not be needed because of the "fix_needto" rule -wlc
  tagged[i] = change_a_to_an(tagged[i])
  #tagged[i] = wpronoun_verb_fix(tagged[i])
  tagged[i] = fix_seen(tagged[i])
  not_tagged = []
  for tup in tagged[i]:
    not_tagged.append(tup[0])
  reordered.append(not_tagged)

print "******* TRANSLATION *******"
print_text(reordered)
