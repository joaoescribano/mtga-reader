# MTGA-Reader
This source is for learning propouse only.

This is a simple code to read the files from MTG Arena game, providing methods to search cards and card images trought SQLite and [UnityPy](https://pypi.org/project/UnityPy/)
The whole .mtga file is a lie, some files is just some SQLite and others unity assets, so we can read both.

The game also provides detailed logs of the "gameplay", something like [CounterStrike Game State](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration), but much whorse (Settings -> Account -> Detailed logs).

I'll be decoding the outputs so we could in theory, read live-feed of the log files to create a event dispatcher (WebSocket or something like) to provide information to third party softwares.

##### Usage:
1) Install requirements using 'pip3 install -r requirements'
2) Edit 'main.py' and set your MTGA root folder there
3) Run it and have fun