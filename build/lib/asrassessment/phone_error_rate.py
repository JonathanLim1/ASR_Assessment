
#global imports 
import pandas as pd
import numpy as np
import os

import difflib
from tqdm import tqdm
import copy

import librosa
from sklearn import preprocessing
import scipy.io.wavfile as wf
from pydub import AudioSegment

#local imports 
from data_input import convert_wav
from standardizer import read_phn,TIMIT_to_IPA, IPA_to_TIMIT,file_text
from noise_sidefunc import load_params,segmental_snr_mixer


#Function to give a overview of the phoneme error rate 
def error_rate(timit, asr,phn = True):
  if phn:
    r = timit.split('/')
    h = asr.split('/')
  else:
    r = timit.split()
    h = asr.split()

  #costs will holds the costs, like in the Levenshtein distance algorithm
  costs = [[0 for inner in range(len(h)+1)] for outer in range(len(r)+1)]

  # backtrace will hold the operations we've done.
  # so we could later backtrace, like the WER algorithm requires us to.
  backtrace = [[0 for inner in range(len(h)+1)] for outer in range(len(r)+1)]
  

  OP_OK = 0
  OP_SUB = 1
  OP_INS = 2
  OP_DEL = 3
  # First column represents the case where we achieve zero
  # hypothesis words by deleting all reference words.
  for i in range(1, len(r)+1):
      costs[i][0] = 1*i
      backtrace[i][0] = OP_DEL

  # First row represents the case where we achieve the hypothesis
  # by inserting all hypothesis words into a zero-length reference.
  for j in range(1, len(h) + 1):
      costs[0][j] = 1 * j
      backtrace[0][j] = OP_INS

  # computation
  for i in range(1, len(r)+1):
    for j in range(1, len(h)+1):
      if r[i-1] == h[j-1]:
        costs[i][j] = costs[i-1][j-1]
        backtrace[i][j] = OP_OK
      else:
        substitutionCost = costs[i-1][j-1] + 1 # penalty is always 1
        insertionCost = costs[i][j-1]      + 1 # penalty is always 1
        deletionCost= costs[i-1][j]        + 1 # penalty is always 1
              
        costs[i][j] = min(substitutionCost, insertionCost, deletionCost)
        if costs[i][j] == substitutionCost:
          backtrace[i][j] = OP_SUB
        elif costs[i][j] == insertionCost:
          backtrace[i][j] = OP_INS
        else:
          backtrace[i][j] = OP_DEL

  # back trace though the best route:
  i = len(r)
  j = len(h)
  numSub = 0
  numDel = 0
  numIns = 0
  numCor = 0

  #new df to track where an error was made
  tracker_df = pd.DataFrame({'phoneme':r,'error':['NIL' for i in range(len(r))],'substituted':['NIL' for i in range(len(r))]})
  
  while i > 0 or j > 0:
    if backtrace[i][j] == OP_OK:
      numCor += 1
      i-=1
      j-=1
    elif backtrace[i][j] == OP_SUB:
      # edit df
      tracker_df.at[i-1,"error"] = "Substitution"
      tracker_df.at[i-1,'substituted'] = h[j-1]
      # print(f"There was a substitution of {h[j-1]} for {r[i-1]} between {r[i-2]} and {r[i]}.")
      numSub +=1
      i-=1
      j-=1
    elif backtrace[i][j] == OP_INS:
      numIns += 1
      # try:
      #   print(f"There was an insertion of {h[j-1]} between {r[i-1]} and {r[i]}.")
      # except: 
      #   print(f"There was an insertion of {h[j-1]} after {r[i-1]}")
      j-=1
    elif backtrace[i][j] == OP_DEL:
      numDel += 1
      # edit df
      tracker_df.at[i-1,"error"] = "Deletion"
      # try:
      #   print(f"There was a deletion     of {r[i-1]} between {r[i-2]} and {r[i]}.")
      # except:
      #   print(f"There was a deletion     of {r[i-1]} after {r[i-2]}")
      i-=1
  per_result = round( (numSub + numDel + numIns) / (float) (len(r)), 3)
  return {'PER':per_result, 'Correct':numCor, 'Substitution':numSub, 'Insertion':numIns, 'Deletion':numDel}, tracker_df

