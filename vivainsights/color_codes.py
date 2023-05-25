# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# The above code defines an Enum class for colors and creates two color palettes using the defined
# colors.
from enum import Enum

class Colors(Enum):
    PRIMARY = '#1d627e'
    HIGHLIGHT_POSITIVE = '#34b1e2'
    HIGHLIGHT_NEGATIVE = '#fe7f4f'
    POSITIVE_ALT_1 ='#bfe5ee'
    POSITIVE_ALT_2 = '#b4d5dd'
    POSITIVE_ALT_3 = '#adc0cb'
    NEGATIVE_ALT_1 = '#fcf0eb'
    NEGATIVE_ALT_2 = '#fbdacd'
    NEGATIVE_ALT_3 = '#facebc'
    NON_HIGHLIGHT = '#e1e1e1'

COLOR_PALLET_ALT_1 = [
    Colors.PRIMARY.value,
    Colors.HIGHLIGHT_POSITIVE.value,
    Colors.HIGHLIGHT_NEGATIVE.value,
    Colors.POSITIVE_ALT_1.value,
    Colors.POSITIVE_ALT_2.value,
    Colors.POSITIVE_ALT_3.value,
    Colors.NEGATIVE_ALT_1.value,
    Colors.NEGATIVE_ALT_2.value,
    Colors.NEGATIVE_ALT_3.value,
    Colors.NON_HIGHLIGHT.value
    ]

COLOR_PALLET_ALT_2 = [
    Colors.PRIMARY.value,
    Colors.HIGHLIGHT_POSITIVE.value,
    Colors.HIGHLIGHT_NEGATIVE.value,
    Colors.POSITIVE_ALT_1.value,
    Colors.NEGATIVE_ALT_1.value,
    Colors.NON_HIGHLIGHT.value
    ]
