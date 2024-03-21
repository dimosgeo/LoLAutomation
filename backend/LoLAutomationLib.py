import requests
import pythoncom
import wmi
import socket
import io
import argparse
from utils.svg import SVG 


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


def getImageFromUrl(url, img_path):
	path = url+img_path
	return io.BytesIO(requests.get(path, verify=False).content)


def getLobbyQueue(url):
	path = url+"/lol-lobby/v2/lobby"
	return requests.get(path, verify=False).json()["gameConfig"]["gameMode"].lower()


def getQueueSpecialName(url):
	queue = getLobbyQueue(url)
	if "spellbook" in queue:
		return "ultbook"
	elif "aram" in queue:
		return "aram"
	elif "urf" in queue:
		return "urf"
	return "5v5"	#"gameMode": "CLASSIC"


def checkIfChampionSelect(url):
	champion_select = url+"/lol-champ-select/v1/current-champion"
	r = requests.get(champion_select, verify=False)
	if r.status_code != 200 or r.json() == 0:
		return False
	return True


def getPerks(url):
	path = url+"/lol-perks/v1/perks"
	r = requests.get(path, verify=False).json()
	
	perks = {}
	for perk in r:
		perks[perk['id']] = {'iconPath': perk['iconPath']}
	return perks	


def getRunes(url):
	path = url+"/lol-perks/v1/styles"
	r = requests.get(path, verify=False).json()	

	#Precision, Domination, Sorcery, Inspiration, Resolve
	rune_colors = {8000:[200, 170, 110], 8100:[220, 71, 71], 8200:[108, 117, 245], 8300:[72, 180, 190], 8400:[164, 208, 141]}
	runes = {}
	for s in r:
		slots = [x['perks'] for x in s['slots']]
		# runes[s['id']] = {'slots': slots, 'iconPath': s['iconPath'], 'color':rune_colors[s['id']]}
		runes[s['id']] = {'slots': slots, 'iconPath': s['assetMap']['svg_icon'], 'color':rune_colors[s['id']]}
	return runes


def getAbilitiesIcons(url, cid):
	path = url+"/lol-game-data/assets/v1/champions/"+str(cid)+".json"
	r = requests.get(path, verify=False).json()

	return [getImageFromUrl(url, r["passive"]["abilityIconPath"]), getImageFromUrl(url, r["spells"][0]["abilityIconPath"]), getImageFromUrl(url, r["spells"][1]["abilityIconPath"]), getImageFromUrl(url, r["spells"][2]["abilityIconPath"]), getImageFromUrl(url, r["spells"][3]["abilityIconPath"])]


def getSpells(url):
	path = url+"/lol-game-data/assets/v1/summoner-spells.json"
	r = requests.get(path, verify=False).json()
	spells = {}
	for spell in r:
		spells[spell['id']] = {'iconPath': spell['iconPath']}
	return spells


def getItems(url):
	path = url+"/lol-game-data/assets/v1/items.json"
	r = requests.get(path, verify=False).json()
	items = {}
	for item in r:
		items[item['id']] = {'iconPath': item['iconPath'], 'iconDesc': item['name']}
	return items


def updateItemSet(url, start_items, best_items, title='AUTOSET'):
	sid = getSummonerId(url)['sid']
	path = url+"/lol-item-sets/v1/item-sets/"+str(sid)+"/sets"
	all_item_sets = requests.get(path, verify=False).json()["itemSets"]

	item_set = {"associatedChampions": [], "associatedMaps": [11, 12], "blocks": [], "map": "", "mode": "", "preferredItemSlots": [], "sortrank": 0, "startedFrom": "blank", "title": title, "type": "custom", "uid": ""}

	item_set["blocks"].append({"hideIfSummonerSpell": "", "items": [{"count": 1, "id": str(item)} for item in start_items], "showIfSummonerSpell": "", "type": 'Start'})
	item_set["blocks"].append({"hideIfSummonerSpell": "", "items": [{"count": 1, "id": str(item)} for item in best_items], "showIfSummonerSpell": "", "type": 'Best Items'})

	for i in range(len(all_item_sets)):
		if all_item_sets[i]["title"] == "AUTOSET":
			all_item_sets[i] = item_set

	put_sets = url+"/lol-item-sets/v1/item-sets/"+str(sid)+"/sets"
	requests.put(put_sets, verify=False, json={"itemSets": all_item_sets})


def setSpells(url, spells):
	path = url+"/lol-champ-select/v1/session/my-selection"
	requests.patch(path, verify=False, json={"spell1Id": spells[0], "spell2Id": spells[1]})