#Function to give exact number of times wrongly and correctly predicted phonemes  
def sequence_match(TIMIT_phoneme, ASR_phoneme):

  ### <Purpose of function>: To get number of correctly and wrongly predicted phonemes according to each phoneme 
  ### <Input variables>:     TIMIT_phoneme and ASR_phoneme (strings), Example:"a/d/b/a/e"
  ### <Output variable>:     Returns Dictionary with phoneme as key and list containing [num of correct, num of wrong] as value

  timit = TIMIT_phoneme.split("/")
  asr = ASR_phoneme.split("/")
  
  #initiate sequence matcher
  seq_matcher = difflib.SequenceMatcher(None,timit,asr) 
  
  #initiate dictionary 
  phoneme_counter_dict = {} 

  for tag,i1,i2,j1,j2 in seq_matcher.get_opcodes():

    #Counting number of correctedly predicted phoneme
    if tag == "equal":
      for letter in timit[i1:i2]: # dealing with list of multiple correct phonemes
        if letter in phoneme_counter_dict: #create dictionary counter
          phoneme_counter_dict[letter][0] += 1
        else:
          phoneme_counter_dict[letter] = [1,0]
    
    #Counting number of wrongly predicted phoneme       
    if tag =='replace' or tag=='delete':
      for letter in timit[i1:i2]:
        if letter not in phoneme_counter_dict:  #for phonemes not in previously counted
          phoneme_counter_dict[letter] = [0,1]
        else:                                   #for phoneme with previously counted wrong
          phoneme_counter_dict[letter][1] += 1

  #Remove unwanted strings '' and '/'
  try:
    phoneme_counter_dict.pop('')
  except:
    pass
  try:
    phoneme_counter_dict.pop('/')
  except:
    pass

  return phoneme_counter_dict

#Using ASR model, convert .wav file into phn and iteratively replace the phn file of asr_dict
def load_asr_dict(TIMIT_dict,asr_model, file_set = "TRAIN",DR = [0,7],noise_file = False):
  ### <Purpose of function>: Using ASR model, convert .wav file into phn and iteratively replace the phn file of asr_dict
  ### <Input variables>:     TIMIT_dict = prior to this function, load the timit_file into a dictionary using the timit_load function in timit_load.py
  ###                        asr_model = function of ASR model, 
  ###                        file_set = "TRAIN" / "TEST"
  ###                        DR = choose the range of DR files want to use for TESTING/TRAINING
  ### <Output variable>:     Returns dictionary containing list of phoneme in same manner as in TIMIT_dict, just without
  ###                        .wav, .txt, .wrd files
  
  #create deepcopy of dictionary
  asr_dict = copy.deepcopy(TIMIT_dict)
  for DR in list(asr_dict[file_set].keys())[DR[0]:DR[1]+1]:
    for speaker in tqdm(asr_dict[file_set][DR].keys()):
      timit_wav_list = asr_dict[file_set][DR][speaker]["wav"]

      ASR_phoneme_lst = []
      for file_dir in timit_wav_list:
        convert_wav(file_dir,overwrite = True)
        ASR_phoneme = asr_model(file_dir) ### insert model function here
        ASR_phoneme_lst.append(ASR_phoneme)
      
      #replace file_dir with phonemes
      asr_dict[file_set][DR][speaker]["phn"] = ASR_phoneme_lst

      #remove unnecessary file types
      file_types = ['txt', 'wrd', 'wav']
      for file_type in file_types:
        asr_dict[file_set][DR][speaker].pop(file_type)
      
  return asr_dict

