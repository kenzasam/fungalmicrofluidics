# Mon, DD YYYY 

**Experiment details**

**Notes**

**To Do**

# Feb, 02 2021

**Experiment details**
- Probing.
- Resorufin sorter experiment: resorufin 10ng/L (10x dilutioon from stock) in plastic syringe. 530nm excitation through new 100um fiber. Emission detection with 200um fiber, directly to spec. Python module. 250mVpp.

**Notes**
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

**To Do**
- [ ] redesign holder
- [ ] new syringe
- [X] rescaling graph
- [ ] integration time resetting


# Jan, 28 2021 

**Experiment details**
Sorting of water in oil droplets. New elec config, fab on January 24th.


**Notes**
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
**To Do**


# Jan, 16 2021

**Experiment details**

530nm excitation, 100um core fiber. 50ng/L resorufin drops, in HFE 7500 2% surfactant. arpund 280nm emmission, 200um core fiber to Flame spec.
Operating flame with ArduBridge lib threadSpec and specplot.

**Notes**
- Can't zoom on graph when reading spectrum
- For resorufin 50ng/L need int time of 500000 us
- Tested with Resorufin in plastic syringe
- Bridge tube was squeezed and thus resulted in tiny drops
- final flowrates: : 0.001uL/s and oil 0.005uL/s

**To Do**
- send from Threadspec the int time to Specplot, whenever it is changed
- call Thorlabs, figure out the right fibers for filter setup.
- new bridge, flat cut
Xled is 565nm, grenn: 590nm and 530nm.... Look for new led module
