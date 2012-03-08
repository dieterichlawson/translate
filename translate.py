#!/usr/bin/env python
from collections import defaultdict
from nltk import tag
import re

dictionary = defaultdict(list)
text = []
tagger = tag.StanfordTagger('stanford-tagger/models/english-bidirectional-distsim.tagger','stanford-tagger/stanford-postagger.jar')
pronouns = ['ik','jij','u','hij','zij','wij','jullie','gij','ge','we']

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
   if index > 0 and is_personal_pronoun(sentence[index-1]):
      return 'v'
   return None

def isVowel(letter):
  vowels = 'aeiou'
  return letter.lower() in vowels

def is_personal_pronoun(word):
  return word in pronouns

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

def translate(source,dictionary,with_rules):
  punctuation = '.,?'
  translated = []
  for sentence in source:
    trans_sentence = []
    for i,word in enumerate(sentence):
      trans_word = ''
      if len(word) == 1 and word in punctuation:
        trans_sentence.append(word)
        continue
      pos = get_pos(word,i,sentence)
      if pos != None: # if we know the POS, pick the best definition
        trans_word = get_definitions(word,pos)[0]
      elif with_rules: # If we're using our special translation rules
        trans_word = get_definition_with_rules(i,sentence)
      else: #we're just doing plain definition grabbing
        trans_word = get_definitions(word)[0]
      trans_sentence.append(trans_word)
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

def reorder_subclause(tagged_sentence):
	in_subclause = False
	prev_is_noun_or_verb = False
	subject_index = -1
	verb_index = -1
	for index,tup in enumerate(tagged_sentence):
		if prev_is_noun_or_verb and tup[1] == 'IN':
			in_subclause = True
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
	else:
		return tagged_sentence	
		
		
def tag_sentences(sentences):
  tagged = []
  for i,sentence in enumerate(sentences):
    tagged.append(tagger.tag(sentence))
    print "Tagged sentence %d of %d" % (i+1,len(sentences))
  return tagged

print "Loading source text..."
load_text('text.txt')

print "Loading dictionary..."
load_dict('dict.txt')

print "Doing first translation pass."
translated = translate(text,dictionary,True)
print_text(translated)

print "Tagging..."
tagged = tag_sentences(translated)

for sentence in tagged:
  	#print sentence
	uselessVariable = 0

print "Reordering..."
for sentence in tagged:
	reordered_sentence = reorder_subclause(sentence)
	print "new sentence:"
	res = ""
	for tup in reordered_sentence:
		res += tup[0].rstrip('\n') + " "
	print res


#print_text(translated)
