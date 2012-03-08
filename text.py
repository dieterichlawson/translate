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
  print "Loading text..."
  load_text(textfile)
  print "Loading dictionary..."
  load_dict(dictfile)
  cache_exists = os.path.isfile(translated_file)
  cache_exists = cache_exists and os.path.isfile(tagged_file)
  if not use_cache or not cache_exists:
    print "Doing first translation pass..."
    translate(with_rules)
    print "Tagging..."
    tag()
    clear_cache()
    write_cache()
  else:
    print "Loading translation and tagged words from cache..."
    load_cache()

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
      taglist.append((pair.split('_')[0],pair.split('_')[1].strip()))
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
    outfile.write('\n')
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
      else: #we're just doing plain definition grabbing
        trans_word = get_definitions(word)[0]
      trans_sentence.append(trans_word)
    translated.append(trans_sentence)

def tag():
  for i,sentence in enumerate(translated):
    tagged.append(tagger.tag(sentence))
    print "Tagged sentence %d of %d" % (i +1,len(translated))
