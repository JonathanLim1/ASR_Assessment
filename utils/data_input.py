
# #Use case for ASR model output Text. Text -> Phoneme -> Phoneme comparison 
# import eng_to_ipa as p

# def split(sentence):
#   return [letter for letter in sentence]

# def remove_space(sentence_lst):
#   delete_empty = [ele for ele in sentence_lst if ele.strip()]
#   return delete_empty

# def remove_other(sentence_lst):
#   removed = [x.strip('ˈ') for x in sentence_lst] #remove "ˈ",but remains ""
#   removed = remove_space(removed) #remove ""
#   return removed

# def txt_cleaning(sentence_list):
#   sentence_list = remove_space(sentence_list) #remove space " "
#   sentence_list = remove_other(sentence_list) #remove ""
#   joined = '/'.join(sentence_list)
#   return joined

# #final function
# def txt_to_phonetics(sentence):
#   txt_converted_sentence = p.convert(sentence)
#   return txt_cleaning(split(txt_converted_sentence))


## CONVERTING NIST SPHERE .WAV file to 'useable' file
import librosa
import numpy as np
import scipy.io.wavfile as wf
from sklearn import preprocessing

def load_wav(file_directory):
  ### Function to load wav file as array

  #load file using librosa
  audio, sr = librosa.load(file_directory,sr=16000)

  #scale the values before converting to float
  minmax_scale = preprocessing.MinMaxScaler(feature_range=(-32768, 32767))
  x_scale = minmax_scale.fit_transform(audio.reshape(-1,1))
  x_scale = x_scale.astype(np.int16)

  return x_scale

def convert_wav(file_directory,overwrite = False, print=False):

  ### LOAD NIST/SPHERE .wav file using librosa which outputs audio in datapoints (0-1)
  ### Using MinMaxScaler to convert datapoints to range(-32768-32767) so that values are lost after converting to integers
  ### Using scipy.io.wavfile to write a wav file using the datapoints 
  ### overwrite = True to create new file replacing old one

  #load file using librosa & scale the values before converting to float
  x_scale = load_wav(file_directory)
  sr = 16000

  if overwrite:
    #write/overwrite wav file
    wf.write(file_directory, sr, x_scale)
    if print:
      print(f"{file_directory} file written!")
  else:
    #write/overwrite wav file
    wf.write(file_directory.split('.')[0] + "_NEW.wav", sr, x_scale)
    if print:
      print(f"{file_directory} file written!")
