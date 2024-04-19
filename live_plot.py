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
from matplotlib.animation import FuncAnimation

from SerialData.SerialData import SerialData


### Set up the serial connection (adjust the COM port and baud rate according to your configuration)
serialData = SerialData('COM2')

### Set a data function, default is lambda _data: _data
# data_function = lambda _data: 1 / _data
# serialData.set_data_function(data_function)

# Wait for first data to arrive
serialData.wait_for_serial()

### Offset, unset is zero, should best be done on the ESP
# Measure current offset
# offset_count = 3
# offset_targetValue = 0
# serialData.measure_offset(offset_count, offset_targetValue)
# Load/stored offset
# serialData.load_offset()
# serialData.save_offset()
### Scaling, unset is unity, should best be done on the ESP
serialData.load_scaling()


import numpy as np


# Initialize plot
fig, ax = plt.subplots(figsize=(4*3, 4*2))
fig.canvas.mpl_connect('close_event', serialData.stop_serial) # Exit thread with plot close

axes = [ax]
for i in range(serialData.size - 1):
    # Twin the x-axis for independent y-axes
    axes.append(ax.twinx())
    # Move the last y-axis spine over to the right by 20% of the width of the axes
    axes[-1].spines['right'].set_position(('axes', 1 + i * 0.1))

# Space on the right side for the extra y-axis
fig.subplots_adjust(left=0.065, right=(1 - (serialData.size - 1) * 0.065))

# Use the serial data counter to indicate omitted data points
x_start = serialData._counter
axes[0].set_xlabel('Data counter')

lines = []
for i, ax in enumerate(axes):
    # Std matplotlib color palette
    _color = plt.rcParams['axes.prop_cycle'].by_key()['color'][i]
    # Plot line, returns a list of lines where we only need the first
    lines.append( ax.plot(x_start, serialData.data.scaled().T[i], label=f"{i+1}", color=_color, linewidth=0.5)[0] )
    # Color axis with plot
    ax.tick_params(axis='y', colors=_color)

# Add legend to first axis
axes[0].legend(lines, [_line.get_label() for _line in lines], loc='upper center', bbox_to_anchor=(0.5, 1.1), fontsize= 'small', ncol=serialData.size)


def update_plot(_):
    """
    Update function for the animation. Updates the imshow plot if new data is available.
    """
    global x_start
    if serialData.new_data_event.is_set():
        serialData.new_data_event.clear()

        ### Select which data to use
        _data = serialData.data
        # _data = serialData.mean
        ### Select raw, offset, scaling
        # _array = _data.raw()
        _array = _data.scaled()
        ### Select colorbar limits
        # _minmax = _data.minmax_raw()
        # _minmax = _data.minmax_scaled()
        # _minmax = _data.minmax_forever_raw()
        _minmax = _data.minmax_forever_scaled()

        # Update graph data
        for i, (ax, line) in enumerate(zip(axes, lines)):
            #print(line.get_data())
            x, y = line.get_data()
            x = np.concatenate([x, [serialData._counter]])
            y = np.concatenate([y, _array.T[i]])
            line.set_xdata(x)               
            line.set_ydata(y)

            #   
            ax.set_ylim(_data.min_forever_scaled_array().T[i], _data.max_forever_scaled_array().T[i])

        # Update limits
        plt.xlim(x_start, serialData._counter + 1)
        # plt.ylim(_minmax)

    return lines

# Start the live view
print("Starting live view ... (close graph to exit)")
ani = FuncAnimation(fig, update_plot, interval = 250)
plt.show()
