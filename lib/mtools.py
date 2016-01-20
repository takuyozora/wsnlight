# -*- coding: utf-8 -*-
#
# This file provide math tool as numpy circular buffer
#

import numpy as np


class CircularBuffer(object):
    """
    This class provide a fast circular buffer
    """

    def __init__(self, size, dtype=np.int16):
        """
        :param size: Size of the buffer
        :return:
        """
        self.data = np.zeros(size, dtype=dtype)

    def put(self, elem):
        """
        Put an elem in the buffer
        :param elem:
        :return:
        """
        self.data = np.roll(self.data, 1)
        self.data[0] = elem