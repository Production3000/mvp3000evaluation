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

import numpy as np
import os
import re
import time
import serial
import time
from datetime import datetime
from threading import Thread, Event

from SerialData.classes.Data import Data
from SerialData.classes.DataMean import DataMean
from SerialData.classes.Noise import Noise


class SerialData:

    _ser: serial.Serial
    __stopped: bool = False

    ### Data collection
    data: Data = None
    mean: DataMean = None

    _data_function = lambda _, _data: _data # two arguments passed

    _counter: int = 0
    _avg_count: int = 0 # Rolling average

    ### Data events for display, do not use for data acquisition
    new_data_event: Event = Event()
    _first_data_event: Event = Event()
    _avg_count_reached_event: Event = Event()
    _noise_calculated_event: Event = Event()

    # Data dimensions
    _shape: tuple = None
    size: int = None
    def sizeX(self) -> int:
        return self._shape[1] # For some reason the X,Y are flipped in Python
    def sizeY(self) -> int:
        return self._shape[0] # For some reason the X,Y are flipped in Python

    ### Offset, scaling
    _offset: np.ndarray = None
    _scaling: np.ndarray = None

    ### Noise
    noise: Noise = None


    def __init__(self, port: str, avg_count: int = 3):
        """
        Continously reads from serial port and parses data received in CSV format.
            # this data function should typically be done on the ESP
        """
        self._avg_count = max(avg_count, 2) # At least 2 for averaging
        self.start_serial(port)


### Main serial data ##########################################################################

    def stop_serial(self, _ = None) -> None:
        # Set stop flag for while loop
        self.__stopped = True
        self._ser.close()
        print("Serial closed.")

    def start_serial(self, port: str) -> None:
        self.__stopped = False
        self._ser = serial.Serial(port, 115200, timeout=1)
        Thread(target=self._serial_thread, args=(self._ser,)).start()
        print("Serial opened.")

    def wait_for_serial(self) -> None:
        while self._first_data_event.is_set() is False:
            print("Waiting for serial data ...")
            time.sleep(1)

    def _serial_thread(self, ser: serial.Serial) -> None:
        """
        Read data from the serial port and convert it to a numpy array.
        Start in thread for continous read.
        """

        # Clear any serial buffer, read possbily partial first line
        ser.flushInput()
        ser.readline()

        _line = ''
        while True:
            # Check for stop flag
            if self.__stopped is True:
                break

            try:
                _line = ser.readline().decode('utf-8').strip()
            except:
                continue

            if _line == '': # Ignore empty lines
                continue

            # Strip any ANSI codes
            _line = re.sub(r'\x1b\[[\d;]*\d+m', '', _line)
            # _line = re.sub(r'\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?', '', _line)

            # Ignore messages not matching expected CSV content
            #   0:07:42 [D] -13,-124,333;-13,-124,333;
            #   -13,-124,333;-13,-124,333;
            _newData = re.search(r"(?:[-?\d+{,|;}]*-?\d+;)", _line)
            if _newData is None:
                continue

            try:
                _data = np.array([list(map(float, row.split(','))) for row in _newData[0].split(';') if row])
            except:
                print("Data not numpy array.") # This should never happen
                continue

            # Apply any data conversion, e.g. 1/data ...
            _data = self._data_function(_data)

            # Called during first run and after clear_data()
            if self.data is None:

                if len(_data.shape) > 2:
                    continue
                self._shape = _data.shape
                self.size = _data.size

                # Init offset, scaling on very first run but only if not set
                if self._offset is None:
                    self._offset = np.zeros(self._shape)
                if self._scaling is None:
                    self._scaling = np.ones(self._shape)

                self.data = Data(self._offset, self._scaling)
                self.mean = DataMean(self._offset, self._scaling, self._avg_count, self._avg_count_reached_event)

                self._first_data_event.set()

            # Update data storing classes
            self.data.update(_data)
            self.mean.update(_data)

            if self.noise is not None:
                self.noise.update(self.data.scaled(), self.mean.scaled())

            # Set the event flag
            self.new_data_event.set()



            # Increment counter, this is done at the end because of this stupid indexing from 0
            self._counter += 1


### General ##########################################################################

    def restart_data_acquisition(self) -> None:
        self._clear_data()
        # Wait for first measurement to not mess up plots
        self._first_data_event.wait()

    def set_data_function(self, data_function) -> None:
        self._data_function = data_function
        self._clear_data()

    def _clear_data(self) -> None:
        self.data = None
        self.mean = None

        self.new_data_event.clear()
        self._first_data_event.clear()
        self._avg_count_reached_event.clear()

        self._counter = 0


