from dataclasses import dataclass


@dataclass
class Padding:
	top: float = 0
	bottom: float = 0
	left: float = 0
	right: float = 0


@dataclass
class Spacing:
	horizontal: int = 0
	vertical: int = 0


@dataclass
class Position:
	x: float = 0
	y: float = 0
