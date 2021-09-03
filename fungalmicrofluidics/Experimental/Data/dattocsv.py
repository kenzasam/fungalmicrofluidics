'''
Script to be used to convert .dat files to csv files.
The first 4 Rows are deleted.

Version = 0.1
Py 2.7
'''
import pandas as pd
#user input
label='_glu_mut_27C_50msec'
filename = r"PeakData-20210729-T15h40m47s.dat"
# reading given csv file 
# and creating dataframe
df = pd.read_csv(filename,
                       header = 0,
                       skiprows=5)
'''Following two lines are needed if your rows are saved as strings. Check your .dat file in a Text editor.
'''
df[df.columns[0].split(',')] = df.iloc[:,0].str.split(',', expand=True)
df.drop(df.columns[0], axis=1, inplace=True)
#adding column headings
#peakdata.columns = ['Name', 'Type']
print(filename[:-4])
#store dataframe into csv file
df.to_csv(filename[:-4]+label+'.csv', index = None)
print('Saved.')

#display quick plot
