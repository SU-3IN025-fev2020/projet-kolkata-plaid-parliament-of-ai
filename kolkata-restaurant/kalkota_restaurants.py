# -*- coding: utf-8 -*-

# Nicolas, 2020-03-20

from __future__ import absolute_import, print_function, unicode_literals
from gameclass import Game,check_init_game_done
from spritebuilder import SpriteBuilder
from players import Player
from sprite import MovingSprite
from ontology import Ontology
from itertools import chain, product
import pygame
import glo

import random 
import numpy as np
import sys

import a_star
    
# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    # pathfindingWorld_MultiPlayer4
    name = _boardname if _boardname is not None else 'kolkata_6_10'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5  # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player
    
def main():

    #for arg in sys.argv:
    iterations = 20 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)

    init()
    
    
    

    
    #-------------------------------
    # Initialisation
    #-------------------------------
    nbLignes = game.spriteBuilder.rowsize
    nbColonnes = game.spriteBuilder.colsize
    print("lignes", nbLignes)
    print("colonnes", nbColonnes)
    
    
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    
    
    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print ("Init states:", initStates)
    
    
    # on localise tous les objets  ramassables (les restaurants)
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    print ("Goal states:", goalStates)
    nbRestaus = len(goalStates)
        
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    #print ("Wall states:", wallStates)
    
    # on liste toutes les positions permises
    """
    THIS DOESNT WORK AS EXPECTED

    allowedStates = [(x,y) for x in range(nbLignes) for y in range(nbColonnes)\
                     if (x,y) not in wallStates or goalStates] 
    """
    allowedStates = list(product(range(nbLignes), range(nbColonnes)))

    for x,y in set(chain(wallStates, goalStates)):
        allowedStates.remove((x,y))
    
    #-------------------------------
    # Placement aleatoire des joueurs, en évitant les obstacles
    #-------------------------------
        
    posPlayers = initStates

    
    for j in range(nbPlayers):
        x,y = random.choice(allowedStates)
        players[j].set_rowcol(x,y)
        game.mainiteration()
        posPlayers[j]=(x,y)


        
        
    
    #-------------------------------
    # chaque joueur choisit un restaurant
    #-------------------------------

    restau=[0]*nbPlayers
    for j in range(nbPlayers):
        c = random.randint(0,nbRestaus-1)
        print(c)
        restau[j]=c
    
    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------
    
    paths = [] # all paths of the players (paths[i] is the path for the player i )
    for i in range(nbPlayers):
        paths.append(a_star.a_star(posPlayers[i], goalStates[restau[i]], wallStates, hereustique=a_star.euc_dist))
        #if goalStates[restau[i]] != paths[i][0]: <------ THIS WILL NEVER HAPPEN
        paths[i].pop(0) # removing the first position ( it's the starting position for the player i )

    print()

    for i in range(nbPlayers):
        print("Player %d starts at %s, chosed the resto number %d located at %s" %(i, posPlayers[i], restau[i], goalStates[restau[i]]))
        print(paths[i])

    players_reached_goal = []

    for i in range(iterations):
        for j in range(nbPlayers): # on fait bouger chaque joueur séquentiellement

            if j in players_reached_goal:
                continue

            else:
                row,col = posPlayers[j]

                next_row, next_col = paths[j].pop(0)
                # and ((next_row,next_col) not in posPlayers)
                if ((next_row,next_col) not in wallStates) and next_row>=0 and next_row<=19 and next_col>=0 and next_col<=19:
                    players[j].set_rowcol(next_row,next_col)
                    print ("pos :", j, next_row,next_col)
                    game.mainiteration()

                    #time.sleep(1)
                    
                    col=next_col
                    row=next_row
                    posPlayers[j]=(row,col)
                
                # si on est à l'emplacement d'un restaurant, on s'arrête
                if (row,col) == goalStates[restau[j]]:
                    #o = players[j].ramasse(game.layers)
                    game.mainiteration()
                    print ("Le joueur ", j, " est à son restaurant.")
                    # goalStates.remove((row,col)) # on enlève ce goalState de la liste
                    players_reached_goal.append(j)
                    break      
    
    pygame.quit()

if __name__ == '__main__':
    main()