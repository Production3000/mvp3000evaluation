""" 
Copyright Production 3000

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License. 
"""

import matplotlib.pyplot as plt

from SerialData.SerialData import SerialData
from SerialData.helper.HelperMatrix import helperMatrix


### Set up the serial connection (adjust the COM port and baud rate according to your configuration)
serialData = SerialData('COM2')

### Set a data function, default is lambda _data: _data
# data_function = lambda _data: 1 / _data
# serialData.set_data_function(data_function)

# Wait for first data to arrive
serialData.wait_for_serial()

### Offset, unset is zero, should best be done on the ESP
# Measure current offset
offset_count = 2
# offset_targetValue = 0
# serialData.measure_offset(offset_count)
# Stored offset
# serialData.load_offset()
### Scaling, unset is unity, should best be done on the ESP
serialData.load_scaling()

input("Press Enter to continue ...")

### Actual noise measurement
noise_count = 10
print("Calculating noise ...")
serialData.measure_noise(noise_count)

# serialData.save_noise()

# End serial thread
serialData.stop_serial(None)


### Full matrix RMS noise
plt.figure()
plt.title("RMS noise.")
plt.loglog(serialData.noise.x[1:], serialData.noise.uncertainty[1:], label=list(range(1, serialData.sizeX() * serialData.sizeY() + 1)) ) # Remove first point, it is obviously useless
plt.xlabel('Averaging count')
plt.ylabel('noise')
plt.grid(which='both')
plt.legend()


### Display all vlaues/pixel as panels
imgsX, imgsY, panel_count_per_fig = helperMatrix.split_figure(serialData.size)
for i in range(serialData.size):
    # Start next figure, if needed
    if i % panel_count_per_fig == 0:
        fig, axs = plt.subplots(imgsY, imgsX, figsize=(imgsX * 3, imgsY * 3), facecolor='w', edgecolor='k')

    _row = i // imgsX
    _col = i % imgsX

    ax = axs[_row, _col]
    ax.scatter(serialData.noise.x, serialData.noise.data_historic[:,i], marker='.', s=5**2, label=f"data {i + 1} / {_row + 1}-{_col + 1}")
    ax.plot(serialData.noise.x, serialData.noise.mean_historic[:,i], color='r', label="running mean") # Remove first, there is no mean
    ax.grid(which='both')
    ax.legend()
    ax.set_xlim(0, noise_count + 1)
    ax.set_ylim(serialData.data.minmax_forever_scaled())
    
    # Only show y-axis labels for first column
    if _col != 0:
        ax.set_yticklabels([])
    # Only show x-axis labels for last row
    if _row != imgsY - 1:
        ax.set_xticklabels([])

    # Last panel overall drawn or current figure full
    if i == serialData.size - 1 or i % panel_count_per_fig == panel_count_per_fig - 1:
        # Last panel overall drawn but figure not full
        if i == serialData.size - 1 and i % panel_count_per_fig != panel_count_per_fig - 1:
            # Clear axis of not-used panels
            for j in range(i % panel_count_per_fig + 1, panel_count_per_fig):
                _row_ = j // imgsX
                _col_ = j % imgsX
                ax_ = axs[_row_, _col_]
                ax_.axis('off')

        # Adjust spacing between subplots to prevent overlap
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        fig.suptitle("Sensor Data Overview.")


### Measurement timing jitter
plt.figure()
plt.title("Measurement Timing Jitter.")
plt.hist(serialData.noise.timings[1:], bins=50) # Remove first, is is always 0
plt.xlabel('Time between measurements (ms)')
plt.ylabel('Counts')
plt.yscale('log')

# plt.show() is blocking
plt.show()
