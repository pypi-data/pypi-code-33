import matplotlib
import numpy as np
import matplotlib.backends
print('a', matplotlib.backends._get_running_interactive_framework())
if matplotlib.get_backend() != "TKAgg":
    print('b', matplotlib.backends._get_running_interactive_framework())
    matplotlib.use("TKAgg")
    print('c', matplotlib.backends._get_running_interactive_framework())
print('d', matplotlib.get_backend())
print('e', matplotlib.backends._get_running_interactive_framework())
from matplotlib import pyplot as plt
print(matplotlib.backends._get_running_interactive_framework())
plt.figure(num=1, figsize=(5, 5))
x = np.linspace(0, 2, 100)
plt.plot(x, x, label='linear')

print(matplotlib.backends._get_running_interactive_framework())
plt.draw()
print(matplotlib.backends._get_running_interactive_framework())
plt.show()
print(matplotlib.backends._get_running_interactive_framework())
