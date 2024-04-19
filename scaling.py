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


### Set up the serial connection (adjust the COM port and baud rate according to your configuration)
serialData = SerialData('COM2')

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
scaling_count = 10
serialData.load_scaling()


# Prepare initial graph
fig, ax = plt.subplots()
bars = plt.bar(list(range(1, serialData.size + 1)), serialData._scaling.flatten())
# Turn on interactive mode, needed to have non-blocking graph
plt.ion()
plt.show()

# Measurement loop
pixel = 0
target_value = None
while pixel < serialData.size:
    try:
        # Get/confirm pixel
        user_next_pixel = input(f"Pixel number scale ... (Ctrl-C to exit): [{pixel + 1}] ").strip()
        if user_next_pixel != "":
            pixel = int(user_next_pixel) - 1 # user count starts at 1
            continue
        # else pixel confirmed 
        
        # Get/confirm target value
        _previous = "" if target_value is None else f"[{target_value}] "
        user_target_value = input(f"Enter target value ... (Ctrl-C to exit): {_previous}").strip()
        if user_target_value != "":
            target_value = int(user_target_value)
        elif target_value is None: # can only happen during first iteration
            raise ValueError
        # else target value confirmed

    except: # ValueError or KeyboardInterrupt
        break

    # Measure data
    print("Collecting data ...")
    serialData.measure_scaling(pixel, target_value, scaling_count)

    # Update graph
    _data = serialData._scaling.flatten()
    for bar, h in zip(bars, _data):
        bar.set_height(h)
    plt.ylim([min(0, min(_data) * 1.02), max(_data) * 1.02])

    # Go to next
    pixel += 1


# End thread and close serial
serialData.stop_serial()

# Save scaling vector
serialData.save_scaling()

# Output result for copy-paste
print(f"scaling = {serialData._scaling.tolist()}")
