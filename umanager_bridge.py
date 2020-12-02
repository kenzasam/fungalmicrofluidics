# simple single image acquisition example with snap
import time

import matplotlib.pyplot as plt
import numpy as np

from pycromanager import Bridge, multi_d_acquisition_events

#### Setup ####
bridge = Bridge()
core = bridge.get_core()

#### imaging settings
exposure = 20
num_frames_to_capture = 2
core.set_exposure(exposure)
x = np.arange(0, 5)
y = np.arange(0, -5, -1)
xy = np.hstack([x[:, None], y[:, None]])
xy

#### strobe settings
# by enforcing a strobe (a small delay between acquisitions), our snap_image acquisition framerate becomes an order of magnitude more accurate (as of 20201006)
interframe_interval = 50
assert interframe_interval > exposure

#### holder variables for images, model values, and processing timestamps
frames = []
model = []
acq_timestamps = []
process_timestamps = []

#### do acquisition
print("beginning acquisition...")
t0 = time.time()
next_call = time.time()  # updated periodically for when to take next image
for f in range(num_frames_to_capture):

    # snap image
    core.snap_image()
    tagged_image = core.get_tagged_image()

    # save acquisition time timestamp
    t1 = time.time()
    acq_timestamps.append(time.time() - t0)

    # pixels by default come out as a 1D array. We can reshape them into an image
    frame = np.reshape(
        tagged_image.pix,
        newshape=[tagged_image.tags["Height"], tagged_image.tags["Width"]],
    )

    # quantify image and save processing time timestamp
    #val = process_frame(frame, ip, is_demo=True)
    #process_timestamps.append(time.time() - t1)

    # store latest value in model and conditionally trigger perturbation
    #model.append(val)
    #process_model(model)

    # helpful printout to monitor progress
    if f % 50 == 0:
        print("current frame: {}".format(f))

    # wait until we're ready to snap next image. note that in this example, the first few images may exceed the strobe delay as numba jit compiles the relevant python functions
    nowtime = time.time()
    next_call = next_call + interframe_interval / 1000
    if next_call - nowtime < 0:
        print(
            "warning: strobe delay exceeded inter-frame-interval on frame {}.".format(f)
        )
    else:
        time.sleep(next_call - nowtime)

print("done!")
