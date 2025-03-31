from dataclasses import dataclass, field
import numpy as np
from PIL import Image
from tkinter.font import Font
from enum import Enum

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


class Lanes(Enum):
	TOP = 'top'
	JUNGLE = 'jungle'
	MID = 'mid'
	BOT = 'adc'
	SUPPORT = 'support'
	FILL = 'fill'
	DEFAULT = ''


lane_indexes = {Lanes.TOP: 0, Lanes.JUNGLE: 1, Lanes.MID: 2, Lanes.BOT: 3, Lanes.SUPPORT: 4, Lanes.FILL: 5}


class StatusType(Enum):
	EMPTY = 'EMPTY'
	GAME_OPENED = 'GAME_OPENED'
	GAME_CLOSED = 'GAME_CLOSED'
	CHAMPION_PICKED = 'CHAMPION_PICKED'
	CHAMPION_LOCKED = 'CHAMPION_LOCKED'
	CHANGED_SKIN = 'CHANGED_SKIN'
	PROCESS_CLOSED = 'PROCESS_CLOSED'


class ServerStatus(Enum):
	OPEN = 'OPEN'
	CLOSED = 'CLOSED'


class ClientStatus(Enum):
	OPEN = 'OPEN'
	CLOSED = 'CLOSED'


@dataclass
class Message:
	message_type: StatusType = StatusType.EMPTY
	message: list = field(default_factory=list)
