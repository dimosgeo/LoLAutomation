from dataclasses import dataclass, field
import numpy as np
from PIL import Image

background_color = "#2E3349"
transparent_color = '#fc5a8d'
gray_array = np.array([0.3, 0.59, 0.11])


def grayscale(img):
    img = np.array(img, dtype='uint8')
    img[:, :, :3] = np.sum(img[:, :, :3] * gray_array, axis=-1, keepdims=True) / 3
    return Image.fromarray(img)


@dataclass
class Message:
    message_type: str = 'EMPTY'
    message: list = field(default_factory=list)
