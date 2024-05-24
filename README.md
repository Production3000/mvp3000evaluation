# MVP3000 Evaluation

Welcome to the **MVP3000 Evaluation** repository, an integral part of the **MVP3000** rapid prototyping framework.

The **MVP3000** framework is written for and by very early stage startup projects/companies. It aims to streamline the development and testing of new sensor or manipulation hardware and the consecutive transfer from the basic concept to a minimum viable product (MVP), a demonstrator device, or an independent setup for applications like manufacturing process control. It is build around readily available low-cost hardware and open software solutions.

A key feature of the framework is the seamless transition between the different development stages. Starting with the initial proof-of-concept script on the engineers laptop with a serial connection to perform first data analysis, moving to a laptop-independent data collection via wireless network allowing longer-term studies, towards a controll device using a handheld Raspberry Pi with touchscreen.

The framework comprises three main repositories:
1.  **[MVP3000 ESP32/ESP8266](https://github.com/Production3000/mvp3000esp)** written in C++. It offers a web interface for main settings including data processing such as averaging, offset, and scaling, as well as data transfer options via serial interface or wireless to a MQTT broker.
2.  **[MVP3000 Controller](https://github.com/Production3000/mvp3000controller)**. Designed to run on a Raspberry Pi or a dedicated computer, this repository supports long-term data collection and demonstration capabilities independent of an engineer's laptop. It acts as MQTT broker and stores the recieved data in a MariaDB table. It includes a web kiosk interface for modern, touch-based user interactions.
3.  **MVP3000 Evaluation** written in Python. The class receives data either via the serial interface or from the MQTT broker and allows basic processing such as averaging, offset, and scaling on the client side. It includes a number of scripts to display the data, record single or repeated or continuous measurements, and to perform basic standard analysis.



## Scripts

Display:

`live_matrix.py`: Live view of 2D data in a matrix using a colorbar.

`live_plot.py`: Live view using a plot with separate y-axis.

Measurements:

`repeated_matrix.py`: Repeated measurements, each started after user confirmation. Data is saved to a CSV file.

`continuous_matrix.py`: Continuous data recording and display. Somewhat similar to live view but uses averaged data and saves it to a CSV file.   

Extra:

`noise.py`: Noise measurement and basic analysis: standard deviation, uncertainty, timing jitter.

`scaling.py`: Tool to measure and set the scaling of single sensors, particularly usefull for a large sensor matrix.



## Quick Start

Please refer to the documentation for detailed options. (once it is written)


### Installation

Download the repository into a local folder to run any of the scripts.


### Data Processing

#### Initiallization and Averaging

Initialize the class and start monitoring the serial port. Optionally provide an averaging count (defaults to 10).

    serialData = SerialData('COM2')
    
    avg_count = 10
    serialData = SerialData('COM2', avg_count)

#### Data Function

Set a data function to be is applied before anything else. This is usefull when for example the reciprocal of the recieved data is to be used.

    data_function = lambda _data: 1 / _data
    serialData.set_data_function(data_function)

#### Offset

Measure the offset on client side during script execution. Typically used for a sensor matrix to record the dark frame just before or after the picture frame. 

    # Measure current offset
    offset_count = 10
    offset_targetValue = 0
    serialData.measure_offset(offset_count, offset_targetValue)

Load stored and save measured offset.

    # serialData.load_offset()
    # serialData.save_offset()

#### Scaling

Load stored and save measured scaling.

    serialData.load_scaling()
    serialData.save_scaling()

There is a script *scaling.py* to measure and calculate the scaling factor.


### Display

#### Selecting Data to Plot

Select which data to plot: shot data, rolling average

    _data = serialData.data
    # _data = serialData.mean

Select data processing: raw, offset, scaled

    _array = _data.raw()
    # _array = _data.scaled()

Select axis limits: current shot raw or scaled, any shot raw or scaled 

    # _minmax = _data.minmax_raw()
    # _minmax = _data.minmax_scaled()
    _minmax = _data.minmax_forever_raw()
    # _minmax = _data.minmax_forever_scaled()



## Serial Port CSV Data Format

Generally any CSV formatted input can be used. Data is matched independent of a prefix, such as additional information or a timestamp.

    12,34,56;
    Some text 12,34,56;
    2024-01-01 01:01:01 12,34,56;
    
    -> [12, 34, 56]

2D arrays are recognized when sent in the same line.

    123,234,345;678,789,890;
    Some text 123,234,345;678,789,890;
    1997-08-29 06:14:00 123,234,345;678,789,890;

    -> [[123, 234, 345], [678, 789, 890]]



## License

Licensed under the Apache License. See `LICENSE` for more information.

Copyright Production 3000
