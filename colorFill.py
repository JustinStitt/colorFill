import pygame
import random
import sys
import numpy as np
pygame.init()
#7x8 (row,col) default. Try out 20x20!!!
ROWS = 7
COLS = 8
colors = [(209, 84, 75),(63, 158, 209),(80, 199, 105),(85, 70, 117),(235, 226, 56),(45, 51, 51)]
#sample extra colors , (255,255,255), (166,16,166),(235, 156, 21),(20, 201, 201)
#setup
cell_size = 100#change cellsize if your monitor is not fitting everything on screen
WIDTH, HEIGHT = (COLS * cell_size, ROWS * cell_size + 100)
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("colorFill -- Justin Stitt")
background_color = (66,66,66)
font = pygame.font.Font('freesansbold.ttf', 16)
p1text = font.render('--> Player(1): 1 <--',True,colors[0])
p2text = font.render('Player(2): 1',True,colors[1])

clock = pygame.time.Clock()
fps = 30
#end setup

cells = []
choices = []

class Game():
    def __init__(self):
        self.turn = 1#game starts with player 1 (bottom left)
        self.player_territory = [[],[]]
        self.setup_grid()
        self.setup_choices()
    def setup_grid(self):
        for r in range(ROWS):
            for c in range(COLS):
                cell_pos = (c * cell_size,r * cell_size)
                cell_color = get_rand_color()
                _cell = Cell(cell_pos,cell_color)
                #manage blobs
                remove = []
                i = r * COLS + c
                if(i == COLS - 2):
                    remove.append(colors[1])
                if(i == COLS - 1):
                    _cell.color = colors[1]
                if(i == ROWS * COLS - 2):# 40 = (8 * 5)  cols = 7 rows = 8
                    remove.append(colors[0])
                if(i == COLS * (ROWS - 1)):
                    _cell.color = colors[0]
                if(r > 0):#remove above color from pool
                    remove.append(cells[(r-1) * COLS + c].color)
                if(c > 0):#remove left color from pool
                    remove.append(cells[r * COLS + (c-1)].color)
                while( is_in(_cell.color,remove) ):
                    _cell.color = get_rand_color()
                cells.append(_cell)
                #end manage blobs

        #set bottom left and top right cells to red/blue respectively
        self.player_territory[0].append(cells[COLS * (ROWS - 1)])
        self.player_territory[1].append(cells[COLS - 1])
        cells[COLS * (ROWS - 1)].border_color = (255,255,255)
        cells[COLS * (ROWS - 1)].border_thickness = 5
        cells[COLS - 1].border_color = (255,255,255)
        cells[COLS - 1].border_thickness = 2
    def setup_choices(self):
        global choices
        for x in range(len(colors)):
            _cell_pos_x = (cells[2].pos[0] + (cell_size//5)) + x * cell_size/1.5 + 15
            _cell_pos_y = cells[(COLS * ROWS )- 1].pos[1] + cell_size +(cell_size//5)
            _cell_pos = (_cell_pos_x,_cell_pos_y)
            _cell = Cell(_cell_pos,colors[x])
            _cell.size /= 1.5
            choices.append(_cell)
        self.update_choices()
    def update_choices(self):
        for choice in choices:
            if (choice.color == self.player_territory[0][0].color or choice.color == self.player_territory[1][0].color):
                choice.unavailable = True
            else:
                choice.unavailable = False
    def choose_color(self, chosen_color):
        global p1text,p2text
        #let current player pick a color, update_choices, then check for new territory, then rotate the turn
        self.alter_territory(self.turn,chosen_color)
        self.conquer_territory(self.turn,chosen_color)
        self.turn = 2 if self.turn == 1 else 1
        if(self.turn == 1):
            p1message = '--> Player(1): {} <--'.format(len(self.player_territory[0]))
        else:
            p1message = 'Player(1): {}'.format(len(self.player_territory[0]))
        if(self.turn == 2):
            p2message = '--> Player(2): {} <--'.format(len(self.player_territory[1]))
        else:
            p2message = 'Player(2): {}'.format(len(self.player_territory[1]))
        p1text = font.render(p1message,True,self.player_territory[0][0].color)
        p2text = font.render(p2message,True,self.player_territory[1][0].color)
        self.update_choices()
    def alter_territory(self, _player_num,new_color):
        if _player_num == 1:
            for owned in self.player_territory[0]:
                owned.color = new_color
        elif _player_num == 2:
            for owned in self.player_territory[1]:
                owned.color = new_color
        else:
            print('player num incorrect while alterting territory')
    def conquer_territory(self, _player_num, chosen_color):
        global ROWS, COLS, cells
        to_add = []
        #check every cell to see if it is adjacent to player territory AND it is the chosen color
        for x in range(len(cells)):
            #check below
            if(x <= (ROWS - 1) * COLS - 1):#not on bottom border <= 47  (7x8)
                if(cells[x].color == chosen_color and is_in(cells[x+COLS],self.player_territory[_player_num - 1]) ):
                    to_add.append(x)
            #check to the left
            if(x % COLS != 0):#not on left border
                if(cells[x].color == chosen_color and is_in(cells[x-1],self.player_territory[_player_num - 1]) ):
                    to_add.append(x)
            #check above
            if(x > ROWS):#not on top border
                if(cells[x].color == chosen_color and is_in(cells[x-COLS],self.player_territory[_player_num - 1]) ):
                    to_add.append(x)
            #check to the right
            if((x+1) % COLS != 0 and x < len(cells) - 1):#not on right border
                if(cells[x].color == chosen_color and is_in(cells[x+1],self.player_territory[_player_num - 1]) ):
                    to_add.append(x)
        for num in to_add:
            if(not is_in(cells[num],self.player_territory[_player_num-1])):
                self.player_territory[_player_num - 1].append(cells[num])
            cells[num].border_color = (255,255,255)
            cells[num].border_thickness = 2
        #after territory has been conquered, have we reached max capacity?
        print('Length of Player (1): {}'.format(len(self.player_territory[0])))
        print('Length of Player (2): {}'.format(len(self.player_territory[1])))
        print('Length of cells : {}'.format(len(cells)))

        if(len(self.player_territory[0]) + len(self.player_territory[1]) == len(cells)):
            if(len(self.player_territory[0]) > len(self.player_territory[1])):
                print('Player (1) has won!')
            elif(len(self.player_territory[0]) == len(self.player_territory[1])):
                print("Tie Game! Both players conquered the same amount of territory.")
            else:
                print('Player (2) has won!')




class Cell():
    def __init__(self, pos, color):
        self.size = cell_size
        self.pos = pos
        self.color = color
        self.border_color = (0,0,0)#black by default
        self.border_thickness = 1
        self.unavailable = False#used for choice selection
    def update(self):
        self.render()
    def render(self):
        pygame.draw.rect(screen,self.color,(*self.pos,self.size - 1,self.size - 1))
        pygame.draw.rect(screen, self.border_color, (*self.pos,self.size,self.size),self.border_thickness)



def update(game):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            check_mouse_collision(mouse_pos,game)
        elif event.type == pygame.KEYDOWN:#make a random move
            if event.key == pygame.K_UP:
                _r = random.randint(0,len(choices) - 1)
                while(choices[_r].unavailable == True):
                    _r = random.randint(0,len(choices) - 1)
                game.choose_color(choices[_r].color)

    for cell in cells:
        cell.update()
    for choice in choices:
        choice.update()

def render():
    pass

#aux funcs
def get_rand_color():
    _r = random.randint(0,len(colors) - 1)
    return colors[_r]

def check_mouse_collision(mouse_pos,game):
    global choices
    for choice in choices:
        if mouse_pos[0] >= choice.pos[0] and mouse_pos[0] <= choice.pos[0] + choice.size:
            if mouse_pos[1] >= choice.pos[1] and mouse_pos[1] <= choice.pos[1] + choice.size:
                #print('clicked on cell with color: {}. With unavailable status: {}'.format(choice.color,choice.unavailable))
                if(choice.unavailable == False):
                    game.choose_color(choice.color)
                else:
                    print('an unavailable color was chosen')
def is_in(thing, multiple_things):
    for object in multiple_things:
        if thing == object:
            return True
    return False
#end aux funcs


#test main
game = Game()
#end main


while True:
    screen.fill(background_color)
    y_pos = cells[ROWS * COLS - 1].pos[1] + cell_size + 15
    screen.blit(p1text,(5,y_pos))
    screen.blit(p2text,(5,y_pos + 50))

    update(game)
    render()
    pygame.display.flip()
    clock.tick(fps)
