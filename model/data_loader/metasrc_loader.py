from typing import Dict
import model.utils.data_scrape as ds
from model.data_loader import APILoader
from utils import Lanes
from time import time


class MetasrcLoader(APILoader):
	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

	def get_build(self, champion_id: int) -> Dict[str, Dict]:
		super().get_build(champion_id)

		def BuildByLane(page, queueName):
			build = ds.get_build(page, queue=queueName)
			if not build['exists']:
				return False, {}, {}
			championLane = dict()
			championLane['spells'] = [self.lol_adapter.getImageFromUrl(self.lol_adapter.allSpells[build['spells'][i]]['iconPath']) for i in range(2)]
			championLane['ability_order'] = build['abilities_order']
			championLane['runes'] = self.lol_adapter.get_rune_mapping(build['runes'])
			championLane['items'] = [
				[{'image': self.lol_adapter.get_item_image(item), 'description': self.lol_adapter.allItems[item]['iconDesc'], 'count': count}
				 for item, count in zip(build['start_items'], build['start_items_n'])],
				[{'image': self.lol_adapter.get_item_image(item), 'description': self.lol_adapter.allItems[item]['iconDesc'], 'count': 1} for
				 item in build['best_items']]]  # TEST
			championLane['wr'] = build['wr']
			championLane['pr'] = build['pr']
			championLane['br'] = build['br']

			return True, championLane, build

		champion_info = self.lol_adapter.getChampionInfo(champion_id)
		queueName = ''
		if not self.mode:
			queueName = self.lol_adapter.getQueueSpecialName()

		champion = dict()
		champion['build'] = {}
		champion['name'] = champion_info['name']
		champion['image'] = champion_info['iconPath']
		champion['abilities'] = [{'name': '', 'icon': ability} for ability in self.lol_adapter.getAbilitiesIcons(champion_id)]

		start = time()
		pages = ds.load_pages(queueName, champion_info['alias'])

		for lane in Lanes:
			exists, championLane, build = BuildByLane(pages[lane.value], queueName)
			if exists:
				champion['build'][lane] = [championLane, build]
		print(f'Champion builds took {time() - start}')

		champion['default_lane'] = ds.getDefaultLane(pages[''])
		return champion
