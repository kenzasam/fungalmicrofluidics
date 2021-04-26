import pandas as pd
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join
#filename='20210210-dropletspeed-dgw003-dgo004-sp00-00003.txt'
#mypath='E:/KENZA Folder/PROJECT2_ClRosea/sorting/droplet_HS/metadata/'
#mypath='/Users/kenza/OneDrive - Concordia University - Canada/CASB-PhD/Gitbubble/fungalmicrofluidics_basement/Experimental/Droplet_speed/Metadata/'
mypath='C:/Users/k_samla/OneDrive - Concordia University - Canada/CASB-PhD/Gitbubble/fungalmicrofluidics/Experimental/Droplet_speed/Metadata/'
#
start= [6, 2, 5, 5, 5, 3, 7, 3, 4, 7, 7, 7, 8, 10, 26, 20, 8, 7, 12, 2, 26, 6, 7, 23, 24, 15, 39, 3, 4, 6, 35, 17, 27, 1, 17, 29, 23, 17, 8, 7, 25, 13 ]
#stop= [36, 27, 28, 27, 25, 22, 25, 19, 19, 21, 21, 19, 20, 21, 37, 30, 19, 17, 21 , 11, 34, 14, 14, 30, 30, 21, 45, 8, 9, 11, 40, 22, 31, 5, 18/2, 33/2, 25, 19, 10, 9, 27, 15 ]
stop= [36, 27, 28, 27, 25, 22, 25, 19, 19, 21, 21, 19, 20, 21, 37, 30, 19, 17, 21 , 11, 34, 14, 14, 30, 30, 21, 45, 8, 9, 11, 40, 22, 31, 5, 18, 33, 25, 19, 10, 9, 27, 15 ]

def returnspeed(filename,first_frame, last_frame):
    df = pd.read_csv(str(filename), header=0, sep="\t")
    #print df
    new_df = df[df['Key'].str.contains('Time_From_Last')]
    new_df.head()
    #print new_df
    df3=df[df['Key'].str.match('Field %d Time_From_Last'%(first_frame))]
    for i in range(first_frame+1,last_frame+1):
        df2 = df[df['Key'].str.match('Field %d Time_From_Last'%(i))]
        thing =[df3, df2]
        df3=pd.concat(thing)
    #print df3
    df3.head()
    df3['Value']=pd.to_numeric(df3['Value'])
    totaltime=df3['Value'].sum()
    return totaltime

#list all flowrates
files = [mypath+f for f in listdir(mypath) if isfile(join(mypath, f))]
flowrates = [f[-7:-4] for f in listdir(mypath) if isfile(join(mypath, f))]
#print flowrates

data = {'File': files, 
'Flowrate': flowrates, 
'start': start,
'stop': stop
}
df = pd.DataFrame(data, columns=['File','Flowrate', 'start', 'stop'])
df['Flowrate']=pd.to_numeric(df['Flowrate'])
df['Speed'] = df.apply(lambda x: returnspeed(x['File'], x['start'], x['stop']), axis=1) 
print (df)
print(data)
# saving the DataFrame as a CSV file 
csv_data = df.to_csv('Speed_data.csv', index = False) 
print(('\nCSV String:\n', csv_data)) 
'''
data['Speed']= list(lambda x: returnspeed(data['File'], data['start'], data['stop']))
plt.figure()
plt.plot(x=data['Flowrate'], y=data['Speed'])
plt.show()
'''
