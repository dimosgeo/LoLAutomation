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

    def get_build(self):
        def BuildByLane(page, queueName):
            build = ds.get_build(page, queue=queueName)
            if not build['exists']:
                return False, {}
            championLane = dict()
            championLane['spells'] = [lolib.getImageFromUrl(self.url, self.allSpells[build['spells'][i]]['iconPath']) for i in range(2)]
            championLane['ability_order'] = build['abilities_order']
            championLane['runes'] = self.get_rune_mapping(build['runes'])
            championLane['items'] = [[{'image': self.get_item_image(item), 'description': self.allItems[item]['iconDesc'], 'count': count} for item, count in zip(build['start_items'], build['start_items_n'])], [{'image': self.get_item_image(item), 'description': self.allItems[item]['iconDesc'], 'count': 1} for item in build['best_items']]] # TEST
            championLane['wr'] = build['wr']
            championLane['pr'] = build['pr']
            championLane['br'] = build['br']

            return True, championLane, build

        champion_info = lolib.getChampionInfo(self.url, self.champion_id)
        queueName = lolib.getQueueSpecialName(self.url)
        # queueName = '' # TEST

        champion = dict()
        champion['build'] = {}
        champion['name'] = champion_info['name']
        champion['image'] = champion_info['iconPath']
        champion['abilities'] = [ability for ability in lolib.getAbilitiesIcons(self.url, self.champion_id)]

        lanes = ['top', 'jungle', 'mid', 'bot', 'support', '']
        pages = ds.load_pages(champion_info['alias'], queueName, lanes)
        for lane in lanes[:-1]:
            exists, championLane, build = BuildByLane(pages[lane], queueName)
            if exists:
                champion['build'][lane] = [championLane, build]

        champion['default_lane'] = ds.getDefaultLane(pages[''])
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
        return complete_runes

    def set_everything(self, champion):
        lolib.setSpells(self.url, champion['spells'])
        lolib.setRunes(self.url, champion['runes'])
        lolib.updateItemSet(self.url, champion['start_items'], champion['best_items'])
