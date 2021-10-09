## kaggle-Lux-AI  

# BigNoBrainer  

- Perception class feeds the current game state to the network  
- A single large network translates the perception into (?)
- Executor class follows the hints from the (?) output matricies and emits unit and citytile actions.

A module construct a gif of the input matricies from a Game() class. The gif below is made by compiling the Game() states every 50 turns of the rule based clusterbot L16H7
![Input Matricies](https://raw.githubusercontent.com/OrsoEric/kaggle-Lux-AI/develop/readme_media/2021-10-09-perception.gif)

# test_json_processsor.py  
This python script converst from a replay.json that can be downloaded from Kaggle in JSON format to a Game() class, to a Perception() class and finally to a .gif image.  
It takes about 90m to generate the .gif
[Kaggle Replay episode 27883823](https://www.kaggle.com/c/lux-ai-2021/submissions?dialog=episodes-episode-27883823)
![Replay of Kaggle episode 27883823](https://raw.githubusercontent.com/OrsoEric/kaggle-Lux-AI/develop/replays/27883823.gif)  
