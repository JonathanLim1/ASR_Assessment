Author: Jonathan Lim Wei Siang 
Email: Jonathanlimws@gmail.com 

# Main Function
This Python package allows you to assess the phonetic error rate and visualise them.

# Workflow of package
1. TIMIT file is loaded 
2. ASR Model converts audio.wav file into phoneme string
3. ASR Phoneme string is standardized to TIMIT standard to allow for comparison 
4. Phonetic Error Rate is generate 

## Additional
Noise can be added to audio.wav fiel to test the ASR model and step 2-4 is repeated

# Types of Plots
1. Boxplot of accuracy rate for each phoneme across selected TIMIT files 
2. Stacked boxplot of accuracy rate across varying added noise 
3. Time/frequency Plot any given TIMIT audio showing the timing/phoneme which was incorrected predicted (substitution and deletion only)
![alt text](/Users/jonathanlim/Desktop/Code_2022/ASR_Assessment/Screenshot 2022-08-12 at 16.57.12.png?raw=True)


# Requirements
TIMIT file: TIMIT is a corpus of phonemically and lexically transcribed speech of American English speakers of different sexes and dialects
link: https://en.wikipedia.org/wiki/TIMIT
