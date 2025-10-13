import sys,os
sys.path.append(os.path.abspath(os.path.join('..', 'petrocene')))

import lasio
import math
from pathlib import Path
import pandas as pd
from Utilities.utilities1 import *
#from LOGPLOTS.DEN_NEU_PLOT import *
import matplotlib.pyplot as plt
import numpy as np
from volume_optimizer import *
from minerals import *

class CPI:
    def __init__(self):
        self.title = ''


    def calcCPI_Direct(self, lasFileName,lasFolder, tops_folder,cpi_Folder):
        print("in Direct")
        param_filename = "tops_paramters.csv"
        lasfilepath = os.path.join(lasFolder,lasFileName)
        paramfilepath = os.path.join(tops_folder,param_filename)
        #print(lasfilepath)
        las = lasio.read(lasfilepath)
        well = las.well.WELL.value
        #print(well)
        #for count, curve in enumerate(las.curves):
            #print(f"Curve: {curve.mnemonic}, Units: {curve.unit}, Description: {curve.descr}")
        #print(f"There are a total of: {count+1} curves present within this file")
        print(paramfilepath)
        df_param = pd.read_csv(paramfilepath)

        df_param_well = df_param[df_param['Well']==well]
        #print(df_param_well.head)
        
        #print(df_param_well['Top'].min())
        #print(df_param_well['Top'].max())
        #print(df_param_well.Zone.unique())
        
        cpi_top=df_param_well['Top'].min()
        cpi_bot=df_param_well['Top'].max()

        df_cpi=las.df()
        df_cpi.reset_index(inplace=True)
        df_cpi.rename(columns={'DEPT':'DEPTH'},inplace=True)
        #print('df_cpi')
        #print(df_cpi.head(10))
        
        df_input = df_cpi[(df_cpi['DEPTH'] > cpi_top) & (df_cpi['DEPTH'] < cpi_bot)]
        #print('df-input')
        #print(df_input.head(10))

        
        #df_vshgr=calc_VSHGR(df_input,df_param_well)
        #df_rhob_calc=calc_RHOB_CALC(df_input,df_param_well)
        df_calc = self.calc_VSHGR(df_input,df_param_well)
        #print(df_calc.info())
        outlas = lasio.LASFile()
        outlas.well['WELL']=lasio.HeaderItem('WELL', value=well)
        outlas.well['SET']=lasio.HeaderItem('SET', value='PYTH')
        #print(outlas.header)
        

        outlas.append_curve(mnemonic='DEPTH',data=df_calc['DEPTH'],unit='m',descr='Depth')
        outlas.append_curve(mnemonic='VSHGR',data=df_calc['VSHGR'],unit='v/v',descr='Shale Volume computed using GR')
        outlas.append_curve(mnemonic='RHOB_CALC',data=df_calc['RHOB_CALC'],unit='g/cc',descr='Calculated Bulk density')
        outlas.append_curve(mnemonic='NPHI_CALC',data=df_calc['NPHI_CALC'],unit='v/v',descr='Calculated Neutron Porosity')
        outlas.append_curve(mnemonic='PHIE',data=df_calc['PHIE'],unit='v/v',descr='Effective Porosity')
        outlas.append_curve(mnemonic='SWE',data=df_calc['SWE'],unit='v/v',descr='Water saturation')
        outlas.append_curve(mnemonic='VOL_UWAT',data=df_calc['VOL_UWAT'],unit='v/v',descr='Volume of Water')
        outlas.append_curve(mnemonic='PHIE_ITER',data=df_calc['PHIE_ITER'],unit='v/v',descr='Effective Porosity by iterative mwthod')
        outlas.append_curve(mnemonic='SWE_ITER',data=df_calc['SWE_ITER'],unit='v/v',descr='Water saturation by iterative method')
        outlas.append_curve(mnemonic='RHOBHC',data=df_calc['RHOBHC'],unit='g/cc',descr='Hydrocarbon corrected bulk density')
        
        outputFolder=cpi_Folder
        print(outputFolder)
        if not os.path.exists(outputFolder):
            os.makedirs(outputFolder)
        lasfilepath_out = os.path.join(outputFolder,lasFileName)
        dfout = outlas.df()
        #print(dfout.info())
        #templ=''
        #ShowPlot2(templ, dfout, outputFolder,well)
        
        #plot_example(dfout,outputFolder,well)
        outlas.write(lasfilepath_out, version=2.0)
        #print(df['VSHGR'])
        print('File Saved')
        
    def calcCPI(self, las_File_Path,zones_File_Path,cpi_Folder):
        print("in CPI")


        #print(lasfilepath)
        las = lasio.read(las_File_Path)
        well = las.well.WELL.value
        #print(well)
        #for count, curve in enumerate(las.curves):
            #print(f"Curve: {curve.mnemonic}, Units: {curve.unit}, Description: {curve.descr}")
        #print(f"There are a total of: {count+1} curves present within this file")
        print(zones_File_Path)
        df_param = pd.read_csv(zones_File_Path)

        df_param_well = df_param[df_param['Well']==well]
        #print(df_param_well.head)
        
        #print(df_param_well['Top'].min())
        #print(df_param_well['Top'].max())
        #print(df_param_well.Zone.unique())
        
        cpi_top=df_param_well['Top'].min()
        cpi_bot=df_param_well['Top'].max()

        df_cpi=las.df()
        df_cpi.reset_index(inplace=True)
        df_cpi.rename(columns={'DEPT':'DEPTH'},inplace=True)
        #print('df_cpi')
        #print(df_cpi.head(10))
        
        df_input = df_cpi[(df_cpi['DEPTH'] > cpi_top) & (df_cpi['DEPTH'] < cpi_bot)]
        #print('df-input')
        #print(df_input.head(10))

        
        #df_vshgr=calc_VSHGR(df_input,df_param_well)
        #df_rhob_calc=calc_RHOB_CALC(df_input,df_param_well)
        df_calc = self.calc_VSHGR(df_input,df_param_well)
        #print(df_calc.info())
        outlas = lasio.LASFile()
        outlas.well['WELL']=lasio.HeaderItem('WELL', value=well)
        outlas.well['SET']=lasio.HeaderItem('SET', value='PYTH')
        #print(outlas.header)
        

        outlas.append_curve(mnemonic='DEPTH',data=df_calc['DEPTH'],unit='m',descr='Depth')
        outlas.append_curve(mnemonic='VSHGR',data=df_calc['VSHGR'],unit='v/v',descr='Shale Volume computed using GR')
        outlas.append_curve(mnemonic='RHOB_CALC',data=df_calc['RHOB_CALC'],unit='g/cc',descr='Calculated Bulk density')
        outlas.append_curve(mnemonic='NPHI_CALC',data=df_calc['NPHI_CALC'],unit='v/v',descr='Calculated Neutron Porosity')
        outlas.append_curve(mnemonic='PHIE',data=df_calc['PHIE'],unit='v/v',descr='Effective Porosity')
        outlas.append_curve(mnemonic='SWE',data=df_calc['SWE'],unit='v/v',descr='Water saturation')
        outlas.append_curve(mnemonic='VOL_UWAT',data=df_calc['VOL_UWAT'],unit='v/v',descr='Volume of Water')
        outlas.append_curve(mnemonic='PHIE_ITER',data=df_calc['PHIE_ITER'],unit='v/v',descr='Effective Porosity by iterative mwthod')
        outlas.append_curve(mnemonic='SWE_ITER',data=df_calc['SWE_ITER'],unit='v/v',descr='Water saturation by iterative method')
        outlas.append_curve(mnemonic='RHOBHC',data=df_calc['RHOBHC'],unit='g/cc',descr='Hydrocarbon corrected bulk density')
        outlas.append_curve(mnemonic='RHOB',data=df_calc['RHOB'],unit='g/cc',descr='bulk density used')
        
        outputFolder=cpi_Folder
        print(outputFolder)
        if not os.path.exists(outputFolder):
            os.makedirs(outputFolder)
        lasFileName=well+'_SPLICE_VSHGR.las'
        lasfilepath_out = os.path.join(outputFolder,lasFileName)
        dfout = outlas.df()
        #print(dfout.info())
        #templ=''
        #ShowPlot2(templ, dfout, outputFolder,well)
        
        #plot_example(dfout,outputFolder,well)
        outlas.write(lasfilepath_out, version=2.0)
        #print(df['VSHGR'])
        print('File Saved')
            
    def get_param(self, depth_series, param, df_params):
        # Check if depth_series is indeed a Series
        if not isinstance(depth_series, pd.Series):
            raise ValueError("depth_series must be a pandas Series")

        # Create a boolean mask for filtering based on depth
        mask = (depth_series.values[:, None] >= df_params['Top'].values) & \
            (depth_series.values[:, None] < df_params['Base'].values)

        # Use the mask to get values for each depth
        result_values = []

        for i in range(len(depth_series)):
            # Get matching rows for the current depth
            matching_rows = df_params.loc[mask[i]]
            
            if not matching_rows.empty:
                result_values.append(matching_rows[param].iloc[0])  # Get the first match
            else:
                result_values.append(None)  # No match found

        return pd.Series(result_values)  # Return results as a Series

    def calc_VSHGR(self,df, df_param_well):
        dfc=pd.DataFrame()
        print('Log data inside calcVSH module', df.columns)
        
        for ind in df.index:
            depth=df['DEPTH'][ind]
            #print(depth)
            gr_min = self.get_param(depth,'GR_MIN', df_param_well)
            gr_max = self.get_param(depth,'GR_MAX', df_param_well)
            rw=self.get_param(depth,'RWS', df_param_well)
            #print(depth, df['GR'], gr_min, gr_max)
            vshgr = (df['GR']-gr_min)/(gr_max-gr_min)
            
            rhosh=2.25
            rhomat = 2.64
            rhob_fluid=1
            rhomf=1
            rhohc=0.8
            nphi_sh=0.54
            nphi_mat = -0.04
            nphi_fluid=1
            por_sand=0.25
            salm=10000
            excavf=1.3
            
            a=1
            rmf=0.6
            rtsh=3
            m=1.8
            n=2
            #print("vshgr %s rhosh %s por_sand %s: " %(vshgr,rhosh,por_sand))
            rhob_calc=vshgr*rhosh+(1-vshgr)*((1-por_sand)*rhomat +por_sand*rhob_fluid)
            nphi_calc=vshgr*nphi_sh+(1-vshgr)*((1-por_sand)*nphi_mat +por_sand*nphi_fluid)
            phit=(rhomat-rhob_calc)/(rhomat-rhob_fluid)
            phie=phit-vshgr*0.24
            
            
            #nom=a*rw
            #denom = df['LLD']*pow(phie,m)
            rhob=df['RHOB'][ind]
            swe = self.sw_indonesia(a,m,n,vshgr,phie,df['LLD'],rtsh,rw)
            phie_iter, swe_iter, rhobhc=self.sw_indonesia_iter(a,m,n,vshgr, df['RHOB'], df['NPHI'], rhomf, rhohc, rhomat, rhosh, salm,excavf, df['LLD'], rtsh,rmf)
            swe_iter_limited=np.minimum(swe_iter,1)
            #swe=pow(nom/denom,1/n)
            swe_limited = np.minimum(swe,1)
            vol_uwat=phie*swe_limited
            dfc['DEPTH']=df['DEPTH']
            dfc['RHOB']=df['RHOB']
            dfc['VSHGR']=np.minimum(vshgr,1)
            dfc['RHOB_CALC']=rhob_calc
            dfc['NPHI_CALC']=nphi_calc
            dfc['PHIE']=phie
            dfc['SWE']=swe_limited
            dfc['PHIE_ITER']=phie_iter
            dfc['SWE_ITER']=swe_iter_limited
            dfc['VOL_UWAT']=vol_uwat
            dfc['RHOBHC']=rhobhc
            
        return dfc
    def calc_GR_RHOB_NPHI_RES(self,df, df_param_well):
        dfc=pd.DataFrame()
        print('Log data inside calc_GR_RHOB_NPHI_RES module', df.columns)
        depth=df['DEPTH']
        tvd = df['TVD']
        rhob=df['RHOB'].to_numpy()
        nphi = df['NPHI'].to_numpy()
        
        #print(depth)
        gr_min = self.get_param(df['DEPTH'],'GR_MIN', df_param_well).to_numpy()
        gr_max = self.get_param(df['DEPTH'],'GR_MAX', df_param_well).to_numpy()
        tvdsstop = self.get_param(df['DEPTH'],'TVDSSTOP', df_param_well).to_numpy()
        rhobshtop = self.get_param(df['DEPTH'],'RHOBSHTOP', df_param_well).to_numpy()
        rhobshgrad = self.get_param(df['DEPTH'],'RHOBSHGRAD', df_param_well).to_numpy()
        nphishtop = self.get_param(df['DEPTH'],'NPHISHTOP', df_param_well).to_numpy()
        nphishgrad = self.get_param(df['DEPTH'],'NPHISHGRAD', df_param_well).to_numpy()
        por_sand = self.get_param(df['DEPTH'],'POR_SAND', df_param_well).to_numpy()
        
        rho_fluid = self.get_param(df['DEPTH'],'RHO_FLUID', df_param_well).to_numpy()
        rho_mat = self.get_param(df['DEPTH'],'RHO_MAT', df_param_well).to_numpy()
        nphi_fluid = self.get_param(df['DEPTH'],'RHO_FLUID', df_param_well).to_numpy()
        nphi_mat = self.get_param(df['DEPTH'],'NPHI_MAT', df_param_well).to_numpy()
        rho_dsh = self.get_param(df['DEPTH'],'RHO_DSH', df_param_well).to_numpy()
        rho_mf = self.get_param(df['DEPTH'],'RHO_MF', df_param_well).to_numpy()
        rho_hc = self.get_param(df['DEPTH'],'RHO_HC', df_param_well).to_numpy()
        #salm = self.get_param(df['DEPTH'],'RHO_DSH', df_param_well).to_numpy()
        salm = 10000
        excavf = self.get_param(df['DEPTH'],'EXCAVF', df_param_well).to_numpy()
        rt_sh = self.get_param(df['DEPTH'],'RT_SH', df_param_well).to_numpy()
        rmf = self.get_param(df['DEPTH'],'RMF', df_param_well).to_numpy()
        rws = self.get_param(df['DEPTH'],'RWS', df_param_well).to_numpy()
        a = self.get_param(df['DEPTH'],'A', df_param_well).to_numpy()
        m = self.get_param(df['DEPTH'],'M_C', df_param_well).to_numpy()
        n = self.get_param(df['DEPTH'],'N', df_param_well).to_numpy()

       
        vshgr=(df['GR']-gr_min)/(gr_max-gr_min)
        vshgr_limited = np.clip(vshgr, 0,1)
        
        rhob_sh = rhobshtop + (tvd-tvdsstop)*rhobshgrad/1000
        nphi_sh = nphishtop - (tvd-tvdsstop)*nphishgrad/1000
        
        
        #print("vshgr %s rhosh %s por_sand %s: " %(vshgr,rhosh,por_sand))
        rhob_calc=vshgr*rhob_sh+(1-vshgr)*((1-por_sand)*rho_mat +por_sand*rho_fluid)
        nphi_calc=vshgr*nphi_sh+(1-vshgr)*((1-por_sand)*nphi_mat +por_sand*nphi_fluid)
        phit=(rho_mat-rhob_calc)/(rho_mat-rho_fluid)
        phit_sh = (rho_dsh-rhob_sh)/(rho_dsh-rho_fluid)
        #phie=phit-vshgr*por_sand
        
        rhob_fin = np.where((rhob > rhob_calc),rhob,rhob_calc)

        rt = df['LLD']
        phie, swe, rhobhc, nphihc=self.sw_indonesia_iter(a,m,n,vshgr_limited,rhob_fin,nphi, rho_mf, rho_hc, rho_mat, rhob_sh, salm,excavf, rt, rt_sh,rws)
        phie_limited = np.clip(phie, 0, 0.5)
        swe_limited=np.clip(swe,0, 1)
        
        dfc['DEPTH']=depth
        dfc['RHOBSH']=rhob_sh
        dfc['NPHISH']=nphi_sh
        dfc['VSHGR'] = vshgr_limited
        dfc['RHOB_CALC']=rhob_calc
        dfc['RHOB_FIN'] = rhob_fin 
        dfc['PHIT_SH'] = phit_sh
        dfc['PHIE']=phie_limited
        dfc['SWE']=swe_limited
        dfc['RHOBC'] = rhobhc
        dfc['NPHIC'] = nphihc
        
        #dfc['VOL_WATER'] = phie_limited*(1-swe_limited)
        
        #print(phie_limited, swe_limited)
        
        
        return dfc

    def calc_Volume_Optimize(self,df, df_param_well):
        
        
        quartz = [15, -0.04, 2.65]
        water = [0, 1, 1]
        clay = [110, 0.5, 2.58]
        characteristic_values = np.array([quartz, water, clay]).T
        
        # Create a DataFrame with target values and uncertainty ranges for each target
        target_values = df['DEPTH']
        uncertainty_value_1 = 5
        uncertainty_value_2 = 0.02
        uncertainty_value_3 = 0.02
        
        # Create a DataFrame with target values and uncertainty ranges for each target
        data = {
            'DEPTH':df['DEPTH'],
            'target_1': df['GR'],
            'target_2': df['NPHI'],
            'target_3': df['RHOB'],
            'uncertainty_1': [uncertainty_value_1] * len(target_values),  # Uncertainty for target 1
            'uncertainty_2': [uncertainty_value_2] *len(target_values), # Uncertainty for target 2
            'uncertainty_3': [uncertainty_value_3] *len(target_values), # Uncertainty for target 3
        }
        
        df = pd.DataFrame(data)

        # Initialize the optimizer
        optimizer = VolumeOptimizer(characteristic_values)

        # Calculate volumes and reconstructed targets
        result_df = optimizer.calculate_volumes_from_df(df)

        # Display results
        print(result_df)
        return result_df

    def convert_Tops_To_Param():
        lasFolder='C:/Oil/Gandhar/LASDIROUT'
        tops_filename = "tops_geolog.csv"
        param_filename = "tops_paramters.csv"
        Convert_Geolog_Tops_To_Param_Tops(lasFolder,tops_filename,param_filename)

    def ShowPlot(templ, df):
        (fig,axes) = plt.subplots(figsize = (10,20))
        plt.tick_labels=None
        curve_names = ["GR","LLD","RHOB","NPHI"]
        ax1 = plt.subplot2grid((1,4),(0,0),rowspan=1,colspan=1)
        ax2 = plt.subplot2grid((1,4),(0,1),rowspan=1,colspan=1)
        ax3 = plt.subplot2grid((1,4),(0,2),rowspan=1,colspan=1)
        
        ax4 = ax3.twiny()
        ax5 = plt.subplot2grid((1,4),(0,2),rowspan=1,colspan=1)
        
        
        ax1.plot('GR','DEPTH', data=df, color='green', lw=0.5)
        ax1.set_xlim(0,150)
        ax1.set_xlabel(curve_names[0])
        ax1.xaxis.set_ticks_position("top")
        ax1.xaxis.set_label_position("top")
        ax1.grid()
        
        ax2.plot('LLD','DEPTH',data=df, color='red')
        ax2.set_xlim(0.2,2000)
        ax2.set_xlabel(curve_names[1])
        ax2.xaxis.set_ticks_position("top")
        ax2.xaxis.set_label_position("top")
        ax2.semilogx()
        ax2.grid()

        ax3.plot('RHOB','DEPTH',data=df, color='red')
        ax3.set_xlim(1.65,2.65)
        ax3.set_xlabel(curve_names[2])
        ax3.xaxis.set_ticks_position("top")
        ax3.xaxis.set_label_position("top")
        ax3.grid() 
        
        ax4.plot('NPHI','DEPTH',data=df, color='blue')
        ax4.set_xlim(0.6,0)
        ax4.set_xlabel(curve_names[3])
        ax4.spines["top"].set_position(("axes",1.08))
        
        ax5.plot('VSHGR','DEPTH',data=df, color='black')
        ax5.set_xlim(0,1)
        ax5.set_xlabel(curve_names[2])
        ax5.xaxis.set_ticks_position("top")
        ax5.xaxis.set_label_position("top")
        ax5.grid() 
        

        for ax in [ax2,ax3]:
            plt.setp(ax.get_yticklabels(),visible = False)
            
        fig.subplots_adjust(wspace=0.04)
        
        plt.show()
    def ShowPlot2(templ, df,dir,well):
        df.reset_index(inplace=True)
        
        cpi_top=df['DEPTH'].min()
        cpi_bot=df['DEPTH'].max()
        
        
        curve_names = ["VSHGR","LLD","RHOB","NPHI"]
        fig, (ax1,ax2) = plt.subplots(nrows=1,ncols=2,figsize=(5,10))

        ax1.plot('VSHGR','DEPTH', data=df, color='green', lw=0.5)
        ax1.set_xlim(0,1)
        ax1.set_ylim(cpi_bot,cpi_top)
        ax1.set_xlabel(curve_names[0])
        ax1.xaxis.set_ticks_position("top")
        ax1.xaxis.set_label_position("top")
        ax1.grid()
        
        ax2.plot('RHOB_CALC','DEPTH', data=df, color='red', lw=0.5)
        ax2.set_xlim(1.65,2.65)
        ax2.set_ylim(cpi_bot,cpi_top)
        ax2.set_xlabel(curve_names[0])
        ax2.xaxis.set_ticks_position("top")
        ax2.xaxis.set_label_position("top")
        ax2.grid()
        
        ax3=ax2.twiny()
        ax3.plot('NPHI_CALC','DEPTH', data=df, color='blue', lw=0.5, linestyle='dashed')
        ax3.set_xlim(0.6,0.0)
        ax3.set_ylim(cpi_bot,cpi_top)
        ax3.set_xlabel(curve_names[0])
        ax3.xaxis.set_ticks_position("top")
        ax3.xaxis.set_label_position("top")
        ax3.grid()
        
        for ax in [ax2]:
            plt.setp(ax.get_yticklabels(),visible = False)
            
        # fill between y=0.75 and df.y
        ax2.fill_between(df['DEPTH'], df['RHOB_CALC'], 3,interpolate=True)
        ax3.fill_between(df['DEPTH'], df['RHOB_CALC'], 3,interpolate=True)
        
        plt.suptitle(well)    
        fig.subplots_adjust(wspace=0.08)
        #plt.show()
        print('this is out directory')
        print(dir)
        plotfilepath_out = os.path.join(dir,'cpi.jpg')
        plt.savefig(plotfilepath_out)
        
    def plot_example(df,dir,well):
        df.reset_index(inplace=True)
        cpi_top=df['DEPTH'].min()
        cpi_bot=df['DEPTH'].max()
        x = np.arange(0.0, 2, 0.01)
        y1 = np.sin(2 * np.pi * x)
        y2 = 0.8 * np.sin(4 * np.pi * x)
        
        fig, (ax1, ax2, ax3, ax4, ax5,ax6) = plt.subplots(
        1, 6, sharey=True, figsize=(8, 10))
        
        
        ax1.plot(df['VSHGR'],df['DEPTH'], lw=2, label='mean population 1')
        ax1.fill_betweenx(df['DEPTH'], 0, df['VSHGR'], facecolor='green')
        ax1.fill_betweenx(df['DEPTH'],  df['VSHGR'],1, df['VSHGR'], facecolor='yellow')
        ax1.set_title('VSHGR')
        ax1.set_xlim(0,1)
        ax1.set_ylim(cpi_bot,cpi_top)
        
        
        ax2.plot(df['RHOB_CALC'], df['DEPTH'], lw=0.5, label='mean population 1',color='red')
        #ax2.plot(df['NPHI_CALC'],df['DEPTH'], lw=0.5, label='mean population 1',color='blue', linestyle='dashed')
        ax2.set_title('RHOB_CALC')
        ax2.set_xlim(1.65,2.65)
        ax2.set_ylim(cpi_bot,cpi_top)
        
        ax3=ax2.twiny()
        ax3.plot(df['NPHI_CALC'],df['DEPTH'], lw=0.5, label='mean population 1',color='blue', linestyle='dashed')
        ax3.set_xlabel('NPHI_CALC')
        ax3.set_xlim(0.6,0)
        nphi_scaled = (2.65-df['RHOB_CALC'])/1.65
        
        plt.fill_betweenx(df['DEPTH'], df['NPHI_CALC'], nphi_scaled,  nphi_scaled<df['NPHI_CALC'], facecolor='green')
        plt.fill_betweenx(df['DEPTH'], nphi_scaled, df['NPHI_CALC'],  nphi_scaled>df['NPHI_CALC'], facecolor='red')
        
        ax4.plot(df['PHIE'], df['DEPTH'], lw=0.5, label='phie',color='red')
        ax4.set_title('PHIE')
        ax4.set_xlim(0.5,0)
        ax4.set_ylim(cpi_bot,cpi_top)
        
        ax5.plot(df['SWE'], df['DEPTH'], lw=0.5, label='swe',color='black')
        ax5.set_title('SWE')
        ax5.set_xlim(1,0)
        ax5.set_ylim(cpi_bot,cpi_top)
        
        ax6=ax4.twiny()
        ax6.plot(df['VOL_UWAT'], df['DEPTH'], lw=0.5, label='swe',color='black')
        ax6.set_title('VOL_UWAT')
        ax6.set_xlim(0.5,0)
        ax6.set_ylim(cpi_bot,cpi_top)
        
        fig.tight_layout()
        plt.suptitle(well)
        #plt.show()
        plotfilepath_out = os.path.join(dir,well+'-cpi.jpg')
        plt.savefig(plotfilepath_out)

    def sw_indonesia(self,A,M,N,vsh, phie, rt, rtsh,flures):
        # Calculate Indonesia Saturation
        ff = A / phie**M
        v = np.pow(vsh,(2-vsh))
        f1  = 1 / ( ff * flures )
        f2  = 2 * np.sqrt ( v / ( flures * ff * rtsh ) )
        f3  = v / rtsh
        sat = ( 1 / ( rt * ( f1 + f2 + f3 ) ) ) ** ( 1/N )
        sat = np.minimum ( sat, 1 )
        return sat
    def sw_indonesia_iter(self,A,M,N,vsh, den, neu, rhomf, rhohc, rhoma, rhobsh, salm,excavf, rt, rtsh,flures):
        # Calculate Indonesia Saturation
        phidi=0.2
        sxoi=0.5
        for i in range(10):
            rhofl = sxoi * rhomf + ( 1 - sxoi ) * rhohc
            shr = 1 - sxoi
            
            hced = 1.15 * rhohc #rhohc * ( 1.15 + 0.2 * ( 0.9 - rhohc ) * ( 0.9 - rhohc ))
            aa=1.07 * (( 1.11 - 0.15 * ( salm / 1000000 )) * rhomf - hced )
            bb=(rhomf * (1-salm/1000000) - 1.67 * rhohc + 0.17)/(rhomf * (1-salm/1000000))
            
            delrho = ( phidi * shr ) * aa
            delnphi = ( phidi * shr )* bb*excavf
            #delrho = np.maximum( 0, delrho ).all()
            #delnphi = np.maximum ( 0, delnphi )

            #print(delrho)
            #Correct density
            rhoc_local = den + delrho
            nphic_local = neu + delnphi
            
            #Calculate density effective porosity
            
            nom = (rhoma - rhoc_local)
            denom = ( rhoma - rhomf )
            phiehc = (nom /denom)  - vsh * ( rhoma - rhobsh ) / ( rhoma - rhofl )
            diff = np.abs(phidi-phiehc)
            phiehc = np.maximum(0,phiehc)
            
            #print('here')
            #print(diff)
            #if (diff <= 0.001):
                #break
            if (phiehc > 0).any():
                #Calculate water saturation
                ff = A / phiehc**M
                v = np.pow(vsh,(2-vsh))
                f1  = 1 / ( ff * flures )
                f2  = 2 * np.sqrt ( v / ( flures * ff * rtsh ) )
                f3  = v / rtsh
                sat = ( 1 / ( rt * ( f1 + f2 + f3 ) ) ) ** ( 1/N )
                sat = np.minimum (sat, 1 )
            else:
                phiehc=0
                sat=1.0
            sxoi=sat
            phidi = phiehc
            print(i,pd.DataFrame(vsh).iloc[400:450])
            if (diff<0.001).all():
                break
        return phiehc, sat, rhoc_local, nphic_local
    def calculate_d_model_all_Tops(self, main_window):
        self.main_window = main_window        
        sel_well=  main_window.current_well
        sel_dataset = main_window.current_dataset
        project_path = main_window.project_path
        print('Calculating CPI for well:', sel_well)
        print('Calculating CPI for Dataset:', sel_dataset)
        
        well = [well for well in self.main_window.selected_wells if well.well_name == sel_well][0]
        print(well.well_name)
        datasets = well.datasets
        if sel_dataset:
            dataset = [dtst for dtst in datasets if dtst.name == sel_dataset][0]
            print('Input Dataset:', dataset.name)
        else:
            print('No Dataset selected')
        index = dataset.index_log
        log_mnemonics = []
        for log in dataset.well_logs:
            log_mnemonics.append(log.name)
        data = {mnem:{} for mnem in log_mnemonics}

        for well_log in dataset.well_logs:
            mnem = well_log.name
            data[mnem] = well_log.log
        #print(GR)
        cpi= CPI()

        
        #Make a input curves dataframe 
        df_input = pd.DataFrame(data)
        #print(df_input.head())
        
        zon = main_window.docks["Zonation"]
        zone_file_path = zon.combo_box.currentText()
        print(zone_file_path)
        df_param = pd.read_csv(zone_file_path) 
        df_param_well = df_param[df_param['Well']==sel_well]    
        cpi_top=df_param_well['Top'].min()
        cpi_bot=df_param_well['Base'].max()
        print('Range processing:', cpi_top, cpi_bot )
        df_input.reset_index(inplace=True)
        df_input.rename(columns={'DEPT':'DEPTH'},inplace=True)
        df_input = df_input[(df_input['DEPTH'] > cpi_top) & (df_input['DEPTH'] < cpi_bot)]
        
        dfc = cpi.calc_VSHGR(df_input, df_param_well)
        las_out_folder = os.path.join(project_path,"data")  
        if not os.path.exists(las_out_folder):
            os.makedirs(las_out_folder)
        las_file_path = os.path.join(las_out_folder, 'result.las')
        cpi.export_df_to_las(dfc, well.well_name, 'TESTCOMP', las_file_path)
        return True
    def calculate_d_model_all_csv_params(self, main_window):
        self.main_window = main_window        
        sel_well=  main_window.current_well
        sel_dataset = main_window.current_dataset
        project_path = main_window.project_path
        print('Calculating CPI for well:', sel_well)
        print('Calculating CPI for Dataset:', sel_dataset)
        
        well = [well for well in self.main_window.selected_wells if well.well_name == sel_well][0]
        print(well.well_name)
        datasets = well.datasets
        if sel_dataset:
            dataset = [dtst for dtst in datasets if dtst.name == sel_dataset][0]
            print('Input Dataset:', dataset.name)
        else:
            print('No Dataset selected')
        index = dataset.index_log
        log_mnemonics = []
        for log in dataset.well_logs:
            log_mnemonics.append(log.name)
        data = {mnem:{} for mnem in log_mnemonics}

        for well_log in dataset.well_logs:
            mnem = well_log.name
            data[mnem] = well_log.log
        #print(GR)
        cpi= CPI()

        
        #Make a input curves dataframe 
        df_input = pd.DataFrame(data)
        #print(df_input.head())
        
        zon = main_window.docks["Zonation"]
        zone_file_path = zon.combo_box.currentText()
        print(zone_file_path)
        df_param = pd.read_csv(zone_file_path) 
        df_param_well = df_param[df_param['Well']==sel_well]    
        cpi_top=df_param_well['Top'].min()
        cpi_bot=df_param_well['Base'].max()
        print('Range processing:', cpi_top, cpi_bot )
        df_input.reset_index(inplace=True)
        df_input.rename(columns={'DEPT':'DEPTH'},inplace=True)
        df_input = df_input[(df_input['DEPTH'] > cpi_top) & (df_input['DEPTH'] < cpi_bot)]
        
        dfc = cpi.calc_VSHGR(df_input, df_param_well)
        las_out_folder = os.path.join(project_path,"data")  
        if not os.path.exists(las_out_folder):
            os.makedirs(las_out_folder)
        las_file_path = os.path.join(las_out_folder, 'result.las')
        cpi.export_df_to_las(dfc, well.well_name, 'TESTCOMP', las_file_path)
        return True
    