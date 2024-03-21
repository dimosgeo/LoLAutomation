from dataclasses import dataclass, field
import numpy as np
from PIL import Image
from tkinter.font import Font

colors = {
	'background': '#22133a',
	'background_widget': '#0e0818',
	'widget_highlight': '#2c114f',
	'transparent': '#fc5a8d',
	'text': '#ffffff'
}

fonts = {}
gray_array = np.array([0.3, 0.59, 0.11])


def init_fonts():
	fonts['title'] = Font(family='Helvetica', size=28, weight='bold')
	fonts['normal_bold'] = Font(family='Helvetica', size=14, weight='bold')
	fonts['normal'] = Font(family='Helvetica', size=14)
	fonts['small'] = Font(family='Helvetica', size=12)
	fonts['small_bold'] = Font(family='Helvetica', size=12, weight='bold')


def grayscale(img):
	img = np.array(img, dtype='uint8')
	img[:, :, :3] = np.sum(img[:, :, :3] * gray_array, axis=-1, keepdims=True) / 3
	return Image.fromarray(img)


@dataclass
class Message:
	message_type: str = 'EMPTY'
	message: list = field(default_factory=list)


lane_indexes = {'top': 0, 'jungle': 1, 'mid': 2, 'adc': 3, 'support': 4, 'aram': 5}
lanes = ('top', 'jungle', 'mid', 'adc', 'support')
