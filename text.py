from collections import defaultdict
from nltk import tag
import re
import os.path

dictionary = defaultdict(list)
text = []
translated = []
tagged = []
translated_file = 'cached_translation'
tagged_file = 'cached_tagged'

tagger = tag.StanfordTagger('stanford-tagger/models/english-bidirectional-distsim.tagger','stanford-tagger/stanford-postagger.jar')
pronouns = ['ik','jij','u','hij','zij','wij','jullie','gij','ge','we']

def load(textfile = "text.txt", dictfile='dict.txt', with_rules=True,use_cache=True):
  load_text(textfile)
  load_dict(dictfile)
  cache_exists = os.path.isfile(translated_file)
  cache_exists = cache_exists and os.path.isfile(tagged_file)
  if not use_cache or not cache_exists:
    translate(with_rules)
    tag()
    clear_cache()
    write_cache()
  else:
    load_cache()

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

def load_cache():
  in_translated = open(translated_file)
  for line in in_translated:
    line = line.strip()
    translated.append(line.split('|'))
  in_translated.close()
  in_tagged = open(tagged_file)
  for line in in_tagged:
    taglist = []
    for pair in line.split('|'):
      taglist.append((pair.split('_')[0],pair.split('_')[1]))
    tagged.append(taglist)
  in_tagged.close()

def write_cache():
  outfile = open(translated_file,'w')
  for sentence in translated:
    outfile.write('|'.join(sentence))
    outfile.write('\n')
  outfile.close()
  outfile = open(tagged_file,'w')
  for sentence in tagged:
    outlist = []
    for word, pos in sentence:
      outword = word + '_' + pos
      outlist.append(outword)
    outfile.write('|'.join(outlist))
  outfile.close()

def clear_cache():
  if os.path.isfile(tagged_file):
    os.remove(tagged_file)
  if os.path.isfile(translated_file):
    os.remove(translated_file)

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

def translate(with_rules):
  punctuation = '.,?'
  for sentence in text:
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

def tag():
  for i,sentence in enumerate(translated):
    tagged.append(tagger.tag(sentence))
    print "Tagged sentence %d of %d" % (i +1,len(translated))
