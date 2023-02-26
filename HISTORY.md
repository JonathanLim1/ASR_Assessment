# History of version changes 

### v 0.1.16
-  updated timit_load function to include timit files with capital letters named files
### v 0.1.12
- Changes to phone_error_rate load_asr_dict function (missing variable in compare_phonemes_perc not in full_phn_boxplot)
- Edited README.md

### v 0.1.11
- Changes to phone_error_rate load_asr_dict function 

### v 0.1.10
- Changes to phone_error_rate load_asr_dict function (missing variable in load_asr_dict not in full_phn_boxplot)

### v 0.1.9
- Error in timit directory for TIMIT_File function  in timit_load.py
- Updated README.md to show:
    - Installation guide 
    - examples 
- edited phone_error_rate functions


### v 0.1.8
Error in output for timit_load.py TIMIT_File function

### v 0.1.7 
Error in import glob. Supposed to be from glob import glob
changed in noise_sidefunc.py & timit_load.py

### v 0.1.6
As in version 0.1.5, the syntax of local import (with dot change) really worked so this version includes for all the other modules


### v. 0.1.5
Previously having problems with local import, going to try import with dot behind local module 
source: https://stackoverflow.com/questions/4142151/how-to-import-the-class-within-the-same-directory-or-sub-directory 

i.e. import data_input
change to import .data_input