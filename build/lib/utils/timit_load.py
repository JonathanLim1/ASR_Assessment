# function to load TIMIT file

##iteratively create dictionary for TIMIT FILE
# TIMIT__dict[TRAIN/TEST][DR?][SPEAKER?][TYPE OF FILE][index of file]

import glob

def TIMIT_file(file_directory):

    train_test_directory = glob(f"{file_directory}/T*")#use own file directory
    lst_filetypes =['phn','txt','wav','wrd']

    #create TRAIN/TEST key
    TIMIT_dict = {i.split("/")[-1]:{} for i in train_test_directory} 

    for file_type in train_test_directory:
        files = glob(f"{file_type}/*") #get directory for DRs
        filetype_dir= f"{file_type.split('/')[-1]}" #create variable for dict by filetype
        TIMIT_dict[filetype_dir] = {fil.split('/')[-1]:{} for fil in files} #create DR dict within the TRAIN/TEST dict
    
        for DR in files:
            speakers = glob(f"{DR}/*") #get directory for speakers
            DR_dir = f"{DR.split('/')[-1]}" #create variable for dict by DR
            TIMIT_dict[filetype_dir][DR_dir] = {speaker.split('/')[-1]:{} for speaker in speakers} #create speaker dict within the DR dict
        
            for speaker in speakers:
                recordings = glob(f"{speaker}/*")
                speaker_dir = f"{speaker.split('/')[-1]}"
        
                #seperate dict into file type (.phn, .wav, .txt)
                TIMIT_dict[filetype_dir][DR_dir][speaker_dir]= {filetype:[] for filetype in lst_filetypes}
        
                #seperate directory into file type
                for filetype in lst_filetypes:
                    lst = sorted(list(filter(lambda x: filetype in x, recordings)))
                    remove_lst = ['wav_SA1real', 'wav_SA1rec','wav_SA1wisp'] #files to remove from dict
                    TIMIT_dict[filetype_dir][DR_dir][speaker_dir][filetype] = [ele for ele in lst if remove_lst[0] not in ele and remove_lst[1] not in ele and remove_lst[2] not in ele]
            
    return file_directory