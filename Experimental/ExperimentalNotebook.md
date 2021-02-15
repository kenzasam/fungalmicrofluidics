# Mon, DD YYYY 

## Experiment details

## Notes

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
- [] test autonomous sorting thread
- [] plot peaks and annotate with wavelength
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
