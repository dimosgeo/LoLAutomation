from abc import ABC, abstractmethod
from typing import Dict, Optional

from model.utils.LoLAutomationLib import LoLAdapter


class APILoader(ABC):
	def __init__(self, adapter: LoLAdapter, mode: Optional[int] = None) -> None:
		self.mode = mode
		self.lol_adapter: LoLAdapter = adapter

	@abstractmethod
	def get_build(self, champion_id: int) -> Dict[str, Dict]:
		pass
