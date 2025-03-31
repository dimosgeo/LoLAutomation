import time
from utils import Message, StatusType, ServerStatus, ClientStatus
from threading import Thread
from queue import Queue
from backend.utils.LoLAutomationLib import LoLAdapter, getClientStatus
from typing import Optional


class LoLHandler(Thread):
    def __init__(self, queue_out: Queue, *args, **kwargs) -> None:
        super().__init__(*args, *kwargs)
        self.queue_out = queue_out
        self.lol_adapter: Optional[LoLAdapter] = None
        self.loop = True
        self.champion_id = -1
        self.champion_locked = False
        self.current_skin = -1
        self.client_state = ClientStatus.CLOSED
        self.server_state = ServerStatus.CLOSED

    def run(self):
        while self.loop:
            previous_state = self.client_state
            previous_server_state = self.server_state
            previous_champion = self.champion_id
            lock_state = self.champion_locked
            previous_skin = self.current_skin
            self.check_client_status()

            if self.client_state == ClientStatus.CLOSED and previous_state == ClientStatus.OPEN:
                self.queue_out.put(Message(StatusType.GAME_CLOSED))
                self.server_state = ServerStatus.CLOSED
                self.champion_id = -1

            if self.client_state == ClientStatus.OPEN and previous_state == ClientStatus.CLOSED:
                self.lol_adapter = LoLAdapter()

            if self.client_state == ClientStatus.OPEN and self.server_state == ClientStatus.CLOSED:
                self.check_server_status()

            if self.server_state == ClientStatus.OPEN and previous_server_state == ClientStatus.CLOSED:
                print(f'Server is open at: {self.lol_adapter.url}')
                self.queue_out.put(Message(StatusType.GAME_OPENED))

            if self.server_state == ServerStatus.OPEN:
                self.get_champion_picked()

            if self.champion_id > 0 and self.champion_id != previous_champion:
                self.queue_out.put(Message(StatusType.CHAMPION_PICKED))

            if self.champion_locked and (self.champion_id != previous_champion or self.champion_locked != lock_state):
                self.get_skin()
                while not self.queue_out.empty():
                    self.queue_out.get()
                self.queue_out.put(Message(StatusType.CHAMPION_PICKED))
                self.queue_out.put(Message(StatusType.CHAMPION_LOCKED))

            if self.champion_id > 0 and self.current_skin != previous_skin:
                self.queue_out.put(Message(StatusType.CHANGED_SKIN, [self.current_skin]))

            time.sleep(.1)
        self.queue_out.put(Message(StatusType.PROCESS_CLOSED))
        print('Process closed')

    def loop_stop(self):
        self.loop = False

    def check_server_status(self):
        self.server_state = self.lol_adapter.check_server_status()
        if self.server_state != ServerStatus.OPEN:
            time.sleep(2)

    def get_champion_picked(self):
        result = self.lol_adapter.getCurrentChampion()
        self.champion_id = result[0]
        self.champion_locked = result[1]

    def check_client_status(self):
        self.client_state = getClientStatus()

    def get_skin(self):
        self.current_skin = self.lol_adapter.getSkins()['selectedSkinId']
