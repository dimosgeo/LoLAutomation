from model.data_loader import APILoader, MetasrcLoader
from model.utils.LoLAutomationLib import LoLAdapter
from utils import Lanes
import subprocess  # REMOVE
from typing import Dict, Optional


class Model:
    def __init__(self, development_mode: Optional[int] = None):
        self.dev_mode = development_mode
        self.primary_spell_f = True
        self.navigation_icons = dict()
        self.api_handler: Optional[APILoader] = None
        self.lol_adapter: Optional[LoLAdapter] = None

    def init_data(self):
        self.lol_adapter = LoLAdapter()
        self.api_handler = MetasrcLoader(self.lol_adapter, self.dev_mode)
        self.load_navigation_icons()

    def get_runes(self):
        return self.lol_adapter.getFullRunePageImages()

    def swap_spells(self) -> None:
        spells = self.lol_adapter.getSpellsIds()
        self.lol_adapter.setSpells(spells[::-1])
        self.primary_spell_f = not self.primary_spell_f

    def load_navigation_icons(self) -> None:
        self.navigation_icons['lane_navigation'] = {lane: {'disabled': f'images/{lane.value}_disabled.png', 'enabled': f'images/{lane.value}.png'} for lane in Lanes if lane.value}

    def get_build(self, champion_id):
        return self.api_handler.get_build(champion_id)

    @staticmethod
    def ping() -> str:  # REMOVE
        cmd_ping = subprocess.Popen(["ping.exe", "72.52.10.14", "-n", "1"], stdout=subprocess.PIPE)  # REMOVE
        return cmd_ping.communicate()[0].decode('utf8').replace("\r", "").strip().split("\n")[-1].split(",")[1].split("=")[1][:-2]  # REMOVE

    def set_client_data(self, champion):
        if not self.primary_spell_f:
            self.lol_adapter.setSpells(champion['spells'][::-1])
        else:
            self.lol_adapter.setSpells(champion['spells'])

        self.lol_adapter.setRunes(champion['runes'])
        self.lol_adapter.updateItemSet(champion['start_items'], champion['best_items'])

    def set_active_skin(self, skin_id):
        self.lol_adapter.setSkin(skin_id)

    def get_skins(self):
        if self.dev_mode:
            return {"selectedSkinId": -1, "availableSkins": []}
        return self.lol_adapter.getSkins()

    def get_lane_navigation_icons(self) -> Dict[str, Dict[str, str]]:
        return self.navigation_icons['lane_navigation']
