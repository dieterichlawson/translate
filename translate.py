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

def isVowel(letter):
	letter = letter.lower()
	if letter=='a' or letter='e' or letter='o' or letter == 'u' or letter=='i':
		return True
	else:
		return False

def translate_word(currWord, prevWords, nextWord):
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
		if nextWord!='' and isVowel(translate_word(nextWord)[0]):
			return 'an'
		else
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
		return lookup_in_dict(currWord)
	
load_text('text.txt')
load_dict('dict.txt')

#for sentence in text:
#  print sentence
#for item in dictionary.items():
#  print "%s: %s" % item
