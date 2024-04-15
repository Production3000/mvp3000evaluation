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
from threading import Event


class Data:
    _offset: np.ndarray = None
    _scaling: np.ndarray = None

    _data: np.ndarray = None

    _fmax: np.ndarray = None
    _fmin: np.ndarray = None

    def __init__(self, offset: np.ndarray, scaling: np.ndarray) -> None:
        self._offset = offset
        self._scaling = scaling

        self._fmax = np.full_like(offset, -2**32)
        self._fmin = np.full_like(offset, 2**32)

    def update(self, data: np.ndarray) -> None:
        self._data = data
        # Update forever min/max
        self._fmax = np.fmax(self._fmax, self._data)
        self._fmin = np.fmin(self._fmin, self._data)

    # Read raw, offset corrected, or scaled data
    def raw(self) -> np.ndarray:
        return self._data
    def offcor(self) -> np.ndarray:
        return self._data + self._offset
    def scaled(self) -> np.ndarray:
        return (self._data + self._offset) * self._scaling
    
    # Min/max integer over all elements of current data    
    def minmax_raw(self) -> tuple[int, int]:
        return np.min(self._data), np.max(self._data)
    def minmax_scaled(self) -> tuple[int, int]:
        return np.min(self.scaled()), np.max(self.scaled())

    # Forever min/max array of current and previous data
    def max_forever_raw_array(self) -> np.ndarray:
        return self._fmax
    def min_forever_raw_array(self) -> np.ndarray:
        return self._fmin
    def max_forever_scaled_array(self) -> np.ndarray:
        return (self._fmax + self._offset) * self._scaling
    def min_forever_scaled_array(self) -> np.ndarray:
        return (self._fmin + self._offset) * self._scaling
    # Forever min/max integer over all elements of current and previous data
    def minmax_forever_raw(self) -> tuple[int, int]:
        return np.min(self._fmin), np.max(self._fmax)
    def minmax_forever_scaled(self) -> tuple[int, int]:
        return np.min(self.min_forever_scaled_array()), np.max(self.max_forever_scaled_array())
