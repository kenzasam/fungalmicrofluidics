'''
Script to be used to convert .dat files to csv files.
The first 4 Rows are deleted.

Version = 0.1
Py 2.7
'''
import pandas as pd

filename=r"E:\KENZA Folder\PYTHON\fungalmicrofluidics\fungalmicrofluidics\Experimental\Data\PeakData-20210617-T15h01m16s_chitin_wt_4d.dat"
# reading given csv file 
# and creating dataframe
peakdata = pd.read_csv(filename
                       ,header = 0,
                       skiprows=5)
  
# adding column headings
#peakdata.columns = ['Name', 'Type']
print(filename[:-4])
# store dataframe into csv file
peakdata.to_csv(filename[:-4]+'.csv', index = None)
print('Saved.')
