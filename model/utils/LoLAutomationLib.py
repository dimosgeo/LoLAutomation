import requests
import pythoncom
import wmi
import socket
import io
import argparse
from utils.svg import SVG
import aiohttp
import asyncio
import platform


requests.packages.urllib3.disable_warnings()


def parse_arguments(args):
	parser = argparse.ArgumentParser()
	parser.add_argument('name', type=str)
	parser.add_argument('--riotclient-auth-token', type=str)
	parser.add_argument('--riotclient-app-port', type=str)
	parser.add_argument('--no-rads', action='store_true')
	parser.add_argument('--disable-self-update', action='store_true')
	parser.add_argument('--region', type=str)
	parser.add_argument('--locale', type=str)
	parser.add_argument('--riotgamesapi-standalone', action='store_true')
	parser.add_argument('--riotgamesapi-settings', type=str)
	parser.add_argument('--rga-lite', action='store_true')
	parser.add_argument('--remoting-auth-token', type=str)
	parser.add_argument('--respawn-command', type=str)
	parser.add_argument('--respawn-display-name', type=str)
	parser.add_argument('--app-port', type=str)
	parser.add_argument('--install-directory', type=str)
	parser.add_argument('--app-name', type=str)
	parser.add_argument('--ux-name', type=str)
	parser.add_argument('--ux-helper-name', type=str)
	parser.add_argument('--log-dir', type=str)
	parser.add_argument('--crash-reporting', type=str)
	parser.add_argument('--crash-environment', type=str)
	parser.add_argument('--app-log-file-path', type=str)
	parser.add_argument('--app-pid', type=str)
	parser.add_argument('--output-base-dir', type=str)
	parser.add_argument('--no-proxy-server', action='store_true')
	parser.add_argument('--ignore-certificate-errors', action='store_true')
	return parser.parse_known_args(args)[0]


def get_client_url(process_name="LeagueClientUx.exe"):
	pythoncom.CoInitialize()
	client = wmi.WMI().Win32_Process(name=process_name)
	client = client[0]
	arguments = client.CommandLine[1:-1].split('" "')
	args = parse_arguments(arguments)
	token = args.remoting_auth_token
	port = args.app_port
	riot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	riot_socket.close()
	url = f"https://riot:{token}@127.0.0.1:{port}"
	return url


def getClientStatus(process_name="LeagueClientUx.exe"):
	pythoncom.CoInitialize()
	client = wmi.WMI().Win32_Process(name=process_name)
	return len(client) != 0


