Author: Jonathan Lim Wei Siang 

Email: Jonathanlimws@gmail.com 

# Automatic Speech Recognition (ASR) Assessment
This Python package allows you to assess the phonetic error rate and visualise them.

## Table of contents
* [Installation](#installation)
* [Brief Overview](#brief-overview)
* [Usage of Package](#usage-of-package)
* [Further Description](#further-description)
* [Package Requirements](#package-requirements)

## Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install asrassessment.

For the latest version check [the PyPI page](https://pypi.org/project/asrassessment/).

```bash
pip install asrassessment
```

**Take Note:**
1. When installing the latest version, there may be an error. Try pip installing a second time to allow the pip install to work.
2. In jupyter notebook and google colab, use '%pip install' instead of '!pip install'.
3. File direcotry names might differ in capitalisaton styles, so take note when writing code. i.e. "TRAIN' instead of "train"

# Brief Overview

**Calculations**
1. Calculate the phoneme error rate (%) using the TIMIT database
2. Identify specific frames for which there was an error in the phoneme conversion 

**Plots**
1. Boxplot of accuracy rate for each phoneme across selected TIMIT files 
2. Stacked boxplot of accuracy rate across varying added noise 
3. Time/frequency Plot any given TIMIT audio showing the timing/phoneme which was incorrected predicted (substitution and deletion only)

### Package Directory

Directory to find some key functions.

- **Main.py**
  Functions:
  - phn_boxplot
  - noise_stacked_boxplot
  - full_phn_boxplot
  - full_noise_stackedplot
  - phoneme_wavchart

- **utils.py**
  - **data_input.py** 
    - convert_wav
  - **standardizer.py**
    - IPA_to_TIMIT
    - TIMIT_to_IPA
    - read_phn
  - **phone_error_rate.py**
    - error_rate


# Usage of package
## Calculating Phoneme Error Rate(%)

ASR Model: Here we use [allosuarus](https://github.com/xinjli/allosaurus) which is defined [below](#allosaurus-model).
```python

#imports
import os 
import pandas as pd

from asrassessment.utils.timit_load import TIMIT_file 

#Load TIMIT Files
timit_dir = f"{os.getcwd()}/{TIMIT_PACKAGE_NAME}" #note this is the folder containing the 'test' & 'train' folders. Usually they are named 'TIMIT'/'timit'
TIMIT_dict = TIMIT_file(timit_dir)

#Take sample phoneme string from TIMIT file 
phn_file_dir = TIMIT_dict['train']['dr1']['fecd0']['phn'][0]

#Load ASR Model
...

#Calculate Phoneneme Error Rate btw. 2 strings

from asrassessment.utils.data_input import convert_wav
from asrassessment.utils.generalfunc import *
from asrassessment.utils.standardizer import *

#file directory
wav_file_dir = TIMIT_dict['train']['dr1']['fecd0']['wav'][0]

#convert and overwrite wav file so it is useable 
convert_wav(file_dir,overwrite=True)

#test model 
asr_phn = allosaurus_model(file_dir)

#standardize phoneme string
asr_phn_conv = IPA_to_TIMIT(asr_phn)

#load TIMIT phn
timit_phn = read_phn(phn_file_dir,string=True)

#standardize phoneme string 
timit_phn_conv = TIMIT_to_IPA(timit_phn)

from asrassessment.utils.phone_error_rate import error_rate

output, error_df = error_rate(timit_phn_conv,asr_phn_conv)

#Final dataframe showing phoneme comparison & type of error
print(output)
print(error_df)
```

## Ploting boxplot for phoneme accuracy of ASR model across selected TIMIT files
Having defined the ASR model prior to this, simply put the function name as a variable. 

Then choose which range of DR files to use within TIMIT and "TRAIN"/"TEST". [Take note of point 3 in Installation](#installation)

```python
from asrassessment import main as asrtest

#plot 
asrtest.full_phn_boxplot(asr_model=allosaurus_model,file_set="TRAIN", DR=[0,1])
```
![boxplot](https://github.com/JonathanLim1/ASR_Assessment/blob/master/images/boxplot.png?raw=true)

## Ploting stacked boxplot for phoneme accuracy of ASR model across varying added noise

Note that adding noise function here requires a 'noisyspeech.cfg' file. 

Noise file should be in wav file and you can find such an example download [here](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwi4rsb6r8n5AhXhBbcAHeqQCn8QFnoECAUQAQ&url=https%3A%2F%2Fwww.audiocheck.net%2Ftesttones_whitenoise.php&usg=AOvVaw2Qg1PzG1unVXJIfPaPcc3a)

ASR_Model
Here we use the [allosaurus model](#allosaurus-model)

Speech-to-text Model
Here we use the [google speech-to-text](#speech-recognition-model-google)

```python
#Load ASR model
...

#Load Speech to Text Model 
...

#import 
from asrassessment import main as asrtest

#plot
asrtest.full_noise_stackedplot(audio_dict=TIMIT_dict['train'],
                               noise_wav="audiocheck.net_whitenoisegaussian.wav",
                               cfg_filedir= 'noisyspeech.cfg',
                               asr_phn_model=allosaurus_model,
                               asr_txt_model=speech_recog,
                               DR = [0,1],
                               SPK = [0,1],
                               louder_volumes=[],
                               softer_volumes=[0,5,10,15,20,25,30])

```
![stacked_boxplot](https://github.com/JonathanLim1/ASR_Assessment/blob/master/images/stacked_boxplot.png?raw=true)

## Ploting time/frequency plot of ASR model to identify phoneme error at given frame

```python

#import 
from asrassessment import main as asrtest

#file directory
phn_file_dir = TIMIT_dict['train']['dr1']['fecd0']['phn'][0]
wav_file_dir = TIMIT_dict['train']['dr1']['fecd0']['wav'][0]


asrtest.phoneme_wavchart(timit_phndir = phn_file_dir, 
                         timit_wavdir = wav_file_dir,
                         asr_model=allosaurus_model,
                         vlinecolor='grey',
                         print_df=False)

```
![freq_phn](https://github.com/JonathanLim1/ASR_Assessment/blob/master/images/phn_freq.png?raw=true)


### Allosaurus Model 

```python
%pip install allosaurus
from allosaurus.app import read_recognizer

def allosaurus_model(file_directory,fr=16000,dataframe=False):
  
    model = read_recognizer()
    str_output = model.recognize(file_directory,lang_id='eng',timestamp=True)
    lst_output = str_output.split("\n")
    df = pd.DataFrame(lst_output, columns=['header'])
    df = df.header.str.split(pat=' ',expand=True)
    df.columns = ['start','timing','phoneme']
    
    #edit dataframe (add 'timing' to 'start' to get 'end' time/change start & end to milliseconds)
    df['start'] = df['start'].astype(float)
    df['start'] = df['start'].values*fr
    
    df['timing'] = df['timing'].astype(float)
    df['timing'] = df['timing'].values*fr
    
    df['end'] = df.apply(lambda row: row.start + row.timing, axis = 1)
    finaldf = df[['start','end', 'phoneme']]
    
    if dataframe == True:
        return finaldf
    else:
        allosaurus_phn = col_to_string(finaldf,colname='phoneme')
    return allosaurus_phn
```

### Speech Recognition Model (Google)
```bash
!pip install SpeechRecognition 
```
```python
import speech_recognition as sr

def speech_recog(timit_wav):
  r = sr.Recognizer()
  with sr.AudioFile(timit_wav) as source:
    audio = r.record(source) 
  
  return r.recognize_google(audio)
```

# Further Description  
## Method to get phoneme_error_rate 
Sources for detailed explanation for the error rate algorithm used in this package:
- https://joyyyjen.github.io/notebook-web/posts/wer/

## TIMIT standardisation mapping 
As the phoneme standard is not similar across various websites, this package follows a standardized mapping found in the module utils.standizer.py

Sources: 
1. https://docs.google.com/document/d/1rXzXyu5fEhco7oB9NAM9S4W0ZRz0iHozx6qn42UqD-8/edit
2. https://cdn.intechopen.com/pdfs/15948/InTech-Phoneme_recognition_on_the_timit_database.pdf
3. https://en.wikipedia.org/wiki/ARPABET


## TIMIT Acoustic-Phonetic Continuous Speech Corpus
TIMIT file: [TIMIT](https://en.wikipedia.org/wiki/TIMIT) is a corpus of phonemically and lexically transcribed speech of American English speakers of different sexes and dialects

Samples of the corpus can be found [here](https://catalog.ldc.upenn.edu/LDC93s1) 

You can download the entire corpus [here](https://academictorrents.com/details/34e2b78745138186976cbc27939b1b34d18bd5b3).

Watch how to download the torrent [here](https://academictorrents.com/docs/downloading.html)

# Package Requirements
Python version required: 3.9

This Project is created with: 
* glob2 version: 0.7
* tqdm version: 4.64.0
* librosa version: 0.9.2
* scipy version: 1.9.0
* numpy version: 1.23.1
* pandas version: 1.4.3
* sklearn version: 0.0
* pydub version: 0.25.1
* soundfile version: 0.10.2
* plotly version: 5.8.0
* matplotlib version: 3.5.3

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)



