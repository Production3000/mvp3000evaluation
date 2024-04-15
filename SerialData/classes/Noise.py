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
import time
from threading import Event


class Noise():
    
    data_historic: np.ndarray = None
    mean_historic: np.ndarray = None

    uncertainty: np.ndarray = None

    timings: np.ndarray = None
    _timing_start: int = 0
    
    _counter: int = 0
    _noise_count: int = 0 # Measurements to stop after
    x: np.ndarray = None

    noise_calculated_event: Event = None


    def __init__(self, noise_count:int, noise_calculated_event: Event = None) -> None:
        self._noise_count = noise_count
        self.noise_calculated_event = noise_calculated_event

        self.x = np.arange(1, self._noise_count + 1)
        self.timings = np.zeros(self._noise_count)


    def update(self, data: np.ndarray, mean: np.ndarray) -> None:
        self._counter += 1

        # Do nothing once count is reached
        if self._counter > self._noise_count:
            return
        
        # Init numpy arrays holding the data, plotting is simpler not having lists
        if self._counter == 1:
            self.data_historic = np.zeros((self._noise_count, data.size))
            self.mean_historic = np.zeros((self._noise_count, data.size))
            self.uncertainty = np.zeros((self._noise_count, data.size))
        
        _index = self._counter -1
        # Store data
        self.data_historic[_index] = data.flatten()
        self.mean_historic[_index] = mean.flatten()
        # Store timing
        self.timings[_index] = self._time_difference_ms()

        # Finished, calculate noise
        if self._counter == self._noise_count:
            self._calculate_uncertainty()
            self.noise_calculated_event.set()

    def _time_difference_ms(self) -> int:
        _now = round(time.time_ns() / 1000000)
        diff = _now - self._timing_start if (self._timing_start > 0) else 0
        self._timing_start = _now
        return diff
    
    def _calculate_uncertainty(self) -> None:
        _sum_squared_deviation: np.ndarray = np.zeros_like(self.data_historic[0])
        for i in range(1, self._counter):
            _N = i + 1
            # Standard deviation s = sqrt( 1/(N-1) SUM((data - mean)^2) )
            _sum_squared_deviation += ( self.mean_historic[i] - self.data_historic[i] )**2
            _s = np.sqrt( _sum_squared_deviation / (_N - 1) )
            # Uncertainty u = s / sqrt(N)
            self.uncertainty[i] =  _s / np.sqrt(_N) 
