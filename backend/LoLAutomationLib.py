import requests
import pythoncom
import wmi
import socket
import io
import argparse


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
	print(arguments)
	args = parse_arguments(arguments)
	print(args)#.get('remoting-auth-token'))
	# token = arguments[7].split("=")[1]
	# token = arguments[1].split("=")[1]
	# port = arguments[2].split("=")[1]
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

def getImageFromUrl(url,img_path):
	path = url+img_path
	return io.BytesIO(requests.get(path, verify=False).content)

def getLobbyQueue(url):
	path = url+"/lol-lobby/v2/lobby"
	return requests.get(path, verify=False).json()["gameConfig"]["queueId"]

def getQueueName(url):
	queue = getLobbyQueue(url)
	if(queue==-1):
		return 'other'
	queues = url+"/lol-game-data/assets/v1/queues.json"
	queues = requests.get(queues, verify=False).json()
	return queues[queue]["shortName"].lower()

def getQueueSpecialName(url):
	queue = getQueueName(url)
	if "spellbook" in queue:
		return "ultbook"
	elif "aram" in queue:
		return "aram"
	elif "urf" in queue:
		return "urf"
	return "5v5"

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
		perks[perk['id']] = {'iconPath':perk['iconPath']}
	return perks	

def getRunes(url):
	path = url+"/lol-perks/v1/styles"
	r = requests.get(path, verify=False).json()	

	runes = {}
	for s in r:
		slots = [x['perks'] for x in s['slots']]
		#runes[s['id']] = {'allowedSubStyles':s['allowedSubStyles'], 'slots':slots, 'iconPath':s['iconPath']}
		runes[s['id']] = {'slots':slots, 'iconPath':s['iconPath']}
	return runes

def getAbilitiesIcons(url,cid):
	path = url+"/lol-game-data/assets/v1/champions/"+str(cid)+".json"
	r = requests.get(path, verify=False).json()
	# return {'P':r["passive"]["abilityIconPath"], 'Q':r["spells"][0]["abilityIconPath"], 'W':r["spells"][1]["abilityIconPath"], 'E':r["spells"][2]["abilityIconPath"], 'R':r["spells"][3]["abilityIconPath"]}
	return [getImageFromUrl(url,r["passive"]["abilityIconPath"]), getImageFromUrl(url,r["spells"][0]["abilityIconPath"]), getImageFromUrl(url,r["spells"][1]["abilityIconPath"]), getImageFromUrl(url,r["spells"][2]["abilityIconPath"]), getImageFromUrl(url,r["spells"][3]["abilityIconPath"])]

def getSpells(url):
	path = url+"/lol-game-data/assets/v1/summoner-spells.json"
	r = requests.get(path, verify=False).json()
	spells = {}
	for spell in r:
		# spells[spell['id']] = {'iconPath':getImageFromUrl(url,spell['iconPath'])}
		spells[spell['id']] = {'iconPath':spell['iconPath']}
	return spells


def getItems(url):
	path = url+"/lol-game-data/assets/v1/items.json"
	r = requests.get(path, verify=False).json()
	items = {}
	for item in r:
		# items[item['id']] = {'iconPath':getImageFromUrl(url,item['iconPath'])}
		items[item['id']] = {'iconPath': item['iconPath']}
	return items

def updateItemSet(url, start_items, best_items, title='AUTOSET'): #MAYBE NEED FIX, NEED TEST
	sid = getSummonerId(url)['sid']
	path = url+"/lol-item-sets/v1/item-sets/"+str(sid)+"/sets"
	all_item_sets = requests.get(path, verify=False).json()["itemSets"]

	item_set = {"associatedChampions": [], "associatedMaps": [11, 12], "blocks": [], "map": "", "mode": "", "preferredItemSlots": [], "sortrank": 0, "startedFrom": "blank", "title": "AUTOSET", "type": "custom", "uid": ""}

	item_set["blocks"].append({"hideIfSummonerSpell": "", "items": [{"count": 1, "id": str(item)} for item in start_items], "showIfSummonerSpell": "", "type": 'Start'})
	item_set["blocks"].append({"hideIfSummonerSpell": "", "items": [{"count": 1, "id": str(item)} for item in best_items], "showIfSummonerSpell": "", "type": 'Best Items'})

	for i in range(len(all_item_sets)):
		if all_item_sets[i]["title"] == "AUTOSET":
			all_item_sets[i] = item_set

	put_sets = url+"/lol-item-sets/v1/item-sets/"+str(sid)+"/sets"
	requests.put(put_sets, verify=False, json={"itemSets": all_item_sets})

def setSpells(url,spells): #NEED TEST
	print(spells)
	path = url+"/lol-champ-select/v1/session/my-selection"
	requests.patch(path, verify=False, json={"spell1Id": spells[0], "spell2Id": spells[1]})

def setRunes(url,runes,title='AUTORUNES'): #NEED TEST
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
			#return champion.lane = player['assignedPosition'].lower()
			return player['assignedPosition'].upper()
	return 'TOP'

def getLaneSpecialName(url): #NEED TEST
	#laneName = getLaneName(url)
	laneName = getLaneName(url)
	if(laneName==''):
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
	return {'sid':r['summonerId'], 'name':r['displayName']}


def getCurrentchampion(server_url):
	path = "/lol-champ-select/v1/current-champion"
	r = requests.get(server_url + path, verify=False)
	if r.status_code != 200:
		return -1
	return r.json()


def getChampionInfo(url, cid):  #NEED TEST
	path = url+"/lol-game-data/assets/v1/champions/"+str(cid)+".json"
	r = requests.get(path, verify=False).json()
	print(r)
	name = r["name"]
	alias = r["alias"].lower()
	icon_path = getImageFromUrl(url, r["squarePortraitPath"])

	return {'name': name, 'alias': alias, 'iconPath': icon_path}


def getFullRunePageImages(url):
	runes = getRunes(url)
	perks = getPerks(url)

	allRunes = [[]]
	stats = [[getImageFromUrl(url,perks[p]['iconPath']) for p in perk] for perk in runes[8000]['slots'][-3:]]
	runesOrder = [8000,8100,8200,8400,8300]
	for rune in runesOrder:
		page = runes[rune]['slots']
		allRunes[0].append(getImageFromUrl(url, runes[rune]['iconPath']))
		# allRunes[0].append(getImageFromUrl(url,perks[p]['iconPath']))
		allRunes.append([[getImageFromUrl(url,perks[p]['iconPath']) for p in perk] for perk in page[:-3]])
	allRunes.append(stats)
	return allRunes

def main():
	url = getClientUrl()
	print(getRunes(url))
	# mak = getChampionInfo(url)
	# print(mak)

if __name__ == '__main__':
	main()
