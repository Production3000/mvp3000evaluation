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


# Turn on interactive mode, needed to have non-blocking graphs in the loop 
plt.ion()
user_input = ""
while True:
    # Get user input and allow break
    try:
        # It is not possible to remove a previously set description
        _previous = "" if user_input == "" else f"[{user_input}] "
        new_input = input(f"Enter description to auto-save (Ctrl-C to exit): {_previous}")
    except KeyboardInterrupt:
        print()
        break

    if new_input.strip() != "":
        user_input = new_input

    # Clear data and avg, but keep offset
    print("Collecting data ...")
    serialData.restart_data_acquisition()
    while serialData._avg_count_reached_event.is_set() is False:
        time.sleep(0.05)


    ### Select which data to use
    _data = serialData.data
    # _data = serialData.mean
    ### Select raw, offset, scaling
    _array = _data.raw()
    # _array = _data.scaled()
    ### Select colorbar limits
    # _minmax = _data.minmax_raw()
    # _minmax = _data.minmax_scaled()
    _minmax = _data.minmax_forever_raw()
    # _minmax = _data.minmax_forever_scaled()


    # Auto-save data
    if user_input != "":
        serialData.write_incremental_csv(_array, user_input)

    # Initialize plot
    fig, ax = plt.subplots() 
    im = plt.imshow(_array, aspect = 'auto', origin='upper', cmap='viridis', extent=(0.5, serialData.sizeX() + 0.5, 0.5, serialData.sizeY() + 0.5))
    # Show only the major ticks
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    # Colorbar
    plt.colorbar(im, ax=ax, orientation="vertical")
    im.set_clim(_minmax)
    plt.show()


# End thread and close serial
serialData.stop_serial()
