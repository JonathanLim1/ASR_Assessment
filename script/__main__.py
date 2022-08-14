#Main functions for plotting 

#global imports 
import numpy as np
import pandas as pd

import plotly.graph_objects as go
import plotly.express as px
from collections import OrderedDict
from scipy.io.wavfile import read
import matplotlib.pyplot as plt

#local imports
from utils.standardizer import read_phn,TIMIT_to_IPA,IPA_to_TIMIT
from utils.phone_error_rate import error_rate, load_asr_dict,compare_phonemes_perc,compare_phn_wrd_noise_multi


def phn_boxplot(phn_counter_dict, styling_outliers = 'suspectedoutliers'):

  ### <Purpose of function>: Plot boxplot
  ### <Input variables>    : phn_counter_dict = Dictionary containing phoneme as key and list of % correctly predicted phonemes as value.
  ###                        styling_outliers = All Points - "all" / 
  ###                                           Only Whiskers - False / 
  ###                                           Suspected Outliers - suspectedoutliers /
  ###                                           Whiskers and Outliers - "outliers"
  ###                                           (Default set to "Suspected Outliers", full detail: https://plotly.com/python/box-plots/)
  ### <Output>             : Boxplot

  #Initiate
  fig = go.Figure()
  
  #Maintain order of dictionary as written 
  ordered_dict = OrderedDict(phn_counter_dict.items())

  for key in ordered_dict:
    fig.add_trace(go.Box(
        y=ordered_dict[key],
        name=key,
        boxpoints= styling_outliers,
        marker=dict(
            line=dict(
                outliercolor='rgba(219, 64, 82, 0.6)'
    ))))

  #x-axis
  fig.update_layout(title_text=f"Phoneme Accuracy Rate")
  fig.update_xaxes(
          tickangle = 90,
          title_text = "Phonemes",
          title_standoff = 25)
  
  #y-axis
  fig.update_yaxes(
          title_text = "Accuracy (%)",
          title_standoff = 25)

  fig.show()

def noise_stacked_boxplot(error_rate_df,
                          x_axis = "Error Rate (%)",
                          y_axis = "Volume",
                          type_error = "Type of Error"):
  
  ### <Purpose of Function> : Plot stacked boxplot from y-axis
  ### <Input variables>     : error_rate_df = dataframe with Columns ("Volume", "Error Rate (%)", "Type of Error")
  ### <Output>              : Stacked boxplot

  fig = px.bar(error_rate_df, x = x_axis, y = y_axis, color = type_error, barmode = 'stack')
  fig.show()

### SIMPLIFIED FUNCTIONS (MAIN FUNCTIONS)
#simplified function to plot phn boxplot 
def full_phn_boxplot(asr_model,phn_counter_dict,DR=[1,7],styling_outliers = False):
    asr_dict = load_asr_dict(asr_model=asr_model,DR=DR)
    phn_counter_dict = compare_phonemes_perc(asr_dict,DR=DR)

    return phn_boxplot(phn_counter_dict,styling_outliers=styling_outliers)

def full_noise_stackedplot(audio_dict,
                            noise_wav,
                            asr_phn_model,
                            asr_txt_model,
                            DR = [0,None],
                            SPK = [0,None],
                            louder_volumes=[],
                            softer_volumes=[]):

    #Full description of inputs is in utils.phone error_rate func compare_phn_wrd_noise_multi
    error_rate_df = compare_phn_wrd_noise_multi(audio_dict = audio_dict,
                                                noise_wav = noise_wav,
                                                asr_phn_model = asr_phn_model,
                                                asr_txt_model = asr_txt_model,
                                                DR = DR,
                                                SPK = SPK,
                                                louder_volumes = louder_volumes,
                                                softer_volumes = softer_volumes)
    return noise_stacked_boxplot(error_rate_df)

#Function to plot wav graph showing phoneme per time and error occur at which frames
def phoneme_wavchart(timit_phndir, timit_wavdir,asr_model,vlinecolor='grey',print_df=False):

  phn_file = timit_phndir
  samplerate, data = read(timit_wavdir)

  time = np.arange(0,len(data))

  #initiate plot
  plt.figure(figsize=(20,10))
  plt.plot(time,data)

  #set up vlines
  list_timing = read_phn(phn_file,df=True)['end'].tolist()
  list_phn    = read_phn(phn_file,df=True)['phoneme'].tolist()
  list_timing = [int(i) for i in list_timing]
  plt.vlines(x=list_timing,ymin=-35000,ymax=35000,colors = vlinecolor,linestyle='dotted')
  for i,timing in enumerate(list_timing):
    plt.text(timing,-36000,timing,rotation=90,horizontalalignment='right')
    if i%2 == 0:
      plt.text(timing,35000,list_phn[i],verticalalignment = 'top',horizontalalignment='center', fontsize='x-large')
    else:
      plt.text(timing,33000,list_phn[i],verticalalignment = 'top',horizontalalignment='center', fontsize='x-large')

  ### plot highlights of wrong area
  timittest = TIMIT_to_IPA(read_phn(phn_file,string=True))[1:-1]     #TIMIT phn #[1:-1] to remove the '/' 
  asrtest = IPA_to_TIMIT(asr_model(timit_wavdir,dataframe=False)) #ASR phn

  error_rate_df,tracker_df = error_rate(timittest,asrtest)           #get tracker_df
  tracker_df.index+=1                                                #shift index of tracker_df up by 1

  timit_phn = read_phn(phn_file,df=True).iloc[1:-1]                  #timit phn (dataframe)
  merged_df = pd.concat([timit_phn,tracker_df],axis=1)               #concat left df

  merged_df['start'] = merged_df['start'].astype(int)                #convert string to int
  merged_df['end'] = merged_df['end'].astype(int)
  merged_df.columns = ['start','end','phoneme','initial_phoneme','error','substituted'] # rename col name

  #select for substitution errors
  sub_df = merged_df[merged_df['error'] == 'Substitution'][['start','end']]
  for i in range(len(sub_df)):
    if i==0:
      plt.axvspan(sub_df.iloc[i][0], sub_df.iloc[i][1], color='orange', alpha=0.4,label='substituted')
    else:
      plt.axvspan(sub_df.iloc[i][0], sub_df.iloc[i][1], color='orange', alpha=0.4)

  #select for deletion errors
  del_df = merged_df[merged_df['error'] == 'Deletion'][['start','end']]
  for i in range(len(del_df)):
    if i==0:
      plt.axvspan(del_df.iloc[i][0], del_df.iloc[i][1], color='red', alpha=0.4,label='deleted')
    else:
      plt.axvspan(del_df.iloc[i][0], del_df.iloc[i][1], color='red', alpha=0.4)

  #labels
  plt.xlabel(f'Time [{samplerate} frame/s]')
  plt.ylabel('Amplitude') 
  plt.title('Plot showing phonemes per frame')
  plt.legend(bbox_to_anchor=(1.05, 1),loc='center')
  plt.show()
  
  if print_df == True:
    print("Dataframe Showing Substitution")
    print(merged_df[merged_df['error'] == 'Substitution'][['start','end','phoneme','substituted']])

    print("Dataframe Showing Deletion")
    print(merged_df[merged_df['error'] == 'Deletion'][['start','end','phoneme']])
