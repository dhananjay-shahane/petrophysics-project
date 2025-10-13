import os
import glob
import sys
import lasio
from matplotlib.ticker import LogFormatterSciNotation
import numpy as np
import pandas as pd

def add_files_in_folder(dirname):
    files = os.listdir(dirname)
    LASFiles=[]
    
    for f in files:
        file_path = os.path.join(dirname, f)
        #print(file_path)
        file_name=os.path.basename(file_path)
        LASFiles.append(LASFile(file_path,file_name))
    return LASFiles
def files_in_folder(dirname):
    print(dirname)
    files=glob.glob(dirname+'/*.LAS')
    print(files)
    #files = os.listdir(dirname)
    LASFiles=[]
    for f in files:
        file_path = os.path.join(dirname, f)
        #print(file_path)
        file_name=os.path.basename(file_path)
        LASFiles.append(LASFile(file_path,file_name))
    return LASFiles
class LASFile():
    def __init__(self, file_path, file_name):
        self.path = file_path
        self.name = file_name
        
def Modified_Well_Name(wellname, wellnametext,nPad):
    print('in modified well name', nPad)
    last_alphas = Get_Last_Alphas(wellname)
    wellnamenumber = int(''.join(filter(str.isdigit, wellname)))
    padded_well_number = str(wellnamenumber).rjust(nPad,"0")
    newwellname = wellnametext + "-" + padded_well_number + last_alphas
    #newwellname = wellnametext + "-" + "{:0"+str(3)+"d}".format(wellnamenumber)
    return newwellname

def Get_Last_Alphas(wellname):
    only_digit=""
    for char in wellname:
        if ord(char)>=48 and ord(char)<=58:
            only_digit+=char
    last_alphas = wellname.split(only_digit)[1]
    return last_alphas

def Get_Data_Start_Line(lines):
    count=0
    mdline=0
    while count < len(lines):
        if (lines[count].split()[0]=='MD'):
            mdline=count
        count += 1
        
    datastartline = mdline+2
    
    return datastartline

def Convert_Geolog_Tops_To_Param_Tops(lasFolder,tops_filename, param_filename):
    print("Converting Geolog tops to paramters tops")
   
    
    df_tops = pd.DataFrame()
    
    tops_folder = os.path.join(os.path.dirname(lasFolder)+'\Tops_Folder')
   
    tops_file = os.path.join(tops_folder,tops_filename)
    param_file = os.path.join(tops_folder,param_filename)
    df_gt = pd.read_csv(tops_file)
    
    df_param_list=[]
    for index, row in df_gt.iterrows():
        r = row.to_dict() # Converting the row to dictionary

        if (index < len(df_gt)-1):
            currwell = df_gt['Well'][index]
            nextwell = df_gt['Well'][index+1]
            if nextwell==currwell:
                r['Base']=df_gt['Depth'][index+1]
                df_param_list.append(r) # appending the dictionary to list
    
    #df_param_tops = df_geol_tops[['Well','Depth','Top']]
   
    df_param = pd.DataFrame(df_param_list)
    df_param=df_param.rename(columns = {'Top':'Zone'})
    df_param=df_param.rename(columns = {'Depth':'Top'})

    df_param.to_csv(param_file, index=False)
def Convert_Geolog_Tops_Excel_To_Param_Tops_csv(tops_file_path, sheet_name, param_file_path):
    print("Converting Geolog tops to paramters tops")
   
    
    df_tops = pd.DataFrame()
    # Read the data from the specified sheet
    df_gt = pd.read_excel(tops_file_path, sheet_name=sheet_name)
    df_gt= df_gt.dropna()
    # Display the entire DataFrame
    print(df_gt.head(100).to_string(index=False))
    
    # Assuming df_gt is already defined
    df_param_list = []

    # Create a new DataFrame with the condition
    for index in range(len(df_gt) - 1):
        currwell = df_gt['WELL'].iloc[index]
        nextwell = df_gt['WELL'].iloc[index + 1]
        
        if nextwell == currwell:
            # Create a dictionary with the necessary values
            r = df_gt.iloc[index].to_dict()  # Use iloc for better performance
            r['BASE'] = df_gt['DEPTH'].iloc[index + 1]
            df_param_list.append(r)

    # Convert list of dictionaries to DataFrame
    df_param = pd.DataFrame(df_param_list)

    # Rename columns
    df_param.rename(columns={'TOP': 'ZONE', 'DEPTH': 'TOP'}, inplace=True)

    # Display the result
    print(df_param)

    df_param.to_csv(param_file_path, index=False)
def get_log_curves(las_File_Path):
    
    las = lasio.read(las_File_Path)
    curves= las.curves
    curve_mnemonics=[]
    for curve in las.curves:
        curve_mnemonics.append(curve.mnemonic)
    return curve_mnemonics

def get_basis(df_zones, well, zones):
    df=df_zones[(df_zones['Well']==well) & df_zones['Zone'].isin(zones)]
    arr = df[['Well','Zone','Top','Base']].to_numpy()
    top = min(df['Top'])
    base = max(df['Base'])
    return top, base

class CustomTicker(LogFormatterSciNotation): 
  
    def __call__(self, x, pos = None): 
  
        if x >=1: 
            return "{x:.0f}".format(x = x) 
  
        else: 
            return "{x:.1f}".format(x = x) 
def scientific_notation(x, pos):
    return f'{x:.0e}'

def log_format_large_numbers(x, pos):
    if x == 0:
        return '0'
    exp = int(np.log10(abs(x)))
    if exp >= 6:
        return f'{x/1e6:.1f}M'
    elif exp >= 3:
        return f'{x/1e3:.1f}K'
    else:
        return f'{x:.1f}'
    
def getprop(log,property):
    
    df = pd.read_csv('PETRO_CONFIGURATION\\petro-config.csv', delimiter=',',index_col=0)
    return df._get_value(log, property) 
# function to get unique values
def unique(list1):

    # initialize a null list
    unique_list = []
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
            
    return unique_list
def Convert(string):
    li = list(string.split(";"))
    return li
    