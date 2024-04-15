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
import time

from SerialData.SerialData import SerialData


### Set up the serial connection (adjust the COM port and baud rate according to your configuration)
avg_count = 10
serialData = SerialData('/dev/ttyACM0', avg_count)

### Set a data function, default is lambda _data: _data
# data_function = lambda _data: 1 / _data
# serialData.set_data_function(data_function)

# Wait for first data to arrive
serialData.wait_for_serial()

### Offset, unset is zero, should best be done on the ESP
# Measure current offset
offset_count = 10
# offset_targetValue = 0
serialData.measure_offset(offset_count)
# Stored offset
# serialData.load_offset()
### Scaling, unset is unity, should best be done on the ESP
serialData.load_scaling()


# Prepare initial graph
_array = serialData.data.scaled()
_minmax = serialData.data.minmax_forever_scaled()
fig, ax = plt.subplots()
im = plt.imshow(_array, aspect = 'auto', origin='upper', cmap='viridis', extent=(0.5, serialData.sizeX() + 0.5, serialData.sizeY() + 0.5, 0.5))
plt.colorbar(im, ax=ax, orientation="vertical")
im.set_clim(_minmax)
# Show only the major ticks
ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
# Turn on interactive mode, needed to have non-blocking graph
plt.ion()
plt.show()

try:
    # Catch Ctrl-C in input and during loop
    user_input = input("Description required (empty or Ctrl-C to exit): ").strip()
    if user_input == "":
        raise ValueError

    _counter = 0
    while True:
        _counter += 1
        print(f"Collecting data ... {_counter}")
        serialData.restart_data_acquisition()
        
        while serialData._avg_count_reached_event.is_set() is False:
            time.sleep(0.05)


        ### Select which data to use
        _data = serialData.mean
        # _data = serialData.mean
        ### Select raw, offset, scaling
        # _array = _data.raw()
        _array = _data.scaled()
        ### Select colorbar limits
        # _minmax = _data.minmax_raw()
        # _minmax = _data.minmax_scaled()
        # _minmax = _data.minmax_forever_raw()
        _minmax = _data.minmax_forever_scaled()


        im.set_array(_array)
        im.set_clim(_minmax)
        # Pause needed for some reason, not needed when there is an input() in the loop 
        plt.pause(0.05)

        # Auto-save data
        serialData.write_incremental_csv(_array, user_input)

except: # ValueError or KeyboardInterrupt
    print() # new line

# End thread and close serial
serialData.stop_serial()
