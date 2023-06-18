import time
from utils.utils import Message
from threading import Thread
import requests.exceptions
from queue import Queue
import backend.LoLAutomationLib as lolib


class LoLHandler(Thread):
    def __init__(self, queue_out: Queue, *args, **kwargs) -> None:
        super().__init__(*args, *kwargs)
        self.queue_out = queue_out
        self.loop = True
        self.champion_id = -1
        self.current_skin = 0
        self.client_state = 'CLOSED'
        self.server_state = 'CLOSED'
        self.url = ''

    def run(self):
        while self.loop:
            previous_state = self.client_state
            previous_server_state = self.server_state
            previous_champion = self.champion_id
            previous_skin = self.current_skin
            self.check_client_status()

            if self.client_state == 'CLOSED' and previous_state == 'OPEN':
                print('Game closed.')
                self.queue_out.put(Message('GAME_CLOSED'))
                self.server_state = 'CLOSED'
                self.champion_id = -1
                self.url = ''

            if self.client_state == 'OPEN' and previous_state == 'CLOSED':
                print('Game is open.')
                self.get_client_url()

            if self.client_state == 'OPEN' and self.server_state == 'CLOSED':
                self.server_state = self.check_server_status()

            if self.server_state == 'OPEN' and previous_server_state == 'CLOSED':
                print(f'Server is open at: {self.url}')
                self.queue_out.put(Message('GAME_OPENED'))

            if self.server_state == 'OPEN':
                self.get_champion_picked()

            if self.champion_id > 0:
                self.get_skin()

            if self.champion_id > 0 and self.champion_id != previous_champion:
                self.queue_out.put(Message('CHAMPION_PICKED'))

            if self.champion_id > 0 and self.current_skin != previous_skin:
                self.queue_out.put(Message('CHANGED_SKIN', [self.current_skin]))


            time.sleep(.1)
        self.queue_out.put('PROCESS_CLOSED')
        print('Process closed')

    def loop_stop(self):
        self.loop = False

    def check_server_status(self):
        r = []
        status_code = -1
        try:
            r = requests.get(self.url + "/lol-perks/v1/styles", verify=False)
            status_code = r.status_code
            r = r.json()
        except requests.exceptions.RequestException as e:
            print('Couldn\'t connect to the client server. Retrying in 2 seconds.')
            time.sleep(2)
        return 'OPEN' if status_code == 200 and len(r) > 0 else 'CLOSED'

    def get_champion_picked(self):
        self.champion_id = lolib.getCurrentchampion(self.url)

    def get_client_url(self):
        self.url = lolib.get_client_url()

    def check_client_status(self):
        self.client_state = 'OPEN' if lolib.getClientStatus() else 'CLOSED'

    def get_skin(self):
        self.current_skin = lolib.getSkins(self.url)['selectedSkinId']
