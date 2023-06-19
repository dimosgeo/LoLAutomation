from dataclasses import dataclass, field
import numpy as np
from PIL import Image
import enum

palette = ['#0e0818', '#140e20', '#1d152d', '#22133a', '#2c114f']
background_color = palette[3]
transparent_color = '#fc5a8d'
widget_color = palette[4]
gray_array = np.array([0.3, 0.59, 0.11])


def grayscale(img):
    img = np.array(img, dtype='uint8')
    img[:, :, :3] = np.sum(img[:, :, :3] * gray_array, axis=-1, keepdims=True) / 3
    return Image.fromarray(img)


@dataclass
class Message:
    message_type: str = 'EMPTY'
    message: list = field(default_factory=list)



lane_indexes = {'top': 0, 'jungle': 1, 'mid': 2, 'adc': 3, 'support': 4, 'aram': 5}
lanes = ['top', 'jungle', 'mid', 'adc', 'support']#, 'aram']


class Lane(enum.Enum):
    top = 0
    jungle = 1
    mid = 2
    adc = 3
    support = 4
    aram = 5