class LoLAdapter:
	def __init__(self) -> None:
		self.url = get_client_url()
		self.loadedItems = {}
		self.allItems = {}
		self.allRunes = None
		self.allSpells = None
		self.allItems = None
		self.rune_mapping = {}
		self.getRunes()
		self.getSpells()
		self.getItems()
		self.create_default_mapping()

	def create_default_mapping(self) -> None:
		if len(self.rune_mapping) > 0:
			return

		for key in self.allRunes:
			for row_num, row in enumerate(self.allRunes[key]['slots'], start=1):
				number = row_num
				if row_num > 4:
					number -= 5
				for index, rune in enumerate(row):
					self.rune_mapping[rune] = (number, index)

		self.rune_mapping[8000] = (0, 0)
		self.rune_mapping[8100] = (0, 1)
		self.rune_mapping[8200] = (0, 2)
		self.rune_mapping[8400] = (0, 3)
		self.rune_mapping[8300] = (0, 4)

	def get_rune_mapping(self, runes):
		complete_runes = []
		for index, part in enumerate(runes):
			if index < 2:
				result = [-1 for _ in range(5)]
			else:
				result = [-1 for _ in range(3)]

			for row, rune in enumerate(part):
				data = self.rune_mapping[rune]

				if index == 2:
					result[row] = data[1]
				else:
					result[data[0]] = data[1]

			complete_runes.append(result)

		return complete_runes

	def get_item_image(self, item):
		if item not in self.loadedItems:
			self.loadedItems[item] = self.getImageFromUrl(self.allItems[item]['iconPath'])
		return self.loadedItems[item]

	def getImageFromUrl(self, img_path):
		path = self.url + img_path
		return io.BytesIO(requests.get(path, verify=False).content)

	async def getImageFromUrlAsync(self, session, img_path):
		path = self.url + img_path
		async with session.get(path, ssl=False) as r:
			return await r.read()

	async def getAllImagesFromUrl(self, perk, perks):
		async with aiohttp.ClientSession() as session:
			tasks = [self.getImageFromUrlAsync(session, perks[p]['iconPath']) for p in perk]
			return await asyncio.gather(*tasks)

	def getLobbyQueue(self):
		path = self.url + "/lol-lobby/v2/lobby"
		return requests.get(path, verify=False).json()["gameConfig"]["gameMode"].lower()

	def getQueueSpecialName(self):
		queue = self.getLobbyQueue()
		if "spellbook" in queue:
			return "ultbook"
		elif "aram" in queue:
			return "aram"
		elif "urf" in queue:
			return "urf"
		return "5v5"  # "gameMode": "CLASSIC"

	def checkIfChampionSelect(self):
		champion_select = self.url + "/lol-champ-select/v1/current-champion"
		r = requests.get(champion_select, verify=False)
		if r.status_code != 200 or r.json() == 0:
			return False
		return True

	def getPerks(self):
		path = self.url + "/lol-perks/v1/perks"
		r = requests.get(path, verify=False).json()

		perks = {}
		for perk in r:
			perks[perk['id']] = {'iconPath': perk['iconPath']}
		return perks

	def getRunes(self) -> None:
		path = self.url + "/lol-perks/v1/styles"
		r = requests.get(path, verify=False).json()

		# Precision, Domination, Sorcery, Inspiration, Resolve
		rune_colors = {8000: [200, 170, 110],
		               8100: [220, 71, 71],
		               8200: [108, 117, 245],
		               8300: [72, 180, 190],
		               8400: [164, 208, 141]}
		self.allRunes = {}
		for s in r:
			slots = [x['perks'] for x in s['slots']]
			# runes[s['id']] = {'slots': slots, 'iconPath': s['iconPath'], 'color':rune_colors[s['id']]}
			self.allRunes[s['id']] = {'slots': slots, 'iconPath': s['assetMap']['svg_icon'], 'color': rune_colors[s['id']]}

	def getAbilitiesIcons(self, cid):
		path = self.url + "/lol-game-data/assets/v1/champions/" + str(cid) + ".json"
		r = requests.get(path, verify=False).json()

		return (self.getImageFromUrl(r["passive"]["abilityIconPath"]),
		        self.getImageFromUrl(r["spells"][0]["abilityIconPath"]),
		        self.getImageFromUrl(r["spells"][1]["abilityIconPath"]),
		        self.getImageFromUrl(r["spells"][2]["abilityIconPath"]),
		        self.getImageFromUrl(r["spells"][3]["abilityIconPath"]))

	def getSpells(self):
		path = self.url + "/lol-game-data/assets/v1/summoner-spells.json"
		r = requests.get(path, verify=False).json()
		self.allSpells = {}
		for spell in r:
			self.allSpells[spell['id']] = {'iconPath': spell['iconPath']}

	def getItems(self):
		path = self.url + "/lol-game-data/assets/v1/items.json"
		r = requests.get(path, verify=False).json()
		self.allItems = {}
		for item in r:
			self.allItems[item['id']] = {'iconPath': item['iconPath'], 'iconDesc': item['name']}

	def updateItemSet(self, start_items, best_items, title='AUTOSET'):
		sid = self.getSummonerId()['sid']
		path = self.url + "/lol-item-sets/v1/item-sets/" + str(sid) + "/sets"
		all_item_sets = requests.get(path, verify=False).json()["itemSets"]

		item_set = {"associatedChampions": [], "associatedMaps": [11, 12], "blocks": [], "map": "", "mode": "",
		            "preferredItemSlots": [], "sortrank": 0, "startedFrom": "blank", "title": title, "type": "custom",
		            "uid": ""}

		item_set["blocks"].append(
			{"hideIfSummonerSpell": "", "items": [{"count": 1, "id": str(item)} for item in start_items],
			 "showIfSummonerSpell": "", "type": 'Start'})
		item_set["blocks"].append(
			{"hideIfSummonerSpell": "", "items": [{"count": 1, "id": str(item)} for item in best_items],
			 "showIfSummonerSpell": "", "type": 'Best Items'})

		for i in range(len(all_item_sets)):
			if all_item_sets[i]["title"] == "AUTOSET":
				all_item_sets[i] = item_set

		put_sets = self.url + "/lol-item-sets/v1/item-sets/" + str(sid) + "/sets"
		requests.put(put_sets, verify=False, json={"itemSets": all_item_sets})

	def setSpells(self, spells):
		path = self.url + "/lol-champ-select/v1/session/my-selection"
		requests.patch(path, verify=False, json={"spell1Id": spells[0], "spell2Id": spells[1]})

	def setSkin(self, skinid):
		path = self.url + "/lol-champ-select/v1/session/my-selection"
		requests.patch(path, verify=False, json={"selectedSkinId": skinid})

	def setRunes(self, runes, title='AUTORUNES'):
		rune_page_id = 0
		path = self.url + "/lol-perks/v1/pages"
		pages = requests.get(path, verify=False).json()
		for page in pages:
			if page["name"] == "AUTORUNES":
				rune_page_id = page["id"]

		path = self.url + "/lol-perks/v1/pages/" + str(rune_page_id)
		requests.delete(path, verify=False)
		path = self.url + "/lol-perks/v1/pages/"
		requests.post(path, verify=False, json={"name": title, "primaryStyleId": runes[0][0], "subStyleId": runes[1][0],
		                                        "selectedPerkIds": runes[0][1:] + runes[1][1:] + runes[2]})

	def getLaneName(self):
		sid = self.getSummonerId()['sid']
		path = f'{self.url}/lol-champ-select/v1/session'
		r = requests.get(path, verify=False).json()
		team = r['myTeam']
		for player in team:
			if player['summonerId'] == sid:
				return player['assignedPosition'].upper()
		return 'TOP'

	def getLaneSpecialName(self):
		laneName = self.getLaneName()
		if laneName == '':
			return 'top'

		laneName = laneName.lower()
		if laneName == 'middle':
			return 'mid'
		elif laneName == 'bottom':
			return 'adc'
		elif laneName == 'utility':
			return 'support'
		return laneName

	def getSummonerId(self):
		path = f"{self.url}/lol-summoner/v1/current-summoner"
		r = requests.get(path, verify=False).json()
		return {'sid': r['summonerId'], 'name': r['displayName']}

	def getSpellsIds(self):
		path = self.url + "/lol-champ-select/v1/session/"
		r = requests.get(path, verify=False).json()

		sid = self.getSummonerId()['sid']

		for player in r['myTeam']:
			if player['summonerId'] == sid:
				return [player['spell1Id'], player['spell2Id']]

		return [0, 0]

	def getCurrentChampion(self):
		path = self.url + "/lol-champ-select/v1/session/"
		r = requests.get(path, verify=False).json()

		cell_id = r.get('localPlayerCellId', -1)
		if cell_id != -1:
			if r['actions']:
				for player in r['actions'][0]:
					if player['actorCellId'] == cell_id:
						return player['championId'], player['completed']
			else:
				for player in r['myTeam']:
					if player['cellId'] == cell_id:
						return player['championId'], True

		return -1, False

	def getChampionInfo(self, cid):
		path = self.url + "/lol-game-data/assets/v1/champions/" + str(cid) + ".json"
		r = requests.get(path, verify=False).json()
		name = r["name"]
		alias = r["alias"].lower()
		icon_path = self.getImageFromUrl(r["squarePortraitPath"])

		return {'name': name, 'alias': alias, 'iconPath': icon_path}

	def getFullRunePageImages(self):
		perks = self.getPerks()

		allRunes = [[]]
		if platform.system() == 'Windows':
			asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
		stats = [[io.BytesIO(img) for img in asyncio.run(self.getAllImagesFromUrl(perk, perks))] for perk in self.allRunes[8000]['slots'][-3:]]
		runesOrder = [8000, 8100, 8200, 8400, 8300]
		colors = ['#c8aa6e', '#dc4747', '#6c75f5', '#a4d08d', '#48b4be']

		for rune, color in zip(runesOrder, colors):
			page = self.allRunes[rune]['slots']
			# print(SVG(requests.get(url+runes[rune]['iconPath'], verify=False).content))
			icon = SVG(requests.get(self.url + self.allRunes[rune]['iconPath'], verify=False).content)
			icon.set(facecolor=color)
			allRunes[0].append(icon.buffer)
			# allRunes[0].append(getImageFromUrl(url, runes[rune]['iconPath']))
			allRunes.append(
				[[io.BytesIO(img) for img in asyncio.run(self.getAllImagesFromUrl(perk, perks))] for perk in page[:-3]])
		allRunes.append(stats)
		return allRunes

	def getSkins(self):
		path = self.url + "/lol-champ-select/v1/skin-selector-info"
		result = {"selectedSkinId": -1, "availableSkins": []}
		try:
			selected = requests.get(path, verify=False).json()
			selectedChampion = selected['selectedChampionId']
			result['selectedSkinId'] = selected['selectedSkinId']

			path = self.url + "/lol-champ-select/v1/pickable-skin-ids"
			all_skins = requests.get(path, verify=False).json()

			path = self.url + f"/lol-game-data/assets/v1/champions/{selectedChampion}.json"
			skins = requests.get(path, verify=False).json()['skins']
			result['availableSkins'] = {skin['id']: self.getImageFromUrl(skin['uncenteredSplashPath']) for skin in skins if
			                            skin['id'] in all_skins or skin['isBase']}
		except Exception as e:
			print(f'Error: {e}')
		return result


def main():
	url = get_client_url()
	print(url)


# getFullRunePageImages(url)
# getRunes(url)
# print(getItems(url))


if __name__ == '__main__':
	main()