def setSkin(url, skinid):
	path = url+"/lol-champ-select/v1/session/my-selection"
	requests.patch(path, verify=False, json={"selectedSkinId": skinid})	


def setRunes(url, runes, title='AUTORUNES'):
	rune_page_id = 0
	path = url+"/lol-perks/v1/pages"
	pages = requests.get(path, verify=False).json()
	for page in pages:
		if page["name"] == "AUTORUNES":
			rune_page_id = page["id"]

	path = url+"/lol-perks/v1/pages/"+str(rune_page_id)
	requests.delete(path, verify=False)
	path = url+"/lol-perks/v1/pages/"
	requests.post(path, verify=False, json={"name": title, "primaryStyleId": runes[0][0], "subStyleId": runes[1][0], "selectedPerkIds": runes[0][1:]+runes[1][1:]+runes[2]})


def getLaneName(url):
	sid = getSummonerId(url)['sid']
	path = f"{url}/lol-champ-select/v1/session"
	r = requests.get(path, verify=False).json()
	team = r['myTeam']
	for player in team:
		if player['summonerId'] == sid:
			return player['assignedPosition'].upper()
	return 'TOP'


def getLaneSpecialName(url):
	laneName = getLaneName(url)
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


def getSummonerId(url):
	path = f"{url}/lol-summoner/v1/current-summoner"
	r = requests.get(path, verify=False).json()
	return {'sid': r['summonerId'], 'name': r['displayName']}


def getSpellsIds(url):
	path = url+"/lol-champ-select/v1/session/"
	r = requests.get(path, verify=False).json()
	
	sid = getSummonerId(url)['sid']

	for player in r['myTeam']:
		if player['summonerId'] == sid:
			return [player['spell1Id'], player['spell2Id']]
	
	return [0, 0]


def getCurrentchampion(url):
	path = url+"/lol-champ-select/v1/session/"
	r = requests.get(path, verify=False).json()

	cell_id = r.get('localPlayerCellId',-1)
	if cell_id != -1:
		for player in r['actions'][0]:
			if player['actorCellId'] == cell_id:
				return player['championId'],player['completed'] 

	return -1, False


def getChampionInfo(url, cid):
	path = url+"/lol-game-data/assets/v1/champions/"+str(cid)+".json"
	r = requests.get(path, verify=False).json()
	name = r["name"]
	alias = r["alias"].lower()
	icon_path = getImageFromUrl(url, r["squarePortraitPath"])

	return {'name': name, 'alias': alias, 'iconPath': icon_path}


def getFullRunePageImages(url):
	runes = getRunes(url)
	perks = getPerks(url)
	# print(runes)

	allRunes = [[]]
	stats = [[getImageFromUrl(url, perks[p]['iconPath']) for p in perk] for perk in runes[8000]['slots'][-3:]]
	runesOrder = [8000, 8100, 8200, 8400, 8300]
	colors = ['#c8aa6e', '#dc4747', '#6c75f5', '#a4d08d', '#48b4be']

	for rune, color in zip(runesOrder, colors):
		page = runes[rune]['slots']
		# print(SVG(requests.get(url+runes[rune]['iconPath'], verify=False).content))
		icon = SVG(requests.get(url+runes[rune]['iconPath'], verify=False).content)
		icon.set(facecolor=color)
		allRunes[0].append(icon.buffer)
		# allRunes[0].append(getImageFromUrl(url, runes[rune]['iconPath']))
		allRunes.append([[getImageFromUrl(url, perks[p]['iconPath']) for p in perk] for perk in page[:-3]])
	allRunes.append(stats)
	return allRunes


def getSkins(url):
	path = url+"/lol-champ-select/v1/skin-selector-info"
	selected = requests.get(path, verify=False).json()
	selectedChampion = selected['selectedChampionId']
	selectedSkin = selected['selectedSkinId']

	path = url+"/lol-champ-select/v1/pickable-skin-ids"
	all_skins = requests.get(path, verify=False).json()

	path = url+f"/lol-game-data/assets/v1/champions/{selectedChampion}.json"
	skins = requests.get(path, verify=False).json()['skins']
	availableSkins = {skin['id']: getImageFromUrl(url,skin['uncenteredSplashPath']) for skin in skins if skin['id'] in all_skins or skin['isBase']}
	
	return {"selectedSkinId": selectedSkin, "availableSkins": availableSkins}


def main():
	url = get_client_url()
	getFullRunePageImages(url)
	# getRunes(url)
	# print(getItems(url))


if __name__ == '__main__':
	main()