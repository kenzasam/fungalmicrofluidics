# Fungal Microfluidics Software Package
# V 1.1 (Win 7/8/10, Python 2.7)
# Quick Start Package

*by Kenza Samlali, 2021*

## 1. Contributions and license

This program is released under license GNU GPL v3.

All Python dependencies were written by Kenza Samlali.

ArduBridge, protocol file and ChipViewer are part of the [GSOF_ArduBridge package](), and were edited by Kenza Samlali.

GUI was written by Kenza Samlali.

Syringe pump and Spectrometry integration were written by Kenza Samlali.


Other dependencies:

Syringe pump python dependencies are not published here, and can be found [here](https://github.com/psyfood/pyqmix), under GPL v3. The Cetoni QmixSDK with Pump DLL library can be acquired through CETONI.


## 2. Content
```
- License.txt
- Readme.md
- requirements.txt
> fungalmicrofluidics
   - main.py
   - GUI.pyw
   > user_config
      - Protocol.py
      - chip.cfg
   > build
      - FLAME_bridge.py
      - SpecPlot.py
      - TCP_Send.py
      - tcpControl.py
      - threadSpec.py
      - wxChipViewer.bat
      - wxSpecViewer.bat
   > Experimental
      - dattocsv.py
      - notebook.md
   > Spectrometer Data
```

- requirements.txt: All dependencies to be installed with pip
- main.py: The main thread python file. User should edit parameters here.
- GUI.pyw: A graphical user interface for operating a single-cell encapsulating hybrid microfluidic device.
- Protocol.py: User dependent file. This file contains specific sequences of electrode actuation, functions and code that is related to one specific user or chip. Includes a chipviewer cfg file :
- chip.cfg: Chip configuration file indicating the position and wiring of electrodes.
- dattocsv.py : converts dat to a csv file for easy statistical analysis
- notebook : md notebook.
- Spectrometer Data: Spectropmeter output data files

## 3. User Guide

First of all you will need to set up an automation system. Refer to our papers, and the block diagrams in this repository.   
ArduBridge was designed specifically for running with our automation setup and depends on the Electrode Driver Board hardware. Find more info in the ArduBridge repository. 

Next, you will want to make a microfluidic device, in such way that you can assign one number to each electrode.   

We realize the setup of a microfluidic system is not easy, and many possible hardware designs are out there. For an Open Source alternative, we can point to OpenDrop.   
Most systems however rely on the same basics: a micro-controller, connected to port expanders, connected to optocouplers that open up the path for high AC voltage to reach electrodes.
This software is written in a way that you could easily change the port expander addresses, and adapt it to your own "numbering" system.
Similarly, you can change the syringe pump system, and write a library for your own pump system.
All the rest this software does, is giving biologists an easy entry to write scripts for automation of microfluidic procedures.   

### How to set up the software

1. Download the quick_start package and unzip. Place this folder somewhere convenient. Keep all files in the same folder.
2. Make sure your system is set up correctly. [See installation guide](../install_guide.md).
3. Change the user config files. 
   - Change the path in the ChipViewer, and SpecViewer batch files, to point to the chipviewer.exe. This was installed during your ArduBridge installation.   
   - Adapt the protocol file fully to fit your needs: The path pointing to the Nemesys configuration file, electrode sequences you will be using, and other settings in the parameter block.
   - Change the ChipViewer.cfg file: edit it with the coordinates of the electrodes on your Digital Microfluidic device. The numbers represent the specific electrode number.
4. Change the main.py file: the path to your specific protocol, the COM port, and other settings in the parameter block.

### How or when to edit the software

* **Each time you redesign your chip:**   
Edit the Protocol file, to include your sequences and functions.   
Edit the cfg file with your electrode configuration.

* **Each time you run an experiment:**   
Edit the Main file, depending on what hardware and protocol file you intend to use, and whether you want to work in simulation mode or not.  
Edit the Viewer .bat files, with correct arguments and path.

### How to run and use the software

1. Be sure your system is online. Arduino needs to be able to communicate with your PC and the optocouplers. The electrode stack needs to be powered. Any additional instrument, like the pump system, needs to be online too.
2. Check if main.py is set up correctly. Verify the protocol file it runs on.
3. Check the ChipViewer file by running it.
4. Run main.py. This can be best done using the Python IDLE
5. Have fun!


## common methods to use in IDLE
```
setup.sortseq('elec nr','onTime')
setup.seq['seqname'].onTime = t
setup.seq['seqname'].start(1)
setup.specsp.setEvents('500')'
setup.specsp.start()
```