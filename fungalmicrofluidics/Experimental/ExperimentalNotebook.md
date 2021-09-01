
# Wed, 04 09 2021
## Experiment details

### FDGlu wt 
50msec 
0.025 oil 
0.01 drops 
normal setting led
continuous gating plot

### FDGlu mut
50msec 
0.025 oil 
0.01 drops 
normal setting led
continuous gating plot and sorting (>8000). Didn't go as well. Lots of giant drops/broken, as expected

### FDGlcNAc mut
10msec 
0.025 oil 
0.01 drops 
normal setting led
continuous gating plot and sorting(>40 000, 0.1 t, 0.3 ont).


# Fri, 25 08 2021
## Experiment details
gating plots of wt and mutant with FDGlcNAC, and also sorting out mutants

See gating plots

needed 10msec int time only. Sorted >40.000

# Thu, 19 08 2021
## Experiment details

### Auto-sort, using 5uM fluorescein and 0.6% dye H2O
*droplet generation* 
- Fluorescein 5uM: 0.0008 oil: 0.005
- H2O: 0.002 Oil: 0.008
- Spacer: 0.02 (but leak at fiber)

*sorting*
- Potential: 450, 10kHz
- Time: 0.2sec
- Gate:  , 500-550nm,
- Int time: 100msec
- pin ontime: 0.4s

Droplets not small enough.
Next time: make drops seperately into pcr tube, then mix population.

# Fri, 29 07 2021
## Experiment details
FDGlu 4d CCMM
gatingplot

didn't go great, only few peaks....
Poisson yes
see excel

# Sat, 03 07 2021
## Experiment details

### Auto-sort, using 5uM fluorescein and 0.6% dye H2O
see screenshot 

*droplet generation* 
- Fluorescein 5uM: 0.0005 oil: 0.0035
- H2O: 0.0085 Oil: 0.006
- Spacer: 0.05 (but leak at fiber)
- total flow = 

*sorting*
- Potential: 420, 10kHz
- Time: 0.1sec
- Gate:  , 500-550nm,
- Int time: 100msec
- pin ontime: 0.4s

pos outlet:
10 blue (FN) out of 57 P
47 fluo (TP) out of 57 P

neg outlet:
165 blue (TN)
34 fluo (FP) out of 199 N

sensitivity or TPR: 47/57 = 82.45%
specificity or TNR: 165/199 = 83%
precision or PPV = 47 / (47+34) = 58.02%
### Sort out mutants at 36 C
Detect ALL peaks above noise. filter later.

flowrate oil: 0.35
flowrate drops:0.1
gate:
noise: 500
background subs
50msec int time
drop travel time:
pulse time:




# Tues, 22 06 2021
## Experiment details

sort out mutants and wt at 26C and 34 C
Detect ALL peaks above noise. filter later.

flowrate oil: 0.35
flowrate drops:0.1

gate:
noise: 500
background subs
50msec int time

drop travel time:
pulse time:


until row 1749: mutants 1


# Sun, 13 06 2021
## Experiment details
Auto-sort, using 5uM fluorescein and 0.6% dye H2O

*droplet generation* 
PERFECT
Fluorescein 5uM: 0.00085 oil: 0.003
H2O: 0.002 Oil: 0.008
Spacer: 0.03
total flow = 44nL/s

*sorting*
Potential: 350, 10kHz
Time: 0.2sec
Gate:  , 500-550nm,
Int time: 50msec
pin ontime: 0.1s

## Notes

## To Do
/


# Mon, DD YYYY
## Experiment details
AUTO-SORT

*droplet generation*
Fluorescein 5uM: 0.0005 oil: 0.005
H2O: 0.001 Oil: 0.001
total flow = 

*sorting*
Spacer: 0.05
Potential: 350, 10kHz
Time: 0.2sec
Gate:  1500-60.000, 500-600nm,
Int time: 50msec
pin ontime: 0.3s
## Notes

When stopped in GUI, then start again : Thread terminated immediately
Sorting went okayish. definitely not perfect. need to use dye in h20 in order to see better


