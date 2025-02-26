import aiohttp
import asyncio
from lxml import html
import platform


def get_lane(tree, data_dict, queue):
	lanes=['top', 'jungle', 'mid', 'adc', 'support', '']
	if queue == '5v5':
		lane = tree.xpath('//*[@id="splash-content"]/div[1]/div/div/div/div[2]/div/h1/span[2]/span[1]')[0].text_content().strip().lower()
		if lane in lanes:
			data_dict['lane'] = lane
		else:
			lane = tree.xpath('//*[@id="splash-content"]/div[1]/div/div/div/div[2]/div/h1/span[1]/span[2]/div/div')
			data_dict['lane'] = lane[0].values()[-1].split('/')[-1].split('.')[0].split('_')[0]
	else:
		data_dict['lane'] = ''


def get_spells(tree, data_dict):
	spells_path = tree.xpath('//div[@class=" _dcqhsp"]')[0]

	data_dict["spells"] = []
	for i in spells_path:
		data_dict["spells"].append(int(i.values()[1].split("-")[1]))


def get_runes(tree, data_dict):
	rune_page = tree.xpath('//*[@id="perks"]/div[2]')[0].getchildren()[0]

	style = int(rune_page.values()[0].split("-")[:2][0])
	substyle = int(rune_page.values()[0].split("-")[:2][1])

	pri_perks = rune_page.getchildren()[0].getchildren()[1:]
	data_dict['runes'] = [[style], [substyle], []]
	data_dict['runes'][0] += [int(perk.values()[1].split("-")[1]) for perk in pri_perks]

	sec_perks = rune_page.getchildren()[1].getchildren()[1]
	data_dict['runes'][1] += [int(perk.values()[1].split("-")[1]) for perk in sec_perks]

	mod_perks = rune_page.getchildren()[1].getchildren()[2]
	data_dict['runes'][2] += [int(perk.values()[1].split("-")[1]) for perk in mod_perks]


def get_abilities(tree, data_dict):
	abilities_page = tree.xpath('//*[@id="page-content"]/div[2]/div[2]/section[2]/div/div/table')[0].getchildren()[1:]
	data_dict["abilities_order"] = [0 for _ in range(18)]
	for i in range(1, 19):
		for row in abilities_page:
			if row.getchildren()[i].text_content() == "Q":
				data_dict["abilities_order"][i-1] = 1
			elif row.getchildren()[i].text_content() == "W":
				data_dict["abilities_order"][i-1] = 2
			elif row.getchildren()[i].text_content() == "E":
				data_dict["abilities_order"][i-1] = 3
			elif row.getchildren()[i].text_content() == "R":
				data_dict["abilities_order"][i-1] = 4


def get_items(tree, data_dict):
	start_items = tree.xpath('//*[@id="page-content"]/div[1]/div[2]/section/div/div/div[1]/div[2]/div[1]/div')[0].getchildren()
	data_dict["start_items"] = []
	data_dict["start_items_n"] = []
	for item in start_items:
		if item.__len__() != 0:
			if item.values()[0] == " _2kdnf4":
				data_dict["start_items_n"][-1]=int(item.getchildren()[0].text_content())
				continue
			data_dict["start_items"].append(int(item.getchildren()[0].values()[1].split("-")[-1]))
			data_dict["start_items_n"].append(1)

	data_dict["best_items"] = []
	best_items = tree.xpath('//*[@id="page-content"]/div[2]/div[2]/section[1]/div/div/div/div[1]')[0].getchildren()
	for item in best_items:
		data_dict["best_items"].append(int(item.getchildren()[0].values()[1].split("-")[-1]))


def get_rates(tree, data_dict, queue):
	if queue == '5v5':
		data_dict['wr'] = float(tree.xpath('//*[@id="splash-content"]/div[2]/span/div/span[2]/span')[0].text_content()[:-1])
		data_dict['pr'] = float(tree.xpath('//*[@id="splash-content"]/div[2]/span/div/span[4]/span')[0].text_content()[:-1])
		data_dict['br'] = float(tree.xpath('//*[@id="splash-content"]/div[2]/span/div/span[5]/span')[0].text_content()[:-1])
	elif queue == 'aram':
		data_dict['wr'] = float(tree.xpath('//*[@id="splash-content"]/div[2]/span/div/span[2]/span')[0].text_content()[:-1])
		data_dict['pr'] = float(tree.xpath('//*[@id="splash-content"]/div[2]/span/div/span[3]/span')[0].text_content()[:-1])
		data_dict['br'] = 0
	elif queue == 'urf':
		data_dict['wr'] = float(tree.xpath('//*[@id="splash-content"]/div[2]/span/div/span[2]/span')[0].text_content()[:-1])
		data_dict['pr'] = float(tree.xpath('//*[@id="splash-content"]/div[2]/span/div/span[3]/span')[0].text_content()[:-1])
		data_dict['br'] = 0
	else:
		data_dict['wr'] = 0
		data_dict['pr'] = 0
		data_dict['br'] = 0


def getDefaultLane(page):
	lanes=['top', 'jungle', 'mid', 'adc', 'support', '']
	tree = html.fromstring(page)
	lane = tree.xpath('//*[@id="splash-content"]/div[1]/div/div/div/div[2]/div/h1/span[2]/span[1]')[0].text_content().strip().lower()
	return lane if lane in lanes else 'mid'


def checkIfExists(tree):
	check = tree.xpath('//div[@class=" _fcip6v _eq293a _r14nwh"]')[0].getchildren()
	if len(check) != 2:
		return False
	return True


def get_build(page, queue='5v5'):
	tree = html.fromstring(page)
	data_dict = dict()
	data_dict["exists"] = True
	if not checkIfExists(tree):
		data_dict["exists"] = False
		return data_dict
	try:
		get_lane(tree, data_dict, queue)
		get_spells(tree, data_dict)
		get_runes(tree, data_dict)
		get_abilities(tree, data_dict)
		get_items(tree, data_dict)
		get_rates(tree, data_dict, queue)
	except:
		data_dict["exists"] = False
	return data_dict


async def load_page(queue_name='5v5', champion_name='aatrox', lane='top'):
	url = f'https://www.metasrc.com/lol/{queue_name}/build/{champion_name}/{lane}'
	page = ''
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as response:
			page = await response.text()
	return lane, page


def load_pages(queue_name='5v5', champion_name='aatrox', lanes=['top', 'jungle', 'mid', 'adc', 'support', '']):
	if platform.system() == 'Windows':
		asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
	data = asyncio.run(create_page_tasks(queue_name, champion_name, lanes), debug=False)
	result = dict()
	for lane, page in data:
		result[lane] = page
	return result


async def create_page_tasks(queue_name='5v5', champion_name='aatrox', lanes=['top', 'jungle', 'mid', 'adc', 'support', '']):
	tasks = [asyncio.create_task(load_page(queue_name, champion_name, lane)) for lane in lanes]
	return await asyncio.gather(*tasks)


if __name__ == '__main__':
	result = load_pages('5v5', 'kennen')
	for lane in result:
		print(get_build(result[lane], queue='5v5'))
		print(getDefaultLane(result[lane]))