#To compare the phoneme strings of TEST/TRAIN set of TIMIT and output a list of datapoints       
def compare_phonemes_perc(TIMIT_dict,asr_dict,file_set = "TRAIN",DR = [0,None]):

  ### <Purpose of function>: To compare the phoneme strings of TEST/TRAIN set of TIMIT and output a list of datapoints 
  ###                        (percentage correct for each recording) of each phoneme.
  ### <Input Variables>:     
  ###                        TIMIT_dict = prior to this function, load the timit_file into a dictionary using the timit_load function in timit_load.py
  ###                        asr_dict = dictionary containing phonemes output from ASR model with the same directory as TIMIT
  ###                        file_set = "TEST" or "TRAIN"
  ### <Output>:              Returns Dictionary containing phoneme as key and list of % correctly predicted phonemes as value.


  ##compare asr vs timit phonemes 
  phn_counter_dict = {
              # "Vowels (Monophthongs)"
              "iy":[], "eh":[], "ey":[], "ae":[], "aa":[], "ao":[], "uh":[], "uw":[], "ah":[], "ax":[],"ow":[],
              
              # "Vowels (Diphthongs)"
              "oy":[],"ay":[],"aw":[],

              # "Consonants (Fricatives)"
              "f":[],"th":[],"s":[],"sh":[],"h":[],"v":[],"dh":[],"z":[],"zh":[],

              # "Consonants (Plosives)"
              "p":[],"t":[],"k":[],"b":[],"d":[],"g":[],
              
              # "Consonants"
              "ch":[],"jh":[],

              # "Approximants"
              "w":[],"r":[],"j":[],
              
              # "Nasals"
              "m":[],"n":[],"ŋ":[],
              
              # "Lateral Approximant"
              "l":[],
              
              # "Misc"
              "ih":[],"ux":[],"er":[],"ix":[],"axr":[],"ax-h":[],"dx":[],"en":[],"em":[],"y":[],"hh":[],"el":[],"eng":[],"hv":[]
  }

  #setting train or test set
  for DR_index in list(TIMIT_dict[file_set].keys())[DR[0]:DR[1]]:
    for speaker in tqdm(TIMIT_dict[file_set][DR_index].keys()):
      
      #Get list of TIMIT phoneme directory specific to the speaker/DR/train-test
      timit_phn_dir_list = sorted(TIMIT_dict[file_set][DR_index][speaker]['phn'])

      #Create list to store the phonemes
      TIMIT_phoneme_lst = []

      #Read through phonemes to store in TIMIT_phoneme_lst
      for file_dir in timit_phn_dir_list:
        TIMIT_phoneme = read_phn(filename = file_dir,string = True)
        TIMIT_phoneme_lst.append(TIMIT_phoneme)

      #get phoneme from ASR model
      asr_phn_dir_list = sorted(asr_dict[file_set][DR_index][speaker]['phn'])

      #convert to standardized phoneme
      TIMIT_phoneme_lst_c = []
      for phn in TIMIT_phoneme_lst:
        timit_phn = TIMIT_to_IPA(phn)
        TIMIT_phoneme_lst_c.append(timit_phn)

      ASR_phoneme_lst_c = []
      for phn in asr_phn_dir_list:
        asr_phn = IPA_to_TIMIT(phn)
        ASR_phoneme_lst_c.append(asr_phn)

      if len(TIMIT_phoneme_lst_c) == len(ASR_phoneme_lst_c):
        for i in range(len(TIMIT_phoneme_lst_c)):
          x = sequence_match(TIMIT_phoneme_lst_c[i],ASR_phoneme_lst_c[i])
          
          for key in x.keys():
            percentage_correct = x[key][0]/(x[key][0]+x[key][1])*100

            if key in phn_counter_dict:
              phn_counter_dict[key].append(percentage_correct)
            else:
              phn_counter_dict[key] = [percentage_correct]

  return phn_counter_dict



