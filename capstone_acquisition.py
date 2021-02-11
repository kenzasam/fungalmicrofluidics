from pycromanager import Acquisition, multi_d_acquisition_events, Bridge
from matplotlib import pyplot as plt
import numpy as np
import time

bridge = Bridge()
core = bridge.get_core()
mm = bridge.get_studio()
pm = mm.positions()
mmc = mm.core()
pos_list = pm.get_position_list()

x_array = []
y_array = []
z_array = []

for idx in range(pos_list.get_number_of_positions()):
   pos = pos_list.get_position(idx)
   #pos.go_to_position(pos, mmc)
   #print(pos.get_label())

   x=pos_list.get_position(idx).get(0).x
   y=pos_list.get_position(idx).get(0).y
   z=pos_list.get_position(idx).get(1).x

   x_array.append(x)
   y_array.append(y)
   z_array.append(z)

x_array = np.array(x_array)
y_array = np.array(y_array)
z_array = np.array(z_array)
   
#xyz = np.hstack([x_array[:, None], y_array[:, None], z_array[:, None]])
#print(xyz)

with Acquisition(directory='E:\KENZA Folder\CapstoneTests', name='saving_name') as acq:
   #Generate the events for a single z-stack
   xyz = np.hstack([x_array[:, None], y_array[:, None], z_array[:, None]])
   events = multi_d_acquisition_events(xyz_positions=xyz)
   acq.acquire(events)
                                    
#with Acquisition('E:\KENZA Folder\CapstoneTests', 'saving_name', tile_overlap=10) as acq:
#10 pixel overlap between adjacent tiles
#acquire a 2 x 1 grid
    #acq.acquire({'row': 0, 'col': 0})
    #acq.acquire({'row': 1, 'col': 0})

#mmc.acquisitions().stopSequenceAcquisition()
time.sleep(5)

dataset = acq.get_dataset().as_array()
img = dataset.read_image()
  # <---- read our z-stack index 0
plt.imshow(img, interpolation='nearest')  # <---- convert numpy array into image
plt.show()  # <--- show us the image

