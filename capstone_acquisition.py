from pycromanager import Acquisition, multi_d_acquisition_events, Bridge, Dataset
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

   x=pos_list.get_position(idx).get(0).x
   y=pos_list.get_position(idx).get(0).y
   z=pos_list.get_position(idx).get(1).x

   x_array.append(x)
   y_array.append(y)
   z_array.append(z)

x_array = np.array(x_array)
y_array = np.array(y_array)
z_array = np.array(z_array)
   
def img_process_fn(image, metadata):
   #add in some new metadata
   metadata['a_new_metadata_key'] = 'a new value'

   #modify the pixels by setting a 100 pixel square at the top left to 0
   image[:100, :100] = 0
   
   #propogate the image and metadata to the default viewer and saving classes
   return image, metadata

# run an acquisition using this image processor
if __name__ == '__main__':

   with Acquisition(directory='E:\KENZA Folder\CapstoneTests', name='saving_name', image_process_fn=img_process_fn) as acq:
      #Generate the events for a single z-stack
      xyz = np.hstack([x_array[:, None], y_array[:, None], z_array[:, None]])
      events = multi_d_acquisition_events(xyz_positions=xyz)
      acq.acquire(events)
      mmc._close()

dataset = acq.get_dataset()
dask_array = dataset.as_array(stitched=True)
with napari.gui_qt():
   v = napari.Viewer()
   v.add_image(dask_array)
#img = dask_array.read_image()
#plt.imshow(img, interpolation='nearest')
#plt.show()  # <--- show us the image

#dataset = acq.get_dataset().as_array()
#img = dataset.read_image()
  # <---- read our z-stack index 0
#plt.imshow(img, interpolation='nearest')  # <---- convert numpy array into image
#plt.show()  # <--- show us the image