### Offset, Scaling, Noise ##########################################################################

    path_to_data = "data/"
    path_to_offset = f"{path_to_data}/offset/"
    path_to_scaling = f"{path_to_data}/scaling/"

    def measure_noise(self, noise_max_count: int = 100) -> None:
        self.noise = Noise(noise_max_count, self._noise_calculated_event)
        print("Measuring noise ...")
        self._measure_mean_with_progress(noise_max_count)

        # Measuring done, wait for calculation to finish
        self._noise_calculated_event.wait()

        # Save recorded noise data
        self.write_timestamped_csv(self.noise.uncertainty, "noise_u")
        self.write_timestamped_csv(self.noise.data_historic, "noise_datas")
        self.write_timestamped_csv(self.noise.mean_historic, "noise_means")
        self.write_timestamped_csv(self.noise.timings, "noise_timings")

    def measure_offset(self, avgCountOffset: int = 10, targetValue: int = 0) -> None:
        print("Measuring offset ...")
        self._measure_mean_with_progress(avgCountOffset)

        # Offset is just the mean data minus target value
        self._offset = self.mean.raw() - targetValue

        # Restart data acquisition
        self.restart_data_acquisition()

    def measure_scaling(self, index: int, targetValue: int, avgCountScaling: int = 10) -> None:
        print("Measuring scaling ...")
        self._measure_mean_with_progress(avgCountScaling)

        # Calculate scaling factor
        if len(self._shape) == 1:
            self._scaling[index] = targetValue / self.mean.offcor()[index]
        if len(self._shape) == 2:
            _row = index // self.sizeX()
            _col = index % self.sizeX()
            self._scaling[_row, _col] = targetValue / self.mean.offcor()[_row, _col]

        # Restart data acquisition
        self.restart_data_acquisition()

    def _measure_mean_with_progress(self, avg_count: int) -> None:
        # Remember averaging count
        _sample_avg_count = self._avg_count

        # Start averaging
        self._avg_count = avg_count
        self._clear_data()

        while self._avg_count_reached_event.is_set() is False:
            # Wait for measurement
            self.new_data_event.wait()
            self.new_data_event.clear()
            print(f"{self._counter}/{avg_count}", end='\r')

        # Set averaging to original count
        self._avg_count = _sample_avg_count

    def load_offset(self) -> None:
        _offset = self._read_npy(f"{self.path_to_offset}offset")
        if _offset is not None:
            self.set_offset(_offset)
        else:
            print("Offset not found.")

    def save_offset(self) -> None:
        self._write_npy(self._offset, f"{self.path_to_offset}offset")
        print("Offset saved.")

    def set_offset(self, offset: np.ndarray) -> None:
        if offset.shape == self._offset.shape:
            print("Offset loaded.")
            self._offset = offset
            self._clear_data()
            # Wait for measurements to start to not mess with plot and such
            self._first_data_event.wait()
        else:
            print("Warning: Offset shape mismatch.")

    def load_scaling(self) -> None:
        _scaling = self._read_npy(f"{self.path_to_scaling}scaling")
        if _scaling is not None:
            self.set_scaling(_scaling)
        else:
            print("Scaling not found.")
            print(f"{self.path_to_scaling}scaling")

    def save_scaling(self) -> None:
        self._write_npy(self._scaling,f"{self.path_to_scaling}scaling")
        print("Scaling saved.")

    def set_scaling(self, scaling: np.ndarray) -> None:
        if scaling.shape == self._scaling.shape:
            print("Scaling loaded.")
            self._scaling = scaling
            self._clear_data()
            # Wait for measurements to start to not mess with plot and such
            self._first_data_event.wait()
        else:
            print("Warning: Scaling shape mismatch.")


### Read, write files ##########################################################################

    def _read_npy(self, filename: str) -> np.ndarray:
        # Load and return the array from the file
        filename = f"{filename}.npy"
        if os.path.exists(filename):
            return np.load(filename)
        return None

    def _write_npy(self, array: np.ndarray, filename: str) -> None:
        _extension = ".npy"
        _fullfilename = filename + _extension

        # Check if the file exists, rename using incremental counter if so
        if os.path.exists(_fullfilename):
            os.rename(_fullfilename, self._get_next_filename(filename, _extension))

        # Save the array to a file
        np.save(_fullfilename, array)
        print(f"Array saved to {_fullfilename}")

    def write_incremental_csv(self, array: np.ndarray, filename: str) -> None:
        # All files are numbered, there is no not-numbered first file
        _extension = ".csv"
        np.savetxt(self._get_next_filename(f"{self.path_to_data}{filename}", _extension), array, delimiter=",")
        # array = np.loadtxt(filename, delimiter=",")

    def write_timestamped_csv(self, array: np.ndarray, filename: str) -> None:
        _extension = ".csv"
        # Get the current date and time in ISO format
        _timestamp = datetime.now().isoformat(timespec='seconds') # 'timespec' for Python 3.6+
        _fullfilename = f"{self.path_to_data}{filename}_{_timestamp}{_extension}"
        # Any existing file is just overwritten without warning
        np.savetxt(_fullfilename, array, delimiter=",")

    def _get_next_filename(self, filename: str, extension: str) -> None:
        # Check if the file exists, and find the next available filename if so
        _counter = 1
        _filename = f"{filename}_{_counter}{extension}"
        while os.path.exists(_filename):
            _filename = f"{filename}_{_counter}{extension}"
            _counter += 1
        return _filename
