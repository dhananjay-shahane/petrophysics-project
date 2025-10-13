import sys, datetime, os, pathlib
from PyQt5.QtWidgets import (
    QMainWindow, QTextEdit,QAction, QListWidget, QWidget, QVBoxLayout,QFileDialog, QInputDialog
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag, QTextCursor
from matplotlib_widget import MatplotlibWidget
from custom_dock_widget import CustomDockWidget
from custom_object import CustomObject
from feedback_dock_widget import FeedbackDockWidget
from feedback_manager import *
from fe_data_objects import *
#from felib.data_browser_not_in_use import *
from feedback_dock_widget import *
from Utility import *
from logplotclass import *
from LogPlot import *
from well_select import *
from zonation_dock_widget import *
from CPI import *
from tvd_comp import *
from Data_Import_Export import *
from alias import *
from log_info import *
from minerals import *
from Project_Manager import *
from Generate_Excel_Report import *
from utilities1 import *
from plotclass import *

class DatabaseQuery:
    def __init__(self):
        self.title = 'Database query'
        self.wells = []
        self.current_well=None
        self.current_dataset = None
        # Load previously saved settings
        self.settings = QSettings('Petrocene', 'PetroceneApp')
        self.project_path = self.settings.value("project_path", "", type=str)
        self.project_folder = os.path.join(self.project_path,'')
        self.wells_Folder = os.path.join(self.project_folder, '10-WELLS')
        self.specs_Folder = os.path.join(self.project_folder, '09-SPECS')
        self.alias_file_path = os.path.join(self.specs_Folder,'alias.alias')
        self.log_info_file_path = os.path.join(self.specs_Folder,'logs.info')
        self.input_las_Folder = os.path.join(self.project_folder, '02-INPUT_LAS_FOLDER')
        self.deviation_Folder = os.path.join(self.project_folder, '03-DEVIATION')
        self.well_header_Folder = os.path.join(self.project_folder, '04-WELL_HEADER')
        self.tops_Folder = os.path.join(self.project_folder, '05-TOPS_FOLDER')
        self.zones_Folder = os.path.join(self.project_folder, '06-ZONES_FOLDER')
        self.zone_file_path = os.path.join(self.zones_Folder,'zones_parameters.csv')
        self.output_Folder = os.path.join(self.project_folder, '01-Output')
        self.output_file_path = os.path.join(self.output_Folder,'Well_Data_Summary.xlsx')
        #self.get_wells_from_ptrc()
        
    def get_wells_from_ptrc(self):
        print('Loading wells from previously used project folder')
        # Load previously saved settings
        self.settings = QSettings('Petrocene', 'PetroceneApp')
        self.project_path = self.settings.value("project_path", "", type=str)
        project_path = self.project_path
        
        print('This is project path', project_path)
        
    def Load_Wells(self):
        print('Loading wells from 10-WELLS folder')
        # Load previously saved settings
        self.settings = QSettings('Petrocene', 'PetroceneApp')
        self.project_path = self.settings.value("project_path", "", type=str)
        project_path = self.project_path
        print('Project path from setting', project_path)
        
        self.current_well=  self.settings.value("current_well", "", type=str)
        self.current_dataset = self.settings.value("current_dataset", "", type=str)
        
        
        if project_path:
            # List all files in the selected folder
            files = os.listdir( self.wells_Folder)
            # Filter files by extension
            well_files = [f for f in files if f.endswith('ptrc')]    
            for f in well_files:
                filepath = os.path.join( self.wells_Folder,f)
                w = Well.deserialize(filepath=filepath)
                self.wells.append(w)
                #print(w.well_name)
            #print('Loaded Wells:', [w.well_name for w in self.wells])
                
    def get_Well(self, wells, well_name):
        results=[]
        for w in wells:
            if getattr(w, 'well_name', None)==well_name:
                results.append(w)
        return results
    def get_Dataset(self, well, dtst_name):
        results=[]
        for d in well.datasets:
            if getattr(d, 'name', None)==dtst_name:
                results.append(d)
        return results
    
    def delete_Dataset(self, well_name, dtst_name):
        print('Deleting Dataset', dtst_name, 'from well:', well_name)
        #found_well = self.get_Well(self.wells, well_name)
        #print('This is the well', found_well[0].well_name)
        #well  = found_well[0]
        #found_dtst = self.get_Dataset(well, dtst_name)
        for w in self.wells:
            #print(w.well_name)
            
            if w.well_name==well_name:
                print(w.well_name + str(len(w.datasets)))
                for dtst in w.datasets:  # Iterate over a copy of the list
                    print(dtst.name)
                    w.datasets = [ds for ds in w.datasets if ds.name != dtst_name]
                    print(len(w.datasets))
                    filepath = os.path.join(self.wells_Folder,w.well_name+'.ptrc')
                    print(filepath)
                    w.serialize(filename=filepath)
                        
        if well_name=='All':
            for w in self.wells:
                for dtst in w.datasets[:]:  # Iterate over a copy of the list
                    if dtst.name == dtst_name:
                        w.datasets.remove(dtst)
                        filepath = os.path.join(self.project_folder,w.well_name+'.ptrc')
                        w.serialize(filename=filepath)
        
    def delete_Well(self, well_name):
        well_file_path = os.path.join(self.wells_Folder, well_name+'.ptrc')
        try:
            os.remove(well_file_path)
            print(f"{well_file_path} has been deleted.")
        except FileNotFoundError:
            print(f"{well_file_path} does not exist.")
        except PermissionError:
            print(f"Permission denied to delete {well_file_path}.")
        except Exception as e:
            print(f"An error occurred: {e}")
    def delete_All_Wells(self):
        #well_file_path = os.path.join(self.project_folder, well_name+'.ptrc')
        files = os.listdir(db.wells_Folder)
        ptrc_files = [f for f in files if f.endswith('.ptrc')] 
        for f in ptrc_files:
            print(f)
            las_file_path=os.path.join(db.wells_Folder,f)
            try:
                os.remove(las_file_path)
                print(f"{las_file_path} has been deleted.")
            except FileNotFoundError:
                print(f"{las_file_path} does not exist.")
            except PermissionError:
                print(f"Permission denied to delete {las_file_path}.")
            except Exception as e:
                print(f"An error occurred: {e}")
        
    def delete_Log(self, well_name, dtst_name, log_name):

        found_well = self.get_Well(self.wells, well_name)
        print('This is the well', found_well[0].well_name)
        well  = found_well[0]
        for dtst in well.datasets:
            if dtst.name == dtst_name:
                dtst.well_logs = [wl for wl in dtst.well_logs if wl.name != log_name]
        
        filepath = os.path.join(self.wells_Folder,well.well_name+'.ptrc')
        well.serialize(filename=filepath)
        
    def delete_Constant(self, well_name, const_name):

        found_well = self.get_Well(self.wells, well_name)
        print('This is the well', found_well[0].well_name)
        well  = found_well[0]
        for dtst in well.datasets:
            print(dtst.name)
            if dtst.name == 'WELL_HEADER':
                print(len(dtst.constants))
                dtst.constants = [c for c in dtst.constants if c.name != const_name]
                print(len(dtst.constants))
                
        filepath = os.path.join(self.wells_Folder,well.well_name+'.ptrc')
        print('File saved to :', filepath)
        well.serialize(filename=filepath)

    def print_Well_Dataset(self):
        print('Following wells and datasets are in th project')
        for w in self.wells:
            for dtst in w.datasets:
                print(w.well_name, dtst.name, dtst.type)
    def print_Well_HEADER_Constants(self):
        print('Following wells and datasets exist:')
        for w in self.wells:
            for dtst in w.datasets:
                if dtst.name=='WELL_HEADER':
                    consts = dtst.constants
                    for const in consts:
                        print(w.well_name, dtst.name, const.name, const.value)
    def rename_Well(self, well_name, new_well_name):
        print('Following wells and datasets exist:')
        thewell = [well for well in self.wells if well.well_name == well_name][0]
        thewell.well_name = new_well_name
        for dtst in thewell.datasets:
            dtst.wellname==new_well_name
        
        filepath = os.path.join(self.wells_Folder,thewell.well_name+'.ptrc')
        thewell.serialize(filename=filepath)
        print('Saved Wells to :', thewell.well_name, self.wells_Folder)
        print('Deleting old well', well_name)
        self.delete_Well(well_name=well_name)     
                    
    def insert_or_update_Well_HEADER_Constant(self, well_name, const_name, const_value):
        #self.Load_Wells()
        print('Following wells and datasets exist:')
        thewell = [well for well in self.wells if well.well_name == well_name][0]
        wh_dataset = [dtst for dtst in thewell.datasets if dtst.type == 'WELL_HEADER'][0]
        if const_name in [c.name for c in wh_dataset.constants]:
            #update constant value
            print(const_name)
            const = find_constant_by_name(wh_dataset,const_name)
            if const:
                const.value = const_value
            else:
                print('Constant:', const_name, ' does not exist')
        else:
            #create constant
            const = Constant(name=const_name, value=const_value)
            wh_dataset.constants.append(const)
            
        filepath = os.path.join(self.wells_Folder,thewell.well_name+'.ptrc')
        thewell.serialize(filename=filepath)
        print('Saved Wells to :', thewell.well_name, self.wells_Folder)
        
    def insert_Log(self, well_name, set_name, log_name):
        #self.Load_Wells()
        print('Following wells and datasets exist:')
        thewell = [well for well in self.wells if well.well_name == well_name][0]
        wh_dataset = [dtst for dtst in thewell.datasets if dtst.type == 'WELL_HEADER'][0]
        if log_name in [c.name for c in wh_dataset.constants]:
            #update constant value
            print(log_name)
            const = find_constant_by_name(wh_dataset,log_name)
            if const:
                const.value = log_name
            else:
                print('Constant:', log_name, ' does not exist')
        else:
            #create constant
            const = Constant(name=log_name, value=log_name)
            wh_dataset.constants.append(const)
            
        filepath = os.path.join(self.wells_Folder,thewell.well_name+'.ptrc')
        thewell.serialize(filename=filepath)
        print('Saved Wells to :', thewell.well_name, self.wells_Folder)            
    def Print_Selected_Well_Names(self):
        print('Loading wells from previously used project folder')
        # Load previously saved settings
        self.settings = QSettings('Petrocene', 'PetroceneApp')
        self.project_path = self.settings.value("project_path", "", type=str)
        project_path = self.project_path
        print('Project path from setting', project_path)
        
        self.current_well=  self.settings.value("current_well", "", type=str)
        self.current_dataset = self.settings.value("current_dataset", "", type=str)
        print(self.current_well,self.current_dataset)
        selected_well_names = json.loads(self.settings.value('selected_wells', '[]')) # Need to fix this error after aa well file is deleted
        print(selected_well_names)
        
    def remove_Selected_Well_Names(self, well_name):
        print('Loading wells from previously used project folder')
        # Load previously saved settings
        self.settings = QSettings('Petrocene', 'PetroceneApp')
        self.project_path = self.settings.value("project_path", "", type=str)
        project_path = self.project_path
        print('Project path from setting', project_path)
        
        self.current_well=  self.settings.value("current_well", "", type=str)
        self.current_dataset = self.settings.value("current_dataset", "", type=str)
        # Load selected items from settings
        selected_well_names = json.loads(self.settings.value('selected_wells', '[]')) # Need to fix this error after aa well file is deleted
        print(selected_well_names)
        mod_selected_well_names=[x for x in selected_well_names if x != well_name]
        self.settings.setValue('selected_wells', json.dumps(mod_selected_well_names))
       
    def Load_Zones(self, project_dir):
        zone_folder = os.path.join(project_dir,"ZONES_FOLDER")
        zone_file_name = 'zones_paramters.csv'
        zone_file_path = os.path.join(zone_folder, zone_file_name)
        df_param = pd.read_csv(zone_file_path) 
        return df_param  

    def export_df_to_las(self, df, well_name, dtst_name,las_file_path):
        
        las_out_folder = os.path.join(db.project_path,"data")  
        if not os.path.exists(las_out_folder):
            os.makedirs(las_out_folder)
        las_file_path = os.path.join(las_out_folder, 'result.las')

        outlas = lasio.LASFile()
        outlas.well['WELL']=lasio.HeaderItem('WELL', value=well_name)
        outlas.well['SET']=lasio.HeaderItem('SET', value=dtst_name)
        for mnem in df.columns:
            outlas.append_curve(mnemonic=mnem, data = df[mnem])
        outlas.write(las_file_path, version=2.0)

    def calc_CPI(self, sel_well, sel_dtst):
        print('Calculating CPI for well:', sel_well)
        print('Calculating CPI for Dataset:', sel_dtst)

        well = [well for well in db.wells if well.well_name == sel_well][0]
        print(well.well_name)
        datasets = well.datasets
        if sel_dtst:
            dataset = [dtst for dtst in datasets if dtst.name == sel_dtst][0]
            print('Input Dataset:', dataset.name)
        else:
            print('No Dataset selected')
        mnem_ind = dataset.index_name
        log_mnemonics = []
        for log in dataset.well_logs:
            log_mnemonics.append(log.name)
        print(log_mnemonics)
        data = {mnem:{} for mnem in log_mnemonics}
        for well_log in dataset.well_logs:
            mnem = well_log.name
            data[mnem] = well_log.log
        #Make a input curves dataframe 
        df_input = pd.DataFrame(data)
        df_param = db.Load_Zones(db.project_path)

        df_param_well = df_param[df_param['Well']==sel_well]    
        cpi_top=df_param_well['Top'].min()
        cpi_bot=df_param_well['Base'].max()

        print('Range processing:', cpi_top, cpi_bot )
        df_input.reset_index(inplace=True)
        df_input.rename(columns={'DEPT':'DEPTH'},inplace=True)
        df_input = df_input[(df_input['DEPTH'] > cpi_top) & (df_input['DEPTH'] < cpi_bot)]
        cpi = CPI()
        dfc = cpi.calc_VSHGR(df_input, df_param_well)
        print(dfc.columns)
        las_out_folder = os.path.join(db.project_path,"data")  
        if not os.path.exists(las_out_folder):
            os.makedirs(las_out_folder)
        out_las_file_path = os.path.join(las_out_folder, 'result_script.las')
        cpi.export_df_to_las(dfc, sel_well,'TESTCOMP', out_las_file_path )
    
    def load_Single_LAS_File(self, las_file_path): # Not to be used. Instead use import function in IMPEX module
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
        existing_wells = self.wells
        if wellname in [w.well_name for w in existing_wells]:
            thewell =   next((w for w in existing_wells if w.well_name == wellname), None)
            print('Well name exists:', thewell.well_name)
            thewell.datasets.append(dataset)
        else:
            #create a new well
            thewell=Well(date_created=datetime.now(), well_name=wellname, well_type='Dev')
            ref = Dataset.reference(0, bottom=bottom, dataset_name='REFERENCE', dataset_type='REFERENCE', well_name=wellname)
            thewell.datasets.append(ref)
            thewell.datasets.append(dataset)

        filepath = os.path.join(self.project_folder,thewell.well_name+'.ptrc')
        thewell.serialize(filename=filepath)
        print('Saved Wells to :', thewell.well_name, self.project_folder)
           
    def load_single_well_deviation_data_from_csv(self, dev_file_path):
        # Code to execute when button 2 is clicked
        # Check if the path points to a valid file
        if os.path.isfile(dev_file_path):
            print(dev_file_path)
        else:
            raise FileNotFoundError(f"The file at '{dev_file_path}' does not exist.")
        
        dev_df = pd.read_csv(dev_file_path, sep='\t')
        print(dev_df)
        
        wellname = dev_df['WELL'].unique()[0]
        dev_df = dev_df.drop('WELL', axis=1)
        datasetname = 'DIRECTIONAL'
        dataset = Dataset(date_created=datetime.now(),name='DIRECTIONAL', type='Point', wellname=wellname, index_name='DEPTH' )
        for col in dev_df.columns:
            print(dev_df[col])
            log = WellLog(date = datetime.now(),name=col.upper(), description='Loaded from csv',  log=dev_df[col].to_list(), dtst = dataset.name)
            dataset.well_logs.append(log)
        bottom = max(dev_df['DEPTH'])
        # 
        if wellname in [w.well_name for w in self.wells]:
            thewell =   next((w for w in self.wells if w.well_name == wellname), None)
            print('Well name exists:', thewell.well_name)
            thewell.datasets.append(dataset)

        #create a new well
        else:
            thewell=Well(date_created=datetime.now(), well_name=wellname, well_type='Dev')
            thewell.datasets.append(dataset)
            self.wells.append(thewell)
        print('Saving wells')
        folder=os.path.join(self.project_path,'')
        print('Foldeer',folder)

        filepath = os.path.join(folder,thewell.well_name+'.ptrc')
        thewell.serialize(filename=filepath)
        print('Saved Wells to :', thewell.well_name, folder)
            
    def load_multi_well_deviation_data_from_csv(self, project_dir):
        # Code to execute when button 2 is clicked
        dev_folder = os.path.join(project_dir,"DEVIATION")
        dev_file_name = 'welldeviation.csv'

        dev_file_path = os.path.join(dev_folder, dev_file_name)
        # Check if the path points to a valid file
        if os.path.isfile(dev_file_path):
            print(dev_file_path)
        else:
            raise FileNotFoundError(f"The file at '{dev_file_path}' does not exist.")
        
        dev_df = pd.read_csv(dev_file_path, sep=',', skiprows=[1])
        print(dev_df)
        
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
        print('Saving wells')
        folder=os.path.join(self.project_path,'')
        print('Foldeer',folder)
        for w in self.wells:
            print(w.well_name)
            for dtst in w.datasets:
                #print('dataset:', dtst.name)
                for wl in dtst.well_logs:
                    print('log:', wl.name)
                    #print(wl.log)
                    
            filepath = os.path.join(folder,w.well_name+'.ptrc')
            w.serialize(filename=filepath)
            print('Saved Wells to :', w.well_name, folder)
    def load_multi_well_well_header_data_from_csv(self, project_dir):
        # Code to execute when button 2 is clicked
        well_header_folder = os.path.join(project_dir,"WELL_HEADER")
        wh_file_name = 'well_header_data.csv'

        wh_file_path = os.path.join(well_header_folder, wh_file_name)
        # Check if the path points to a valid file
        if os.path.isfile(wh_file_path):
            print(wh_file_path)
        else:
            raise FileNotFoundError(f"The file at '{wh_file_path}' does not exist.")
        
        wh_df = pd.read_csv(wh_file_path, sep=',', skiprows=[1])
        print(wh_df)
        
        well_names = wh_df['WELL'].unique()
        print('Unique well names', well_names)
        for well_name in well_names:
            
            wh_df_well = wh_df[wh_df['WELL']==well_name]
            #print('Single well dataframe:', well_name, wh_df_well)
            
            datasetname = 'WELL_HEADER'
            dataset = Dataset(date_created=datetime.now(),name=datasetname, type='well_header', wellname=well_name, index_name='DEPTH' )
            wh_df_well = wh_df_well.drop('WELL', axis=1)
            for col in wh_df_well.columns:
                value=wh_df_well[col].astype(float).values[0]
                const = Constant(name=col, value = value)
                dataset.constants.append(const)
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
        print('Saving wells')
        folder=os.path.join(self.project_path,'')
        print('Foldeer',folder)
        for w in self.wells:
            filepath = os.path.join(folder,w.well_name+'.ptrc')
            w.serialize(filename=filepath)
            print('Saved Wells to :', w.well_name, folder)
            
    def Calc_TVD(self, well_name):
        #self.Load_Wells()
        well = [well for well in self.wells if well.well_name == well_name][0]
        print('Calculatting TVD for well:', well.well_name)
        ref_dtst = [dtst for dtst in well.datasets if dtst.name == 'REFERENCE'][0]
        dir_dtst = [dtst for dtst in well.datasets if dtst.name == 'DIRECTIONAL'][0]
        
        #Make dataframe of directional data
        log_mnemonics = []
        for log in dir_dtst.well_logs:
            log_mnemonics.append(log.name)
        print(log_mnemonics)
        data = {mnem:{} for mnem in log_mnemonics}
        for well_log in dir_dtst.well_logs:
            mnem = well_log.name
            data[mnem] = well_log.log
        #Make a input curves dataframe 
        df_directional = pd.DataFrame(data)
        
        ref_log = [well_log for well_log in ref_dtst.well_logs if well_log.name == 'DEPTH'][0]
        ref_depths = ref_log.log
        print(df_directional)
        
        interpolated_data = Calculate_TVD(df_directional,ref_depths)
        
        tvdlist = interpolated_data[:,0].tolist()
        tvd_formatted = [round(value,4) for value in tvdlist]
        
        devlist = interpolated_data[:,1].tolist()
        dev_formatted = [round(value,2) for value in devlist]
        
        azimlist = interpolated_data[:,2].tolist()
        azim_formatted = [round(value,2) for value in azimlist]
        
        log = WellLog(date = datetime.now(), name='TVD', description='Loaded from csv',  log=tvd_formatted, dtst = ref_dtst.name)
        ref_dtst.well_logs.append(log)
        log = WellLog(date = datetime.now(), name='DEVI', description='Loaded from csv',  log=dev_formatted, dtst = ref_dtst.name)
        ref_dtst.well_logs.append(log)
        log = WellLog(date = datetime.now(), name='AZIM', description='Loaded from csv',  log=azim_formatted, dtst = ref_dtst.name)
        ref_dtst.well_logs.append(log)
        
        folder=os.path.join(self.project_path,'')
        filepath = os.path.join(folder,well.well_name+'.ptrc')
        well.serialize(filename=filepath)
        print('Saved Wells to :', well.well_name, folder)
        print(interpolated_data)
        
    def Load_Constant(self):
        print('Loading Constant')
        
    def create_New_Project(self):
        app = QApplication(sys.argv)

        # Open a dialog to select a directory
        selected_folder = QFileDialog.getExistingDirectory(None, "Select Folder")
        if not selected_folder:
            return  # User canceled the dialog

        # Prompt user for the new folder name
        new_folder_name, ok = QInputDialog.getText(None, "New Folder Name", "Enter the new folder name:")
        if not ok or not new_folder_name.strip():
            QMessageBox.warning(None, "Warning", "Please enter a valid folder name.")
            return

        # Create the new folder path
        new_folder_path = os.path.join(selected_folder, new_folder_name.strip())

        try:
            os.makedirs(new_folder_path)
            self.settings = QSettings('Petrocene','PetroceneApp')
            print(f"Selected folder: {self.new_folder_path}")
            self.settings.setValue('project_path', self.project_path)
            QMessageBox.information(None, "Success", f"Folder '{new_folder_name}' created successfully!")
        except FileExistsError:
            QMessageBox.critical(None, "Error", "A folder with that name already exists.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"An error occurred: {e}")
            
    def open_Project(self):
        app = QApplication(sys.argv)

        # Open a dialog to select a directory
        selected_folder = QFileDialog.getExistingDirectory(None, "Select Folder")
        if not selected_folder:
            return  # User canceled the dialog
        
        #project_folder_path = os.path.join(selected_folder, '')
        self.project_path=selected_folder
        try:
            
            self.settings = QSettings('Petrocene','PetroceneApp')
            print(f"Selected folder: {self.project_path}")
            self.settings.setValue('project_path', self.project_path)
            QMessageBox.information(None, "Success", f"Folder '{self.project_path}' open successfully!")
        except FileExistsError:
            QMessageBox.critical(None, "Error", "A folder with that name already exists.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"An error occurred: {e}")
    
    def calc_CPI_DMODEL_ALL(self,well_name, dtst_name):
        print('Calculating D Model...')
        # select well from wells
        well = [well for well in self.wells if well.well_name == well_name][0] 
        
        dataset = [dtst for dtst in well.datasets if dtst.name == dtst_name][0]
        dev_dtst = [dtst for dtst in well.datasets if dtst.name == 'REFERENCE'][0] # this is from calculated REFERENCE set
        
        print(dataset.well_logs[0].name)
        #ref_dtst = [well_log for well_log in dataset.well_logs if well_log.name == 'DEPT'][0] # Output will be generated with this reference
        
        interpolated_data = InterPolate_TVD_Using_Datasets(dev_dtst,dataset)
        tvdlist = interpolated_data[:,0].tolist()
        
        log_mnemonics = []
        for log in dataset.well_logs:
            log_mnemonics.append(log.name)
        data = {mnem:{} for mnem in log_mnemonics}

        for well_log in dataset.well_logs:
            mnem = well_log.name
            data[mnem] = well_log.log
            
        df_input = pd.DataFrame(data)
        df_input['TVD']= tvdlist

        df_param = pd.read_csv(self.zone_file_path)
        df_param_well = df_param[df_param['Well']==well_name]    
        cpi_top=df_param_well['Top'].min() #2982.3 #
        cpi_bot=df_param_well['Base'].max() #3029.5 #
        
        print('Range processing:', cpi_top, cpi_bot )
        df_input.reset_index(inplace=True)
        df_input.rename(columns={'DEPT':'DEPTH'},inplace=True)
        df_input = df_input[(df_input['DEPTH'] > cpi_top) & (df_input['DEPTH'] < cpi_bot)]
        
        cpi= CPI()
        dfc = cpi.calc_GR_RHOB_NPHI_RES(df_input, df_param_well)
        las_out_folder = os.path.join(self.project_path,"data")  
        if not os.path.exists(las_out_folder):
            os.makedirs(las_out_folder)
        las_file_path = os.path.join(las_out_folder, well.well_name+'-CPI-GR-DEN.las')
        set_name = 'PYGR'
        impex = DataIMPEX()
        impex.export_df_to_las(dfc, well.well_name, set_name, las_file_path)
        
    def calc_CPI_VOLUMES_OPTIMIZER(self,well_name, dtst_name):
        print('Calculating Volume Optimize Model...')
        # select well from wells
        well = [well for well in self.wells if well.well_name == well_name][0] 
        
        dataset = [dtst for dtst in well.datasets if dtst.name == dtst_name][0]
        dev_dtst = [dtst for dtst in well.datasets if dtst.name == 'REFERENCE'][0] # this is from calculated REFERENCE set
        
        print(dataset.well_logs[0].name)
        #ref_dtst = [well_log for well_log in dataset.well_logs if well_log.name == 'DEPT'][0] # Output will be generated with this reference
        
        interpolated_data = InterPolate_TVD_Using_Datasets(dev_dtst,dataset)
        tvdlist = interpolated_data[:,0].tolist()
        
        log_mnemonics = []
        for log in dataset.well_logs:
            log_mnemonics.append(log.name)
        data = {mnem:{} for mnem in log_mnemonics}

        for well_log in dataset.well_logs:
            mnem = well_log.name
            data[mnem] = well_log.log
            
        df_input = pd.DataFrame(data)
        df_input['TVD']= tvdlist

        df_param = pd.read_csv(self.zone_file_path)
        df_param_well = df_param[df_param['Well']==well_name]    
        cpi_top=df_param_well['Top'].min() #2982.3 #
        cpi_bot=df_param_well['Base'].max() #3029.5 #
        
        print('Range processing:', cpi_top, cpi_bot )
        df_input.reset_index(inplace=True)
        df_input.rename(columns={'DEPT':'DEPTH'},inplace=True)
        df_input = df_input[(df_input['DEPTH'] > cpi_top) & (df_input['DEPTH'] < cpi_bot)]
        
        cpi= CPI()
        dfc_vol_opt = cpi.calc_Volume_Optimize(df_input,df_param_well)
        las_out_folder = os.path.join(self.project_path,"data")  
        if not os.path.exists(las_out_folder):
            os.makedirs(las_out_folder)
        las_file_path = os.path.join(las_out_folder, well.well_name+'-CPI-VOL_OPT.las')
        set_name = 'VOL_OPT'
        impex = DataIMPEX()
        impex.export_df_to_las(dfc_vol_opt, well.well_name, set_name, las_file_path)


                                                                 #Project creation, open
# base_folder = r"C:\Petrocene_Projects" 
# project_name = 'PSM'
# pm = ProjectManager()
# pm.create_project(base_folder=base_folder, project_name=project_name)
# pm.get_project_path()
db = DatabaseQuery()
#db.create_New_Project()
#db.open_Project()

#sel_well = db.current_well
#sel_dtst = 'SPLICE' #db.current_dataset

#load commands
db.Load_Wells()
impex = DataIMPEX(db.wells)
#kv = KeyValueStore(db.alias_file_path)
#li = ItemCollection(db.log_info_file_path)


                                                                            # Manage Tops Data
# excel_file_path = os.path.join(r"C:\Oil\Karjisan\01-Output",r'KARJISAN Data Acquisition Summary.xlsx')
# impex.load_single_well_tops_data_from_excel(excel_file_path,'Tops', 'KJ-07')
                                                                            # Manage Deviation Data
#db.load_deviation_data_from_csv(project_dir=db.project_path)
#db.load_multi_well_deviation_data_from_csv(project_dir=db.project_path)
# excel_file_path = os.path.join(r"C:\Oil\Karjisan\01-Output",r'KARJISAN Data Acquisition Summary.xlsx')
#impex.load_single_well_deviation_data_from_excel(excel_file_path, 'Deviation Data','KJ-10')
# impex.load_multi_well_deviation_data_from_excel(excel_file_path, 'Deviation Data')
# dev_filepath =  os.path.join(r'C:\Oil\Gandhar\Well DEV\OutFiles', 'G-026_dev.txt')
# db.load_single_well_deviation_data_from_csv(dev_filepath)
# dataimpex = DataIMPEX(db.project_folder)
# dev_filepath =  os.path.join(r'C:\Oil\Gandhar\Well DEV\OutFiles', 'G-026_dev.txt')
# db.load_single_well_deviation_data_from_csv(dev_filepath)
# dataimpex = DataIMPEX(db.project_folder)
                                                                            # Import LAS files
las_file_path = os.path.join(r'C:\ProgramData\Paradigm\projects\KARJISAN\data', 'kj-1_splice.las')
impex.import_Single_LAS_File(las_file_path)                                                                         
# las_Folder = db.input_las_Folder
# impex.load_multi_well_las_files_from_folder(las_Folder=las_Folder)

                                                                            # Manage Well header
#db.load_multi_well_well_header_data_from_csv(project_dir=db.project_path)                                                           
# db.insert_or_update_Well_HEADER_Constant('KJ-10', 'Well_Profile', 'Inclined')
# db.insert_or_update_Well_HEADER_Constant('KJ-01', 'KB', 86.04)
# db.insert_or_update_Well_HEADER_Constant('KJ-02', 'Date_Spud', '21-12-2008')
# db.insert_or_update_Well_HEADER_Constant('KJ-02', 'Date_Spud', '21-12-2008')
# excel_file_path = os.path.join(r"C:\Oil\Karjisan\01-Output",r'KARJISAN Data Acquisition Summary.xlsx')
# impex.insert_Constants_From_Well_Information(excel_file_path, 'Well Info')

                                                                            # Print Commands
# Print Commands
# print(len(db.wells))            
# db.print_Well_Dataset()
# db.print_Well_Dataset()
# db.print_Well_HEADER_Constants()
# db.Print_Selected_Well_Names()
                                                                            # Generate Report

# er= ExcelReport(db.wells)
# er.collect_data(['Td'])
# er.save_to_excel(output_file=db.output_file_path)

                                                                            #delete/remove/rename commands
#delete/remove commands
#db.remove_Selected_Well_Names('G-022')
#db.delete_Log('G-023', 'REFERENCE', 'TVD')
# db.delete_Dataset('KJ-06', 'TOPS')
# db.delete_Constant('KJ-06', 'Td') # delete constant by name in all wells
# db.delete_Well('KJ-03')
# db.delete_All_Wells()
# db.rename_Well('KJ-1', 'KJ-01') 
                                                                            #calculate commands
#calculate commands
# db.Calc_TVD('G-026')   # Should run after a LAS file is loaded\
                        # and deviation survey loaded
#db.calc_CPI_DMODEL_ALL('G-026', 'SPLICE')
#db.calc_CPI_VOLUMES_OPTIMIZER('G-026', 'SPLICE')
                                                                            # Manage alias file

#kv.add_key('DEPTH')
#kv.add_values_to_key('SWE','SWE')
#kv.delete_key('SWE')
#kv.update_file()
#kv.print_data()SER
#kv.contains_key('WSID')
#print(kv.list_keys())
#print(kv.get_values('VSH'))
                                                                            # Manage log_info file

#li.create_and_add_item('DEPTH', 'Depth Index', 'Linear', 'm', 0, 100.0, 'Depth index')
#li.create_and_add_item('SW', 'Water Saturation', 'Linear', 'v/v', 1.0, 0.0, 'Water saturation calculated Indoanesia equation')
#li.create_and_add_item('PHIE', 'Porosity', 'Linear', 'v/v', 0.5, 0.0, 'Effective porosity deom density log with shale correction')
#li.create_and_add_item('RHOB_FIN', 'Density', 'Linear', 'v/v', 1.8, 2.8, 'Bulk density corrected in washout section')
#print(li.get_attribute_by_item_name('SWE', 'unit'))
#print(li.list_items())

                                                                            # Manage Mineral
#mp = Minerals()
#mp.print_minerals()
# Adding minerals (Example)
#quartz = Mineral("Quartz")
#mp.add_mineral(quartz)
#calcite = Mineral("Calcite")
#mp.add_property_to_mineral('Quartz', 'GR', 20)
#mp.save_to_csv()

                                                                            # Utility Function
# tops_file_name = 'KARJISAN_TOPS.xlsx'
# sheet_name = 'TOPS'
# tops_file_path = os.path.join(db.tops_Folder,tops_file_name)
# zones_file_name = 'KARJISAN_ZONES.csv'
# zones_file_path = os.path.join(db.zones_Folder,zones_file_name)
# Convert_Geolog_Tops_Excel_To_Param_Tops_csv(tops_file_path, sheet_name=sheet_name, param_file_path=zones_file_path)


                                                                            #Database Creation Work Flow
#1
# create an new project
# base_folder = r"C:\Petrocene_Projects" 
# project_name = 'Karjisan'
# pm = ProjectManager()
# pm.create_project(base_folder=base_folder, project_name=project_name)
# #2 
# create wells by importing LAS files from a folder
# las_Folder = db.input_las_Folder
# impex.load_multi_well_las_files_from_folder(las_Folder=las_Folder)
# # 3
# import WELL_HEADER constant
# excel_file_path = os.path.join(db.well_header_Folder,'KARJISAN Data Acquisition Summary.xlsx')
# impex.insert_Constants_From_Well_Information(excel_file_path, 'Well Info')
# # # # 4
# if well constant INCL in well header is no, create  2 row DIRECTIONAL dataset [0,0],[0,TD]
#5
# Load DIRECTIONA dataset in all the wells
# allowed_headers = ['well','depth', 'azim','inc','ang','WELL','dev','md']
# dev_mnemonics = ['WELL','DEPTH', 'DEVI', 'AZIM']
# excel_file_path = os.path.join(db.deviation_Folder,r'KARJISAN Data Acquisition Summary.xlsx')
# impex.load_multi_well_deviation_data_from_excel(excel_file_path, 'Deviation Data',allowed_headers,dev_mnemonics)
#6
# Load Zones Dataset 
# excel_file_path = os.path.join(db.zones_Folder,r'KARJISAN_ZONES.xlsx')
# impex.load_multi_well_zone_data_from_excel(excel_file_path, 'Deviation Data')
#7
# Calculate TVDSS
# 8
# Display log plot


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
    
#     well = [well for well in db.wells if well.well_name == db.current_well][0]
#     print(well.well_name)
#     datasets = well.datasets
#     dtst=None
#     if db.current_dataset:
#         dtst = [dtst for dtst in datasets if dtst.name == db.current_dataset][0]
#         print('Input Dataset:', dtst.name)
#     else:
#         print('No Dataset selected')
    
#     main_win = MainWindow(well, dtst)
#     main_win.show()
#     sys.exit(app.exec_())

#8 
# Calculate CPI
#9
# Calculate Averages
#10
# Calculate Sensitivity
#11
# Make averageshiatogram and plots
#12
# # Make report for well constants
# output_pdf_file_path = os.path.join(db.output_Folder,'Well_summary.pdf')
# er= ExcelReport(db.wells)
# const_list = ['WELL','DATE SPUD', 'KB', 'TD', 'WELL COURSE','INCL','MUD', 'STATUS','WFT','CONV CORE']
# er.collect_data(const_list)
# er.save_to_excel(output_file=db.output_file_path,const_list=const_list)
# er.save_to_pdf(output_file=output_pdf_file_path,const_list=const_list)