# May 13, 2021
# Experiment details
double droplet generator with independent oil flow.
Much better, yay. nice ratio of around 30% fluo drops.
Fluorescein 10mM: 0.0005 oil: 0.002
H2O: 0.003 Oil: 0.008
Droplets are a bit big. Ratio maybe too much.


Fluorescein 10mM: 0.0005 oil: 0.003
H2O: 0.003 Oil: 0.009
Ratio around 10% or less. Droplets still a litle big.

Restructured code and fixed relative imports

## Notes
To do, fix path for all of the data files, including PID.

# May, 4th 2021

# Experiment details
for 10uM: gate 4000-60.000, 500-600nm 500events
for 5uM: gate 1500-60.000, 500-600nm, 500events
for 50uM: gate 4000-80.000, 500-600nm, 500events

## Notes
- oil: 0.012
- fluorescein 10uM / 5uM / 50uM: 0.004
- oil spacer 0.06


# Mon, DD YYYY

## Experiment details

## Notes
150mvpp, 15nl/s
150, 90
600 mvpp, 15nl/s
## To Do

# March 24 2021

## Experiment details
histogram of resorufin intensity for gating
## Notes
- oil: 0.004
- resorufin 20g 60g: 0.001
- oil spacer 0.06

BUT! resorufin syringe kind of blocked. Better check droplet size from video. Checked again on 30.03.2021 and 0.001/0.004 gives really tiny droplets...

Script worked great. But gating overlaps. Resolution bad....
Use flow rates exactly ame as for what you would use in autosort.
## To Do

# March 20th 2021

