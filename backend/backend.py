import time
from queue import Queue
import subprocess
import backend.LoLAutomationLib as lolib
from backend.lolhandler import LoLHandler
import backend.data_scrape as ds


class Backend:
    def __init__(self):
        self.queue = Queue(maxsize=10)
        self.lol_handler = LoLHandler(self.queue)
        self.lol_handler.start()
        self.url = ''
        self.champion_id = -1
        self.allRunes = None
        self.allSpells = None
        self.allItems = None
        self.loaded_items = dict()
        self.rune_mapping = dict()
        self.primary_spell_f = True
        self.lol_status = 'GAME_CLOSED'
        self.navigation_icons = dict()

    def get_status(self):
        message = self.queue.get()
        if message == 'GAME_OPENED':
            self.url = self.lol_handler.url
            if self.allRunes is None:
                self.allRunes = lolib.getRunes(self.url)
            if self.allSpells is None:
                self.allSpells = lolib.getSpells(self.url)
            if self.allItems is None:
                self.allItems = lolib.getItems(self.url)
            self.get_navigation_icons()
            self.create_default_mapping()
        if message == 'CHAMPION_PICKED':
            self.champion_id = self.lol_handler.champion_id
        return message

    def get_runes(self):
        return lolib.getFullRunePageImages(self.url)

    # TODO
    def swap_spells(self) -> None:
        self.primary_spell_f = not self.primary_spell_f
        print('swapped')

    def get_navigation_icons(self):
        self.navigation_icons['lane_navigation'] = {}
        self.navigation_icons['lane_navigation']['top'] = {'enabled': 'images/top.png', 'disabled': 'images/top_disabled.png'}
        self.navigation_icons['lane_navigation']['jungle'] = {'enabled': 'images/jungle.png', 'disabled': 'images/jungle_disabled.png'}
        self.navigation_icons['lane_navigation']['mid'] = {'enabled': 'images/mid.png', 'disabled': 'images/mid_disabled.png'}
        self.navigation_icons['lane_navigation']['bot'] = {'enabled': 'images/bot.png', 'disabled': 'images/bot_disabled.png'}
        self.navigation_icons['lane_navigation']['support'] = {'enabled': 'images/support.png', 'disabled': 'images/support_disabled.png'}

    # TODO
    def get_build(self):
        def BuildByLane(page, championInfo, queueName, championAlias, laneSpecialNane):
            build = ds.get_build(page, queue=queueName)
            if not build['exists']:
                return False,{}
            championLane = {}
            championLane['spells'] = [lolib.getImageFromUrl(self.url, self.allSpells[build['spells'][i]]['iconPath']) for i in range(2)]
            championLane['ability_order'] = build['abilities_order']
            championLane['runes'] = self.get_rune_mapping(build['runes'])
            championLane['items'] = [[{'image': self.get_item_image(item)} for item in build['start_items']], [{'image': self.get_item_image(item)} for item in build['best_items']]]
            championLane['wr'] = build['wr']
            championLane['pr'] = build['pr']
            championLane['br'] = build['br']

            # championLane['Sspells'] = build['spells']
            # championLane['Srunes'] = build['runes']
            # championLane['Sitems'] = [build['start_items'], build['best_items']]
            return True, championLane, build

        champion_info = lolib.getChampionInfo(self.url, self.champion_id)
        queueName = lolib.getQueueSpecialName(self.url)

        champion = {}
        champion['build'] = {}
        champion['name'] = champion_info['name']
        champion['image'] = champion_info['iconPath']
        champion['abilities'] = [ability for ability in lolib.getAbilitiesIcons(self.url, self.champion_id)]

        lanes = ['top', 'jungle', 'mid', 'bot', 'support', '']
        start = time.time()
        pages = ds.load_pages(champion_info['alias'], queueName, lanes)
        print([len(page) for page in pages])
        print('load time:', time.time() - start)
        for lane in lanes[:-1]:
            exists, championLane, build = BuildByLane(pages[lane], champion_info, queueName, champion_info['alias'], lane)
            if(exists):
                champion['build'][lane] = [championLane, build]

        champion['default_lane'] = ds.getDefaultLane(pages[''])
        print('total', time.time() - start)
        # champion['name'] = champion_info['name']
        # champion['image'] = champion_info['iconPath']
        # champion['abilities'] = [ability for ability in lolib.getAbilitiesIcons(self.url,champion_info['cid'])]
        # champion['build'] = {}
        # champion['build'][build['lane']] = {}
        # champion['build'][build['lane']]['spells'] = [self.allSpells[build['spells'][i]]['iconPath'] for i in range(2)]
        # champion['build'][build['lane']]['ability_order'] = build['abilities_order']
        # champion['build'][build['lane']]['runes'] = self.runes2index(build)
        # champion['build'][build['lane']]['items'] = [[{'image':self.allItems[item]['iconPath']} for item in build['start_items']],[{'image':self.allItems[item]['iconPath']} for item in build['best_items']]]
        # champion['build'][build['lane']]['wr'] = build['wr']
        # champion['build'][build['lane']]['pr'] = build['pr']
        # champion['build'][build['lane']]['br'] = build['br']

        # champion['abilities'] = ['images/TwitchFullAutomatic.png' for _ in range(5)]
        # champion['name'] = 'Kennen'
        # champion['image'] = 'images/Kennen_0.jpg'
        # champion['abilities'] = ['images/TwitchFullAutomatic.png' for _ in range(5)]
        # champion['build']['top']['spells'] = ['images/SummonerHeal.png', 'images/SummonerHeal.png']
        # champion['build']['top']['ability_order'] = [1, 2, 3, 1, 1, 4, 1, 2, 1, 2, 4, 2, 2, 3, 3, 4, 3, 3]
        # champion['build']['top']['runes'] = [[0, 1, 1, 1, 1], [1, -1, 1, 1, 1], [0, 0, 0]]
        # champion['build']['top']['items'] = [[{'image':'images/1001.png', 'description': 'makaronia'} for _ in range(3)], [{'image':'images/1001.png'} for _ in range(6)]]
        # champion['build']['top']['wr'] = 55.5
        # champion['build']['top']['pr'] = 12.1
        # champion['build']['top']['br'] = 5
        # champion['build']['bot'] = {}
        # champion['build']['bot']['spells'] = ['images/SummonerMana.png', 'images/SummonerMana.png']
        # champion['build']['bot']['ability_order'] = [2, 1, 3, 1, 1, 4, 1, 2, 1, 2, 4, 2, 2, 3, 3, 4, 3, 3]
        # champion['build']['bot']['runes'] = [[1, 2, 2, 2, 2], [0, 2, 2, 2, 2], [0, 0, 0]]
        # champion['build']['bot']['items'] = [[{'image':'images/7008.png'} for _ in range(3)], [{'image':'images/7008.png'} for _ in range(6)]]
        # champion['build']['bot']['wr'] = 55.5
        # champion['build']['bot']['pr'] = 12.1
        # champion['build']['bot']['br'] = 5
        # champion['default_lane'] = 'top'
        return champion

    def get_item_image(self, item):
        if item not in self.loaded_items:
            self.loaded_items[item] = lolib.getImageFromUrl(self.url, self.allItems[item]['iconPath'])
        return self.loaded_items[item]

    def ping(self) -> str:
        cmd_ping = subprocess.Popen(["ping.exe", "72.52.10.14", "-n", "1"], stdout=subprocess.PIPE)
        return cmd_ping.communicate()[0].decode('utf8').replace("\r", "").strip().split("\n")[-1].split(",")[1].split("=")[1][:-2]

    def close(self):
        self.lol_handler.loop_stop()
        self.lol_handler.join()

    def create_default_mapping(self):
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
        # print(complete_runes)
        return complete_runes

    def set_everything(self, champion):
        lolib.setSpells(self.url, champion['spells'])
        lolib.setRunes(self.url, champion['runes'])
        lolib.updateItemSet(self.url, champion['start_items'], champion['best_items'])
