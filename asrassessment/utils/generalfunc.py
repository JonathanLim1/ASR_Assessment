#General functions 
def split_string(string):
  return string.split("/")

def col_to_string(df,colname):
  return '/'.join(df[colname].tolist())