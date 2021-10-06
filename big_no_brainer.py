##  @package big_no_brainer
#   ARCHITECTURE
#
#   INFERENCE
#   1) Game() -> Perception()
#   2) Perception() -> model? -> Orders()
#   3) Orders() -> list()
#
#   TRAINING
#
#   1) run inference this vs this at given random map size   
#   2) game result -> Reward() -> float
#   3) reinforcement learning


#--------------------------------------------------------------------------------------------------------------------------------
#   IMPORT
#--------------------------------------------------------------------------------------------------------------------------------

from lux.game import Game

#--------------------------------------------------------------------------------------------------------------------------------
#   Perception
#--------------------------------------------------------------------------------------------------------------------------------

class Perception():
    


    #----------------    Constructor    ----------------

    def __init__( self, ic_game_state : Game ):
        """Construct perception class based on a game state
        Args:
            ic_game_state (Game): Current game state
        """
        #store locally the game state. Not visible from outside
        self._game = ic_game_state
        return

    ## Stringfy class for print method
    def __str__(self) -> str:
        return f"Perception{self._game}"

    #----------------    Public    ---------------

    def compute_perception( self ):


        return


