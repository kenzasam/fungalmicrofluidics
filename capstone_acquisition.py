from pycromanager import Acquisition, multi_d_acquisition_events, Bridge
from matplotlib import pyplot as plt
import numpy as np

bridge = Bridge()
mm = bridge.get_studio()
pm = mm.positions()
mmc = mm.core()
pos_list = pm.get_position_list()

for idx in range(pos_list.get_number_of_positions()):
   pos = pos_list.get_position(idx)
   #pos.go_to_position(pos, mmc)
   #print(pos.get_label())
   #print(pos_list.get_position(0).get(0).x) #x position
   #print(pos_list.get_position(0).get(0).y) #y position
   #print(pos_list.get_position(0).get(1).x) #z position

   x=pos_list.get_position(idx).get(0).x
   y=pos_list.get_position(idx).get(0).y
   z=pos_list.get_position(idx).get(1).x
   #print(pos_array)
   xyz = np.hstack(([x], [y], [z]))
   #xyz = np.hstack([x[:, None], y[:, None], z[:, None]])
   print(xyz)

#with Acquisition(directory='E:\KENZA Folder\CapstoneTests', name='saving_name') as acq:
   #Generate the events for a single z-stack
   #xyz = np.hstack([x[:, None], y[:, None], z[:, None]])
   #events = multi_d_acquisition_events(xyz_positions=xyz)
   #acq.acquire(events)
                                    
#with Acquisition('E:\KENZA Folder\CapstoneTests', 'saving_name', tile_overlap=10) as acq:
#10 pixel overlap between adjacent tiles
#acquire a 2 x 1 grid
    #acq.acquire({'row': 0, 'col': 0})
    #acq.acquire({'row': 1, 'col': 0})

#dataset = acq.get_dataset()
#img = dataset.read_image(row=0, col=1)
  # <---- read our z-stack index 0
#plt.imshow(img, interpolation='nearest')  # <---- convert numpy array into image
#plt.show()  # <--- show us the image

