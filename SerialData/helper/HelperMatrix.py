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


class HelperMatrix:

    def split_figure(self, number: int, max_panels: int = 40) -> tuple[int,]:
        ''' 
        Split long matrix into multiple parts/figures for display
        Defaults to max. 40 = 8x5 panels per figure, thus will essentially stay between 6x4 and 8x5
        '''
        _fig_count = np.ceil(number / max_panels)
        _target_panel_count_per_fig = np.ceil(number / _fig_count)
        imgsX, imgsY = self._almost_factors(_target_panel_count_per_fig)
        panel_count_per_fig = imgsX * imgsY
        return imgsX, imgsY, panel_count_per_fig

    def _close_factors(self, number: int) -> tuple[int,]:
        ''' 
        Find the closest pair of factors for a given number
        '''
        factor1 = 0
        factor2 = number
        while factor1 +1 <= factor2:
            factor1 += 1
            if number % factor1 == 0:
                factor2 = number // factor1
            
        return int(factor1), int(factor2)

    def _almost_factors(self, number: int) -> tuple[int,]:
        '''
        Find a pair of factors that are close enough for a number that is close enough
        '''
        while True:
            factor1, factor2 = self._close_factors(number)
            if 1/2 * factor1 <= factor2: # the fraction in this line can be adjusted to change the threshold aspect ratio
                break
            number += 1
        return factor1, factor2

helperMatrix: HelperMatrix = HelperMatrix()
