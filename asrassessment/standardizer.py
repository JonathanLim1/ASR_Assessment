#TIMIT to IPA mapping

#source of phoneme categorisation:
# 1. https://thesoundofenglish.org/ipa/
# 2. https://savioingles.blogspot.com/2016/02/phonetic-symbols.html

#local import from generalfunc
from generalfunc import split_string

#global import
import pandas as pd

comapping = {
            "Vowels (Monophthongs)":
            ["iy", "eh", "ey", "ae", "aa", "ao", "uh", "uw", "ah", "ax","ow"],
             
            "Vowels (Diphthongs)":
            ["oy","ay","aw"],

            "Consonants (Fricatives)":
            ["f","th","s","sh","h","v","dh","z","zh"],

            "Consonants (Plosives)":
            ["p","t","k","b","d","g"],
             
            "Consonants":
            ["ch","jh"],

            "Approximants":
            ["w","r","j"],
             
            "Nasals":
            ["m","n","ŋ"],
             
            "Lateral Approximant":
            ["l"],
             
            "Misc": 
            ["ih","ux","er","ix","axr","ax-h","dx","en","em", "y", "hh", "el", "eng", "hv"]
}

IPA_to_TIMIT_mapping = {
    "ɪ":"iy", "i":"iy", 
    "I":"ih", #check during testing if this exist
    "ɛ":"eh", 
    "e":"ey",
    "æ":"ae",
    "ɑ":"aa",
    "aʊ":"aw","aU":"aw","aw":"aw",
    "aɪ":"ay","ay":"ay",
    "ʌ":"ah",
    "ɔ":"ao",
    "ɔɪ":"oy","ɔy":"oy",
    "o":"ow",
    "ʊ":"uh",
    "u":"uw",
    "ʉ":"ux",
    "ɝ":"er",
    "ə":"ax",
    "ɨ":"ix",
    "ɚ":"axr",
    "ə̥":"ax-h", 
    "dʒ":"jh",
    "tʃ":"ch",
    "b":"b",
    "d":"d",
    "ɡ":"g",
    "p":"p",
    "t":"t",
    "k":"k",
    "ɾ":"dx",
    "s":"s",
    "ʃ":"sh","š":"sh",
    "z":"z",
    "ʒ":"zh","ž":"zh",
    "f":"f",
    "θ":"th",
    "v":"v",
    "ð":"dh",
    "m":"m",
    "n":"n",
    "m̩":"em",
    "n̩":"en",
    "l":"l",
    "ɹ":"r",
    "w":"w",
    "y":"y",
    "h":"hh",
    "l̩":"el",
    "ŋ̍":"eng",
    "ɦ":"hv"
}

TIMIT_to_IPA_mapping ={
    "ng":"ŋ","nx":"ŋ",
    "en":"n","em":"m",
    "h#":"","bcl":"b","dcl":"d",
    "gcl":"g","pcl":"p",
    "tcl":"t","kcl":"k",
    "vi":"v", #not in TIMIT 61 phoneset 
}

#for ASR model phoneme to a standardized phoneme comparison
def IPA_to_TIMIT(ipa_list,split = True):
  
  #### INPUT VALUE IS LIST OF INDIVIDUAL PHONEME STRINGS ####
  
  if split:
    ipa_list = split_string(ipa_list)

  converted_list = []
  for IPA_letter in ipa_list:
    loop_count= 0
    for key,value in IPA_to_TIMIT_mapping.items():
      if IPA_letter == key:
        converted_list.append(value)
      else:
        loop_count += 1
      if loop_count == len(IPA_to_TIMIT_mapping.keys()):
        converted_list.append(IPA_letter)
  return '/'.join(converted_list)

#for TIMIT phoneme to a standardized phoneme comparison
def TIMIT_to_IPA(timit_list,split = True):

  #### INPUT VALUE IS LIST OF INDIVIDUAL PHONEME STRINGS ####
  if split:
    timit_list = split_string(timit_list)

  converted_list = []
  for TIMIT_letter in timit_list:
    loop_count= 0
    for key,value in TIMIT_to_IPA_mapping.items():
      if TIMIT_letter == key:
        converted_list.append(value)
      else:
        loop_count += 1
      if loop_count == len(TIMIT_to_IPA_mapping.keys()):
        converted_list.append(TIMIT_letter)
  return '/'.join(converted_list)

##loading file PHN/CSV into df
def read_phn(filename,df=False,string=False):
  phn_df = pd.read_csv(filename, names=['header'])
  phn_df = phn_df.header.str.split(pat=' ',expand=True)
  phn_df.columns = ['start','end','phoneme']
  
  #convert to string
  phn_string = '/'.join(phn_df['phoneme'].tolist())
  
  if string == True:
    return phn_string
  if df == True:
    return phn_df

#function to read text given file input
def file_text(file):
  with open(file) as f:
      contents = f.read()
      return contents