#ADD NOISE
def add_noise(audio_dir,noise_dir, cfg_filedir,louder=0,softer=0):
      ### <Purpose of Function>: Add noise (optional varying volumes) to audio
  ### <Variable>           : audio_dir = timit.wav file
  ###                        noise_dir = noise.wav file 
  ###                        cfg_filedir = cfg file used for setting params
  ###                        louder = integer input to increase volume of noise
  ### <Output>             : new audio file with noise exported same file directory as audio_dir with new label         

  #Load params
  params = load_params(cfg_filedir)


  #Load audio and noise
  clean = librosa.load(audio_dir,16000)
  clean = clean[0]
  noise = librosa.load(noise_dir,16000)
  noise = noise[0]

  ##Mix noisy audio with clean audio
  clean, noisenewlevel, noisyspeech, noisy_rms_level = segmental_snr_mixer(params = params, 
                                                                          clean = clean,
                                                                          noise = noise,
                                                                          snr = softer-louder)
  
  ##Scale the values before converting to float
  minmax_scale = preprocessing.MinMaxScaler(feature_range=(-32768, 32767))

  #for clean
  clean_scaled = minmax_scale.fit_transform(clean.reshape(-1,1))
  clean_scaled = clean_scaled.astype(np.int16)

  #for noisy
  noisy_scaled = minmax_scale.fit_transform(noisyspeech.reshape(-1,1))
  noisy_scaled = noisy_scaled.astype(np.int16)

  #export file
  if softer-louder > 0:
    wf.write(f"{audio_dir.split('.wav')[0]}_noise_softer{softer}dB.wav", 16000, noisy_scaled)
  else:
    wf.write(f"{audio_dir.split('.wav')[0]}_noise_louder{softer}dB.wav", 16000, noisy_scaled)

def compare_phn_wrd_noise(timit_wav,
                          timit_phn, 
                          timit_txt,
                          noise_wav,
                          asr_phn_model, 
                          asr_txt_model,
                          louder_volumes=[],
                          softer_volumes=[]):
  
  ### <Purpose of Function> : Compare Phoneme Error Rate of ASR model after adding varying levels of noise, 
  ###                         and comparing with the Word Error Rate of the ASR model after adding varying levels of noise
  ### <Input Variables>     : timit_wav             = directory for timit.wav
  ###                         timit_phn             = directory for timit.phn
  ###                         timit_txt             = directory for timit.txt
  ###                         noise_wav             = directory for noise audio
  ###                         asr_phn_model         = function for ASR model which generates phonemes
  ###                         asr_txt_model         = function for ASR model which generates words
  ###                         louder/softer volumes = list of integers which will increase or decrease volume 
  ###                                                 (ONLY choose either louder or softer)
  ### <Output>              : dataframe showing columns (Volume, Error Rate, Type of Error (i.e WER/PER))

  #ASR model phn and txt output
  convert_wav(timit_wav,overwrite=True)
  asr_phoneme = asr_phn_model(timit_wav) #asr model phn
  asr_phoneme = IPA_to_TIMIT(asr_phoneme)
  asr_txt = asr_txt_model(timit_wav) #txt model phn

  #Phoneme Error Rate w/o noise
  timit_phoneme = read_phn(timit_phn,string=True)
  timit_phoneme = TIMIT_to_IPA(timit_phoneme)
  initial_per = error_rate(timit_phoneme,asr_phoneme)

  #Word Error Rate w/o noise
  timit_text = file_text(timit_txt)[8:-1]
  initial_wer = error_rate(timit_text,asr_txt,phn=False)

  output_lst = [["Initial",initial_per['PER'],"PER"],["Initial",initial_wer["PER"],"WER"]]

  if len(louder_volumes) != 0 :
    for vol in louder_volumes:
      add_noise(timit_wav,noise_wav,louder=vol) #add increasing noise & create new audio.wav
      louder_path_dir = f"{timit_wav.split('.wav')[0]}_noise_louder{vol}dB.wav"

      #Phoneme ASR Model
      asr_phoneme_noise = asr_phn_model(louder_path_dir)
      asr_phoneme_noise = IPA_to_TIMIT(asr_phoneme_noise)
      noise_per = error_rate(timit_phoneme,asr_phoneme_noise)
      output_lst.append([f"+{vol}",noise_per['PER'],"PER"])

      #Word ASR Model
      asr_txt_noise = asr_txt_model(louder_path_dir)
      noise_wer = error_rate(timit_text,asr_txt_noise,phn=False)
      output_lst.append([f"+{vol}",noise_wer['PER'],"WER"])

      #remove audio.wav
      os.remove(louder_path_dir)
  else:
    for vol in softer_volumes:
      add_noise(timit_wav,noise_wav,softer=vol) #add decreasing noise & create new audio.wav
      softer_path_dir = f"{timit_wav.split('.wav')[0]}_noise_softer{vol}dB.wav"

      #Phoneme ASR Model     
      asr_phoneme_noise = asr_phn_model(softer_path_dir)
      asr_phoneme_noise = IPA_to_TIMIT(asr_phoneme_noise)
      noise_per = error_rate(timit_phoneme,asr_phoneme_noise)
      output_lst.append([f"-{vol}",noise_per['PER'],"PER"])

      #Word ASR Model
      asr_txt_noise = asr_txt_model(softer_path_dir)
      noise_wer = error_rate(timit_text,asr_txt_noise,phn=False)
      output_lst.append([f"-{vol}",noise_wer['PER'],"WER"])
      
      #remove audio.wav
      os.remove(softer_path_dir)

  #Convert into dataframe
  df = pd.DataFrame(output_lst)
  error_rate_df = df.rename(columns = {0:"Volume", 1:"Error Rate (%)", 2:"Type of Error"})

  return error_rate_df

