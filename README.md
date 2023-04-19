# LoLAutomation (PATCH 13.8)

## About The Project
This project is a Python-coded application. The primary objective of this project is to introduce automation to the League of Legends game. With the help of this program, players can automatically import Rune pages, spells, and items into the game during the League of Legends champion Select phase. Also, goal of this app is to help players by giving them the most common builds and champion ability level ups.

## Data
All information is supplied by METAsrc. A lot of helpful information is available on METAsrc, including details on builds, spells, skill order, and many other things. It includes information for the most popular game modes, including 5v5 and Aram. Users can choose between Pick rate and Win rate depending on the desired data.

## Setup and Prerequisites
### Python
Users must already have Python installed on their systems in order for this app to function properly. A few libraries are also necessary for effective operation. The file ```requirements.txt``` contains the necessary libraries. To install them, execute ```pip install -r requirements.txt``` on the terminal. 

### League of Legends
The tool that we provide, helps users to import runes, spells and item sets in the game automatically. To do so, the user need to make some changings into the game.
* On Collection tab -> Runes tab, create a new Rune page and rename it to AUTORUNES
* On Collection tab -> Items tab, create a new Item set and rename it to AUTOSET

### Execution
To execute the app you must run ```python main.py```. After that, LoLAutomation app will wait until the player selects a champion during the Champion Select phase.

## Contact
Georgoulas Dimosthenis - dimosgeo99@gmail.com

Papanikolaou Nikolaos - nickp3065@gmail.com
