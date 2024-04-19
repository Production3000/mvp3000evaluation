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
serialData.measure_offset()
# Stored offset
# serialData.load_offset()
### Scaling, unset is unity, should best be done on the ESP
serialData.load_scaling()


def update_plot(_):
    """
    Update function for the animation. Updates the imshow plot if new data is available.
    """
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
        im.set_array(_array)
        im.set_clim(_minmax)

    return im


# Initialize plot
fig, ax = plt.subplots()
fig.canvas.mpl_connect('close_event', serialData.stop_serial) # Exit thread with plot close
im = ax.imshow(serialData.data.scaled(), aspect = 'auto', origin='upper', cmap='viridis', extent=(0.5, serialData.sizeX() + 0.5, serialData.sizeY() + 0.5, 0.5))
# Show only the major ticks
ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
# Colorbar
plt.colorbar(im, ax=ax, orientation="vertical")

# Start the live view
print("Starting live view ... (close graph to exit)")
ani = FuncAnimation(fig, update_plot, interval = 50)
plt.show()
