import sys, datetime, os, pathlib
from PyQt5.QtWidgets import (
    QMainWindow, QTextEdit,QAction, QListWidget, QWidget, QVBoxLayout,QFileDialog, QInputDialog
)
from PyQt5.QtCore import Qt, QSettings
from fe_data_objects import *
from alias import *
from log_info import *
from Utility import *
class DataIMPEX:
    def __init__(self,wells):
        self.title = 'Data_IMPEX'
        self.settings = QSettings('Petrocene', 'PetroceneApp')
        self.project_path = self.settings.value("project_path", "", type=str)
        self.project_folder = os.path.join(self.project_path,'')
        self.wells_Folder = os.path.join(self.project_folder, '10-WELLS')
        self.specs_Folder = os.path.join(self.project_folder, '09-SPECS')
        self.alias_file_path = os.path.join(self.specs_Folder,'alias.alias')
        self.log_info_file_path = os.path.join(self.specs_Folder,'logs.info')
        self.wells=wells
    def Load_Wells(self):
        print('Loading wells from previously used wells folder')

        self.current_well=  self.settings.value("current_well", "", type=str)
        self.current_dataset = self.settings.value("current_dataset", "", type=str)

        if self.wells_Folder:
            # List all files in the selected folder
            files = os.listdir(self.wells_Folder)
            # Filter files by extension
            well_files = [f for f in files if f.endswith('ptrc')]    
            for f in well_files:
                filepath = os.path.join(self.wells_Folder,f)
                w = Well.deserialize(filepath=filepath)
                self.wells.append(w)
                #print(w.well_name)
    def load_LAS_Files(self, project_folder):
        # Code to execute when button 2 is clicked
        las_File_Folder = os.path.join(project_folder,'LAS_FOLDER')
        files = os.listdir(las_File_Folder)
            # Filter files by extension
        las_files = [f for f in files if f.endswith('las')]    
       
        print(las_files)
        filepath =las_files[0]
        # Check if the path points to a valid file
        if os.path.isfile(filepath):
            print(filepath)
        else:
            raise FileNotFoundError(f"The file at '{filepath}' does not exist.")
        
        las = lasio.read(filepath)
        wellname = las.well.WELL.value
        datasetname = las.params.SET.value
        top = las.well.STRT.value
        bottom = las.well.STOP.value
        dataset = Dataset.from_las(filepath,dataset_name=datasetname, dataset_type='Cont', well_name=wellname)
        
        print(wellname)
        #print(self.mainwindow.wells)
        existing_wells = self.mainwindow.wells
        if wellname in [w.well_name for w in existing_wells]:
            thewell =   next((w for w in existing_wells if w.well_name == wellname), None)
            print('Well name exists:', thewell.well_name)
            thewell.datasets.append(thewell)
            self.text_edit.append("Dataset appended: " + datasetname)
        else:
            #create a new well (WELL_HEADER and REFERENCE folders must be created)
            print('Creating a new well')
            thewell=Well(date_created=datetime.now(), well_name=wellname, well_type='Dev')
            ref = Dataset.reference(0, bottom=bottom, dataset_name='REFERENCE', dataset_type='REFERENCE', well_name=wellname)
            wh = Dataset.well_header(dataset_name='WELL_HEADER', dataset_type='WELL_HEADER', well_name=wellname)
            const = Constant('WELL_NAME', thewell.well_name)
            wh.constants.append(const)
            self.text_edit.append("New well created: "+thewell.well_name)
            thewell.datasets.append(ref)
            thewell.datasets.append(wh)
            thewell.datasets.append(dataset)
            self.text_edit.append("Dataset appended: "+ datasetname)
            self.mainwindow.wells.append(thewell)
            
    def export_df_to_las(self, df, well_name, set_name,las_file_path):
        kv = KeyValueStore( self.alias_file_path)
        li = ItemCollection(self.log_info_file_path)
        #print(li.filename)
        #print(li.list_items())
        #li.list_items()
        #kv.print_data()
        outlas = lasio.LASFile()
        outlas.well['WELL']=lasio.HeaderItem('WELL', value=well_name)
        outlas.well['SET']=lasio.HeaderItem('SET', value=set_name)
        for mnem in df.columns:
            #print(mnem)
            unit = li.get_attribute_by_item_name(mnem, 'unit')
            descr = li.get_attribute_by_item_name(mnem, 'description')
            #print(unit)
            outlas.append_curve(mnemonic=mnem, data = df[mnem], unit=unit, descr=descr)
        outlas.write(las_file_path, version=2.0)
        print('LAS file saved to file : ',las_file_path)
        
    def import_Single_LAS_File(self, las_file_path):
        
        # Code to execute when button 2 is clicked
        filepath =las_file_path
        # Check if the path points to a valid file
        if os.path.isfile(filepath):
            print(filepath)
        else:
            raise FileNotFoundError(f"The file at '{filepath}' does not exist.")
        
        las = lasio.read(filepath)
        wellname = las.well.WELL.value
        datasetname = las.params.SET.value
        top = las.well.STRT.value
        bottom = las.well.STOP.value
        dataset = Dataset.from_las(filepath,dataset_name=datasetname, dataset_type='Cont', well_name=wellname)
        
        print(wellname)
        #print(self.mainwindow.wells)
        print('Loaded Wells:', [w.well_name for w in self.wells])
        existing_wells = self.wells
        if wellname in [w.well_name for w in existing_wells]:
            thewell =   next((w for w in existing_wells if w.well_name == wellname), None)
            print('Well name exists:', thewell.well_name)
            existing_dataset_names = [dtst.name for dtst in thewell.datasets]
            new_name = generate_unique_name(existing_names=existing_dataset_names, base_name=dataset.name)
            print('The dataset named',dataset.name, 'already exists. imported dataset name will be:',new_name)
            dataset.name = new_name
            thewell.datasets.append(dataset)
        else:
            #create a new well
            thewell=Well(date_created=datetime.now(), well_name=wellname, well_type='Dev')
            ref = Dataset.reference(0, bottom=bottom, dataset_name='REFERENCE', dataset_type='REFERENCE', well_name=wellname)
            wh = Dataset.well_header(dataset_name='WELL_HEADER', dataset_type='WELL_HEADER', well_name=wellname)
            const = Constant(name ='WELL_NAME',value = thewell.well_name, tag = thewell.well_name)
            wh.constants.append(const)
            thewell.datasets.append(ref)
            thewell.datasets.append(wh)
            thewell.datasets.append(dataset)
            

        filepath = os.path.join(self.wells_Folder,thewell.well_name+'.ptrc')
        thewell.serialize(filename=filepath)
        print('Saved Wells to :', thewell.well_name, self.wells_Folder)
        
    def load_multi_well_las_files_from_folder(self, las_Folder):
        files = os.listdir(las_Folder)
        las_files = [f for f in files if f.endswith('las')]  
       
        for f in las_files:
            #print(f)
            # base_name = os.path.splitext(f)[0]
            print(f)
            las_file_path=os.path.join(las_Folder,f)
            self.import_Single_LAS_File(las_file_path)
    
    def load_single_well_deviation_data_from_excel(self, excel_file_path, sheet_name, well_name):
        print("Loading directional data from excel file Well Data Acquistion Summary")
   
        # Read the data from the specified sheet
        dev_df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
        dev_df= dev_df.dropna()
        # Display the entire DataFrame
        print(dev_df.head(100).to_string(index=False))
        
        dev_df_well = dev_df[dev_df['WELL']==well_name]
        
        print('Single well dataframe:', well_name, dev_df_well)
        
        datasetname = 'DIRECTIONAL'
        dataset = Dataset(date_created=datetime.now(),name='DIRECTIONAL', type='Point', wellname=well_name, index_name='DEPTH' )
        dev_df_well = dev_df_well.drop('WELL', axis=1)
        for col in dev_df_well.columns:
            #print(dev_df_well[col])
            log = WellLog(date = datetime.now(),name=col.upper(), description='Loaded from csv',  log=dev_df_well[col].to_list(), dtst = dataset.name)
            dataset.well_logs.append(log)
        # if well exists
        existing_wells = self.wells
        if well_name in [w.well_name for w in existing_wells]:
            thewell =   next((w for w in self.wells if w.well_name == well_name), None)
            print('Well name exists:', thewell.well_name)
            existing_dataset_names = [dtst.name for dtst in thewell.datasets]
            new_name = generate_unique_name(existing_names=existing_dataset_names, base_name=dataset.name)
            print('The dataset named',dataset.name, 'already exists. imported dataset name will be:',new_name)
            dataset.name = new_name
            thewell.datasets.append(dataset)
            #self.text_edit.append("Dataset appended: " + datasetname)
        #create a new well
        else:
            thewell=Well(date_created=datetime.now(), well_name=well_name, well_type='Dev')
            thewell.datasets.append(dataset)
            #self.text_edit.append("Dataset appended: "+ datasetname)
            self.wells.append(thewell)
            
        print('Saving wells')
        
        for dtst in thewell.datasets:
            #print('dataset:', dtst.name)
            for wl in dtst.well_logs:
                print(dtst.name, 'log:', wl.name)
                #print(wl.log)
                
        filepath = os.path.join(self.wells_Folder,thewell.well_name+'.ptrc')
        thewell.serialize(filename=filepath)
        print('Saved Wells to :', thewell.well_name, self.wells_Folder)

                
    def load_multi_well_deviation_data_from_excel(self, excel_file_path, sheet_name, allowed_headers, dev_mnemonics):
        
        # Load the Excel file
        df1 = pd.read_excel(excel_file_path, sheet_name=sheet_name, header=None)
        pos = self.find_first_occurrence(df1, 'WELL')
        print(pos)
        
        # Reload the Excel file with header row identified
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name, header=pos[0])
         # Extract column names from the first row
        # Exclude columns before the found column
        df = df.iloc[:, pos[1]:].dropna(how='all')
        
        # Create a pattern that matches any of the allowed headers as substrings, case-insensitive
        pattern = '|'.join(allowed_headers)  # Join allowed headers with '|' for regex OR
        regex_pattern = f'({pattern})'  # Create regex pattern

        # Filter columns: Keep columns where header is not empty and matches the regex pattern
        filtered_df = df.loc[:, df.columns.notnull() & df.columns.str.contains(regex_pattern, case=False, regex=True)]

        
        dev_df = self.keep_and_rename_columns(filtered_df,dev_mnemonics)
        
        # Capitalize the column names
        dev_df.columns = dev_df.columns.str.upper()
        print(dev_df)

        # Display the entire DataFrame
        print(dev_df.head(100).to_string(index=False))
        well_names = dev_df['WELL'].unique()
        print('Unique well names', well_names)
        for well_name in well_names:
            dev_df_well = dev_df[dev_df['WELL']==well_name]
            print('Single well dataframe:', well_name, dev_df_well)
            datasetname = 'DIRECTIONAL'
            dataset = Dataset(date_created=datetime.now(),name='DIRECTIONAL', type='Point', wellname=well_name, index_name='DEPTH' )
            dev_df_well = dev_df_well.drop('WELL', axis=1)
            for col in dev_df_well.columns:
                #print(dev_df_well[col])
                log = WellLog(date = datetime.now(),name=col.upper(), description='Loaded from csv',  log=dev_df_well[col].to_list(), dtst = dataset.name)
                dataset.well_logs.append(log)
            # if well exists
            if well_name in [w.well_name for w in self.wells]:
                thewell =   next((w for w in self.wells if w.well_name == well_name), None)
                print('Well name exists:', thewell.well_name)
                thewell.datasets.append(dataset)
                #self.text_edit.append("Dataset appended: " + datasetname)
            #create a new well
            else:
                thewell=Well(date_created=datetime.now(), well_name=well_name, well_type='Dev')
                thewell.datasets.append(dataset)
                #self.text_edit.append("Dataset appended: "+ datasetname)
                self.wells.append(thewell)
                
            print(thewell.well_name)
            for dtst in thewell.datasets:
                #print('dataset:', dtst.name)
                for wl in dtst.well_logs:
                    print('log:', wl.name)
                    #print(wl.log)
                    
            filepath = os.path.join(self.wells_Folder,thewell.well_name+'.ptrc')
            thewell.serialize(filename=filepath)
            print('Saved Wells to :', thewell.well_name, self.wells_Folder)
    def keep_and_rename_columns(self, filtered_df, new_column_names):
        """Keep only specified columns and rename them."""
        # Keep only the first three columns
        columns_to_keep = filtered_df.columns[:len(new_column_names)]  # Adjust as needed to ensure exactly three columns
        filtered_df = filtered_df[columns_to_keep]

        # Rename columns
        filtered_df.columns = new_column_names[:len(filtered_df.columns)]  # Rename only if there are enough new names

        return filtered_df
    def load_multi_well_las_files_from_folder(self, las_Folder):
        files = os.listdir(las_Folder)
        las_files = [f for f in files if f.endswith('las')]  
       
        for f in las_files:
            #print(f)
            # base_name = os.path.splitext(f)[0]
            print(f)
            las_file_path=os.path.join(las_Folder,f)
            self.import_Single_LAS_File(las_file_path)
    
    def load_single_well_tops_data_from_excel(self, excel_file_path, sheet_name, well_name):
        print("Loading tops data from excel file Well Data Acquistion Summary")
   
        # Read the data from the specified sheet
        top_df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
        top_df= top_df.dropna()
        # Display the entire DataFrame
        print(top_df.head(100).to_string(index=False))
        
        top_df_well = top_df[top_df['WELL']==well_name]
        
        print('Single well dataframe:', well_name, top_df_well)
        
        datasetname = 'TOPS'
        dataset = Dataset(date_created=datetime.now(),name=datasetname, type='Tops', wellname=well_name, index_name='DEPTH' )
        top_df_well = top_df_well.drop('WELL', axis=1)
        interp = "TOPS"
        for col in top_df_well.columns:
            #print(dev_df_well[col])
            if(col=="DEPTH"):
                log_type = 'float'
            if(col=="TOP"):
                log_type = 'str'
            log = WellLog(date = datetime.now(),name=col.upper(), description='Loaded from csv',  interpolation=interp, log_type = log_type, log=top_df_well[col].to_list(), dtst = dataset.name)
            dataset.well_logs.append(log)
        # if well exists
        existing_wells = self.wells
        if well_name in [w.well_name for w in existing_wells]:
            thewell =   next((w for w in self.wells if w.well_name == well_name), None)
            print('Well name exists:', thewell.well_name)
            existing_dataset_names = [dtst.name for dtst in thewell.datasets]
            new_name = generate_unique_name(existing_names=existing_dataset_names, base_name=dataset.name)
            print('The dataset named',dataset.name, 'already exists. imported dataset name will be:',new_name)
            dataset.name = new_name
            thewell.datasets.append(dataset)
            #self.text_edit.append("Dataset appended: " + datasetname)
        #create a new well
        else:
            thewell=Well(date_created=datetime.now(), well_name=well_name, well_type='Dev')
            thewell.datasets.append(dataset)
            #self.text_edit.append("Dataset appended: "+ datasetname)
            self.wells.append(thewell)
            
        print('Saving wells')
        
        for dtst in thewell.datasets:
            #print('dataset:', dtst.name)
            for wl in dtst.well_logs:
                print(dtst.name, 'log:', wl.name)
                #print(wl.log)
                
        filepath = os.path.join(self.wells_Folder,thewell.well_name+'.ptrc')
        thewell.serialize(filename=filepath)
        print('Saved Wells to :', thewell.well_name, self.wells_Folder)

    def load_multi_well_zone_data_from_excel(self, excel_file_path, sheet_name):
        # Code to execute when button 2 is clicked
        
        
        # Read the data from the specified sheet
        dev_df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
        dev_df= dev_df.dropna()
        # Display the entire DataFrame
        print(dev_df.head(100).to_string(index=False))
        well_names = dev_df['WELL'].unique()
        print('Unique well names', well_names)
        for well_name in well_names:
            dev_df_well = dev_df[dev_df['WELL']==well_name]
            print('Single well dataframe:', well_name, dev_df_well)
            datasetname = 'DIRECTIONAL'
            dataset = Dataset(date_created=datetime.now(),name='ZONES', type='Zones', wellname=well_name, index_name='DEPTH' )
            dev_df_well = dev_df_well.drop('WELL', axis=1)
            for col in dev_df_well.columns:
                #print(dev_df_well[col])
                log = WellLog(date = datetime.now(),name=col.upper(), description='Loaded from csv',  log=dev_df_well[col].to_list(), dtst = dataset.name)
                dataset.well_logs.append(log)
            # if well exists
            if well_name in [w.well_name for w in self.wells]:
                thewell =   next((w for w in self.wells if w.well_name == well_name), None)
                print('Well name exists:', thewell.well_name)
                thewell.datasets.append(dataset)
                #self.text_edit.append("Dataset appended: " + datasetname)
            #create a new well
            else:
                thewell=Well(date_created=datetime.now(), well_name=well_name, well_type='Dev')
                thewell.datasets.append(dataset)
                #self.text_edit.append("Dataset appended: "+ datasetname)
                self.wells.append(thewell)
                
            print(thewell.well_name)
            for dtst in thewell.datasets:
                #print('dataset:', dtst.name)
                for wl in dtst.well_logs:
                    print('log:', wl.name)
                    #print(wl.log)
                    
            filepath = os.path.join(self.wells_Folder,thewell.well_name+'.ptrc')
            thewell.serialize(filename=filepath)
            print('Saved Wells to :', thewell.well_name, self.wells_Folder)
    
      
    def parse_row_to_constants(self, row: List[Union[str, float, int]],   column_names: List[str], 
                                tag: str, exclude_indices: List[int] = None) -> List[Constant]:
        
        constants = []
        if exclude_indices is None:
            exclude_indices = []

        for i, value in enumerate(row):
            if i in exclude_indices:
                continue  # Skip excluded indices

            column_name = column_names[i]
            
            if column_name == 'Drilled Date':
                if isinstance(value, pd.Timestamp):
                    value = value.to_pydatetime()  # Convert Timestamp to datetime
                elif isinstance(value, str):
                    # Try parsing in different formats
                    for fmt in ['%d-%b-%y', 'dd-mm-yyyy']:
                        try:
                            value = datetime.strptime(value, fmt)  # Attempt to parse the date
                            break  # Break if parsing was successful
                        except ValueError:
                            continue  # Try the next format
                    else:
                        value = None  # Set to None if no format matches
                elif isinstance(value, datetime):
                    value=value
                else:
                    value = None  # Handle other cases as needed
            elif isinstance(value, (float, int)):  # Check if the value is a float or int
                value = float(value)  # Ensure it's treated as a float
            else:
                value = str(value)  # Treat it as a string
            
            constants.append(Constant(name=column_name, value=value, tag=tag))  # Associate the tag
        
        return constants
        
        return constants
    def insert_Constants_From_Well_Information(self,file_path, sheet_name):
        # Read the Excel file
        #file_path = 'your_file.xlsx'  # Replace with your actual file path
        #sheet_name = 'Sheet1'          # Replace with your sheet name

        # Load the Excel file
        df1 = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        pos = self.find_first_occurrence(df1, 'WELL')
        print(pos)
        
        # Reload the Excel file with header row identified
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=pos[0])
         # Extract column names from the first row
        # Exclude columns before the found column
        df = df.iloc[:, pos[1]:].dropna(how='all')
        # Capitalize the column names
        df.columns = df.columns.str.upper()
        column_names = df.columns.tolist()
        
        print(df)
        print("Column Names:", column_names)

        # Loop through each data row
        for index in range(0, len(df)):  # Start from 1 to skip header row
            data_row = df.iloc[index].tolist()  # Extract the row as a list
            tag = data_row[0]  # Get the tag from the second column (AAA)
            
            # Specify indices to exclude (e.g., exclude columns at index 0, 1, and 2)
            excluded_indices = []
            # Parse the row into Constant objects
            constants = self.parse_row_to_constants(data_row, column_names, tag, excluded_indices)
            print('Number of constants read:',len(constants))
            for const in constants:
                print(const.name, const.tag)
            #print(self.wells)
            # Output the constants
            for const in constants:
                w  =find_well_by_name(self.wells,const.tag)
                if w:
                    print(w.well_name)
                    wh_dataset = find_dataset_by_name(w,'WELL_HEADER')

                    if const.name in [c.name for c in wh_dataset.constants]:
                        #update constant value
                        print(const.name)
                        const = find_constant_by_name(wh_dataset,const.name)
                        if const:
                            #replace
                            const.value = const.value
                            print (const.name, 'value replace to:', const.value)
                        else:
                            print('Constant:', const.name, ' does not exist')
                    else:
                        #append constant
                        wh_dataset.constants.append(const)
                        print (const.name, 'inserted with value:', const.value)
                    
                    filepath = os.path.join(self.wells_Folder,w.well_name+'.ptrc')
                    w.serialize(filename=filepath)
                    print('Saved Wells to :', w.well_name, self.wells_Folder)
        
    def find_first_occurrence(self, df, search_word):
        # Limit the DataFrame to the first three rows and first three columns
        limited_df = df.iloc[0:3, 0:3]

        # Find the first occurrence of the search word
        for row_index in limited_df.index:
            for col_index in limited_df.columns:
                print(limited_df.at[row_index, col_index])
                if limited_df.at[row_index, col_index] == search_word:
                    return row_index, col_index  # Return row and column index
        return None  # Return None if not found
            