def compare_phn_wrd_noise_multi(audio_dict,
                                noise_wav,
                                asr_phn_model,
                                asr_txt_model,
                                DR = [0,None],
                                SPK = [0,None],
                                louder_volumes=[],
                                softer_volumes=[]):
  ### <Purpose of Function> : same function as compare_phn_wrd_noise but for multiple files
  ### <Input Variables>     : audio-dict            = TIMIT["TRAIN"] or TIMIT["TEST"] file
  ###                         noise_wav             = noise audio file
  ###                         asr_phn_model         = function for ASR model which generates phonemes
  ###                         asr_txt_model         = function for ASR model which generates words
  ###                         DR                    = list of range of DR selected
  ###                         SPK                   = range of speakers within DR selected 
  ###                         louder/softer volumes = list of integers which will increase or decrease volume 
  ###                                                 (ONLY choose either louder or softer)
  ### <Output>              : dataframe showing columns (Volume, Error Rate, Type of Error (i.e WER/PER)) 
  ###                         for multiple timit wav files


  #file types 
  type_lst = ['wav','phn','txt']
  
  #initiat df
  error_rate_df = pd.DataFrame({"Volume": [], "Error Rate (%)":[],"Type of Error":[]})

  for DR_index in list(audio_dict.keys())[DR[0]:DR[1]]:
    for speaker in tqdm(list(audio_dict[DR_index].keys())[SPK[0]:SPK[1]]):
      for i in range(len(audio_dict[DR_index][speaker]['wav'])):
        compare_df = compare_phn_wrd_noise(timit_wav = audio_dict[DR_index][speaker]['wav'][i] ,
                                           timit_phn = audio_dict[DR_index][speaker]['phn'][i], 
                                           timit_txt = audio_dict[DR_index][speaker]['txt'][i],
                                           noise_wav = noise_wav,
                                           asr_phn_model = asr_phn_model, 
                                           asr_txt_model = asr_txt_model,
                                           louder_volumes= louder_volumes,
                                           softer_volumes= softer_volumes)
        error_rate_df = error_rate_df.append(compare_df)

  return error_rate_df

# ## Initial add_noise function
def initial_add_noise(audio_dir,noise_dir,louder=0,softer=0):
  ### <Purpose of Function>: Add noise (optional varying volumes) to audio
  ### <Variable>           : audio_dir = timit.wav file
  ###                        noise_dir = noise.wav file 
  ###                        louder = integer input to increase volume of noise
  ### <Output>             : new audio file with noise exported same file directory as audio_dir with new label         

  sound1 = AudioSegment.from_file(audio_dir, format="wav")
  sound2 = AudioSegment.from_file(noise_dir, format="wav")

  # sound1 dB louder
  new_noise = sound2 + louder - softer

  # Overlay sound2 over sound1 at position 0 
  overlay = sound1.overlay(new_noise, position=0)

  # simple export
  if louder == 0:
    file_handle = overlay.export(f"{audio_dir.split('.wav')[0]}_noise_softer{softer}dB.wav", format="wav")
  if softer == 0:
    file_handle = overlay.export(f"{audio_dir.split('.wav')[0]}_noise_louder{louder}dB.wav", format="wav")