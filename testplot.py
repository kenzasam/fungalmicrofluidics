from matplotlib import pyplot as plt
preampmVpp=[200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 900, 1100, 1300, 1600, 1800]
Vrms=[17.4, 21.3, 25, 28.7, 32.6, 36.5, 40.3, 44.3, 48.3, 52.1, 56.1, 60.1, 64, 72, 87.5, 103, 124]
plt.xlabel('preampmVpp')
plt.ylabel('Vrms')
plt.title('Measurements Feb 02 2020')
plt.plot(preampmVpp,Vrms)
plt.show