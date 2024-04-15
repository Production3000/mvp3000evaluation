# MVP3000 Evaluation

This is the data evaluation code matching the 'MVP 3000' rapid prototyping framework. 

Recieves data via the serial interface and processes it for display and noise analysis.


## CSV Data Format

CSV Data is matched independent of a prefix, such as additional information or a timestamp. 

    12,34,56;
    Some text 12,34,56;
    2024-01-01 01:01:01 12,34,56;
    
    -> [12, 34, 56]

2D arrays are recognized when sent in the same line.

    123,234,345;678,789,890;
    Some text 123,234,345;678,789,890;
    2024-01-01 01:01:01 123,234,345;678,789,890;

    -> [[123, 234, 345], [678, 789, 890]]

## Scripts

**continuous_matrix.py**: Continuous data recording and display. Somewhat similar to live view but uses averaged data and saves it.

**live_matrix.py**: Live view of 2D data in a matrix using a colorbar.

**live_plot.py**: Live view using a plot with separate y-axis.

**noise.py**: Noise measurement and analysis.

**repeated_matrix.py**: Repeated measurements, each started manually.

**scaling.py**: Tool to measure and set the scaling of a large matrix.


## Functionality

Start using the correct port

    serialData = SerialData('/dev/ttyACM0')

### Data Function

Set a data function to be is applied before anything else. This is usefull when for example the reciprocal of the recieved data is to be used.

    data_function = lambda _data: 1 / _data
    serialData.set_data_function(data_function)

### Offset

Fix the measured value to zero (or a defined target value).

Measure or load offset. Typically used for a sensor matrix to record the dark frame just before or after the picture frame. 

    # Measure current offset
    offset_count = 10
    # offset_targetValue = 0
    serialData.measure_offset(offset_count)

Load stored or save measured offset

    # serialData.load_offset()
    # serialData.save_offset()

### Scaling

Scale the measured value to a target value

Load stored or save measured scaling

    serialData.load_scaling()
    serialData.save_scaling()

### Data Averaging

Data averaging

### Selecting Data to Plot

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


### Noise Analysis

Noise analysis and plots


## License

Licensed under the Apache License. See `LICENSE` for more information.