## Experiment details
Auto-sort: 20ng/L Resorufin, H2O in two T-junction device. Bridge to sorter (with droplet generator, since we don't have good ones with droplet collection anymore.) Two yellow tubing going outside.
Let run for a bit, thenm perform autosort at these scenarios:

- 450Vpp, 80nL/s, 0.1t
- 350Vpp 60nL/s, 0.13

## Notes
use tubing of Sam to fit yellow tubing inside and make bridge. Surprisingly worked.
Droplet collection chip = incubation chamber chip. Not ideal... drops just fly past. What else??

Drops came in with too many resoruifin positive. How can I control the ratio of Reso+ vs H2O??

## To Do
- [x] GUI splash screen
- [x] add time interval for sorting into GUI/
- [x] Know whether spec is on, from Ardubridge, npt GUI....

# March, 9 2021

## Experiment details
Autosort!!
Two chips: sorter with droplet input, and double drop generator of chiara.
20ng/mL resorufin.
Droplet generation varied, see videos.

Trying to find at which speed we can still detect with Int time of 100000.

## Notes
Plotting has delay when overlay.

## To Do
- [x] Integration time
- [x] easily turn overlay off.


# March 4th, 2021

## Experiment details
SORTING EFFICIENCY GRAPH
Sorting: varying Vpp and oil flow rate.
Kept droplet generation constant at W:0.0005, O:0.001/0.0012.
Made videos of failures.

## Notes
All results into spreadsheet.

## To Do
- [x] plot and analyze data.
- [ / ] take excerpts from videos
- [ ] make slomo videos of errors


# March, 2nd 2021
## Experiment details
autosort with fibers and all the bells nd whistles.
With 10ng/L resorufin and BP filter.
Took around 1 hr to set up: place new chip in holder, inserting fibers, taping fibers, connecting optics, starting flow...

## Notes
Went ok. Good first try. Problem: outlet of +sorting channel was partially blockd, so not good flow. Also had no clue what ideal Vpp/oil settings were.
But figured out SpecSP settings!

**Settings SApecSP:**

Period = 0.1 ,      #<-- Period-time of the control-loop [s]. 1 runs it once. Defines plotting speed.
nameID = 'Auto Sort',
threshold = 3200,    #<-- Threshold peak intensity above which trigger goes.
noise = 2500,       #<-- background noise level.
DenoiseType = 'BW', #<-- BW, Butterworth filter
PeakProminence = None, #
PeakWlen = None, #
PeakThreshold = None, # Vertical distance to neighbouring peaks
PeakWidth = [15,200],#<-- [min,max] width of the peak(s) in nm
Peak_range = [520,680],  #<-- [min,max] wavelength of the peak(s) in nm
Pin_cte = 75, #37,       #<-- electrode to turn on constantly
Pin_pulse = 98, #38,     #<-- electrode to pulse for sorting
Pin_onTime = 0.2,   #<-- pulse on time [s].
t_wait=0.1

**Settings PID:**

nameID='PID', #<-- proces name
Period=0.5,   #<-- Period-time of the control-loop. PID calculation cycle time in sec.
fbPin=1,      #<-- The analog pin (Ardu) of the temp sensor.
outPin=10,    #<-- The output pin  of the driver (Ardu connection).
dirPin=7      #<-- The direction pin for the driver (Ardu connection).                                  
Pid.PID.Kp = 30 #<-- proportional control of PID
Pid.PID.Ki = 1.2 #<-- integral of PID
Pid.PID.Kd = 0.0 #<-- rate of change of PID (derivative)
Pid.RC_div_DT = 10.0 #<-- time constant, determining how fast you reach settle point


## To Do
- [x] save succesful settings and write in methods or results.


# March,1 2021

## Experiment details
Doing a bunch of coding and testing. The autonomoussorting is now ready for use!!
***Probing 50 - 200mVpp***
 Pin 46. 10X
10khz
## Notes
```python
Vpp3=[50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 1100, 1300, 1600]
Vrms3=[3.97, 8.13, 12.1, 16.0, 20.0, 23.9, 27.9, 31.8, 35.7, 39.7, 43.7, 47.7, 51.6, 55.6, 59.5, 63.5, 67.4, 71.0, 87.3, 102, 126]
```
## To Do
- [x] add results to graph



# Feb, 21 2021

## Experiment details
Saturday session!

## Notes

broke fiber in chip.
Used PDMS filled chip.
Quick testing of auto sort.
Auto sort is buggy: for some reason, always in each loop detects drop....

## To Do

- [x] peaks" print intensities and wavelengths
- [x] for autosort, be able to tell range of wavelennth in between which you expect peak. e.g. in case background substraction doesn't work well...
- [x] print for after setting treshold or Int time through GUI.

# Mon, DD YYYY

## Experiment details

## Notes

## To Do

# Feb, D15 2021

## Experiment details
Tested the Spec.SP.start() function experimentally.
Device channel V4 elec V4 straight design.
- Elec pulses: 10kHz, 250mVpp. Probed:
- Droplet generation oil flow: 0.004
- Droplet generation H2O flow:0.003
- spacer oil either 0.01 or 0.02
- 400um core fiber between 580nm filter and spec.


## Notes
Perforated pdms with emm fiber... :( oil flow goes out.
Tested SpecSP.start() and stop(). Both worked as expected. The findpeaks function was able to find peak above treshold set (3700). Correct elecs are turned on and off, and elec pulsing works too, tested by probing.

## To Do


# Feb, 10 2021

## Experiment details
**Fast frame rate to determine droplet speed under different oil flows.**

waiting 15sec after increasing oil flow.
- Droplet generation oil flow:
- Droplet generation H2O flow:
- Both kept stable, and only spacer oil increased.
See Spectrometer Data / metadata sheets.

***Probing 50 - 200mVpp***
 Pin 46. 10X
10khz

```python
Vpp=[50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 1100, 1300, 1600]
Vrms=[4.1, 8.05, 12.0, 16.0, 20.0,  24.1, 28.1, 32, 36.1, 40.0, 44, 47.9, 51.9, 55.9, 59.8, 63.7, 67.65, 72.3, 87.9, 103, 127 ]
```



## Notes
***drop speed***
Saved in format: 20210210-dropletspeed-dgw003-dgo004-sp00-00006.cxd

***Code test***

- GUI: can not send = in string through udp.... make a function for setting treshold and setting integration time.
- Togglebutton for sorting does not work. Line 529, AttributeError: 'SortingPanel' object has no attribute 'button'
- Spec cplot can not be started through menu
- sorting sequence: ontime eternalÉÉ

## To Do

# Feb, 09 2021

## Experiment details**
Remote experiment with spectrometer. Using saved data from live experiment, to detect peaks. See code below.

## Notes**
Code that can be used in interactive IDLE, to tune the peak finding function.

```python

Spec.start()
Spec.pause()
Spec.autorepeat=False

nnn = Spec.draft_data()
SpecSP.findallpeaks(nnn)

SpecSP.width=[10,500]
SpecSP.treshold=8000

nono = SpecSP.findpeaks(nnn)
nono
ind = [i for i, item in enumerate(nnn) if item in nono]
peakwvl = [Spec.wavelengths[i] for i in ind]
peakwvl
```
Tuning went well, detected two peaks, one around 521nm (15500 intensity), one at 591nm (9000 intensity) with above settings. Shouldn't that be 230nm though?

Implemented the code for this in ThreadSpec.py and Specplot.py. Peak detection works, Plotting does not work.

## To Do**
- [] test elec sequence through GUI
- [] change period and ontime of elec sequence, tune. GUI?
- [] test GUI
- [x] test autonomous sorting thread
- [x] plot peaks and annotate with wavelength
- [] denoised spectrum

# Feb, 02 2021

## Experiment details**
- Probing. Pin 46. 10X
- Resorufin sorter experiment: resorufin 10ng/L (10x dilutioon from stock) in plastic syringe. 530nm excitation through new 100um fiber. Emission detection with 200um fiber, directly to spec. Python module. 250mVpp.

## Notes**
- probing
```python
import matplotlib.pyplot as plt
Probing = {
    "preampmVpp": [200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 900, 1100, 1300, 1600]
    "Vrms": [17.4, 21.3, 25, 28.7, 32.6, 36.5, 40.3, 44.3, 48.3, 52.1, 56.1, 60.1, 64, 72, 87.5, 103, 124]
}
preampmVpp=[200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 900, 1100, 1300, 1600]
Vrms= [17.4, 21.3, 25, 28.7, 32.6, 36.5, 40.3, 44.3, 48.3, 52.1, 56.1, 60.1, 64, 72, 87.5, 103, 124]

plt.plot(preampmVpp, Vrms)
plt.ylabel('Measured Vrms')
plt.xlabel('mVpp')
plt.title('10kHz Sine amplified signal')
plt.show()

```

- Resorufin sorter
    - Do NOT use the damn plastic syringe anymore. unreliable florates....
    - fiber 100um is more stable and does not break. However, with full set up (elecs and all) eaily slides too deep. need to print new holder, once final electrodes have been chosen. Or, just stick with what you got.
    - Need to make sure the peak detection works, graphs rescale,

## To Do**
- [ ] redesign holder
- [x] new syringe
- [X] rescaling graph
- [ ] integration time resetting


# Jan, 28 2021

## Experiment details**
Sorting of water in oil droplets. New elec config, fab on January 24th.


## Notes**
DESIGN 1
Sine, 10kHz, 400mVpp: Bottom electrode (37) can be left on without problem, turn 38 on when sorting.

Chip1
sin AkHz B mVpp
with B range 200mVpp - 800 mVpp
and A range 2kHz - 15 kHz
flowrates in ul/s:
dropgen oil:0.0025
dropgen h20:0.002
spacer oil: 0.015

Chip2
sin 10kHz 500mVpp
dropgen oil:0.0025
dropgen h20:0.002
spacer oil: 0.015
(bridge)
## To Do**


# Jan, 16 2021

## Experiment details**

530nm excitation, 100um core fiber. 50ng/L resorufin drops, in HFE 7500 2% surfactant. arpund 280nm emmission, 200um core fiber to Flame spec.
Operating flame with ArduBridge lib threadSpec and specplot.
## Notes**
- Can't zoom on graph when reading spectrum
- For resorufin 50ng/L need int time of 500000 us
- Tested with Resorufin in plastic syringe
- Bridge tube was squeezed and thus resulted in tiny drops
- final flowrates: : 0.001uL/s and oil 0.005uL/s

## To Do**
- [] send from Threadspec the int time to Specplot, whenever it is changed
- [x] call Thorlabs, figure out the right fibers for filter setup.
- [] new bridge, flat cut
Xled is 565nm, grenn: 590nm and 530nm.... Look for new led module
