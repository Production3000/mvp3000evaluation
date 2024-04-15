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

from SerialData.classes.Data import Data


class DataMean(Data):
    # _data holds rolling mean
    _counter: int = 0

    _avg_count: int = -1
    avg_count_reached_event: Event = None

    def __init__(self, offset: np.ndarray, scaling: np.ndarray, avg_count:int, avg_count_reached_event: Event = None) -> None:
        super().__init__(offset, scaling) 
        self._avg_count = avg_count
        self.avg_count_reached_event = avg_count_reached_event

    def update(self, data: np.ndarray) -> None:
        self._counter += 1
        
        if self._counter == 1:
            super().update(data)
        elif self._counter < self._avg_count:
            # Dirty rolling average start, for example for measurement 5 with index 4: 4/5 old + 1/5 new
            super().update( (self._counter - 1)/self._counter * self._data + 1/self._counter * data )
        else:
            # Rolling average, for example for measurement 17 with index 16: 9/10 old + 1/10 new
            super().update( (self._avg_count - 1)/self._avg_count * self._data + 1/self._avg_count * data )

        # Targeted averaging count reached, let the world know
        if self._counter == self._avg_count and self.avg_count_reached_event is not None:
            self.avg_count_reached_event.set()
