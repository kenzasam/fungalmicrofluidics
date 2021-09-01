'''
Script to be used to convert .dat files to csv files.
The first 4 Rows are deleted.

Version = 0.1
Py 2.7
'''
import pandas as pd
#user input
label='_glc_mut_27C_10msec'
filename = "PeakData-20210622-T16h07m45s_chitin_4d_wt.dat"
# reading given csv file 
# and creating dataframe
df = pd.read_csv(filename,
                       header = 0,
                       skiprows=5)
df[df.columns[0].split(',')] = df.iloc[:,0].str.split(',', expand=True)
df.drop(df.columns[0], axis=1, inplace=True)
#adding column headings
#peakdata.columns = ['Name', 'Type']
print(filename[:-4])
#store dataframe into csv file
df.to_csv(filename[:-4]+label+'.csv', index = None)
print('Saved.')

#display quick plot
