# NECESSARY LIBRARIES
import random
from typing import Any
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.colors
import matplotlib.animation as plt_anim
from matplotlib.widgets import Button
import copy
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.offsetbox import AnchoredText
from matplotlib import gridspec
from scipy.ndimage import median_filter
import sys
import time
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# IMPORTING FROM OTHER FILES
from Chiara_Barbieri_517096_planisuss_constants import *
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Animal species present in the map
class Carviz():
    instance_count = 0

    def __init__(self, i, j):
        self.energy = MAX_ENERGY_C                          # when a Carviz is born, its energy is the maximum energy (100), represents the strenght of the individual
        self.lifetime = random.randint(1, MAX_LIFE_C)       # lifetime is choosen randomly between 0 and MAX_LIFE_C (10000)
        self.age = 0                                        # when a Carviz is born, the age is set to 0
        self.social_attitude = random.uniform(0,1)          # the social attitude of a Carviz in choosen randomly between 0 and 1
        self.i = i
        self.j = j
        self.death = False
        self.movement = False
    
    # To see the methods of the class
    def __str__ (self):
        return f'{self.energy} {self.lifetime} {self.age} {self.social_attitude} {self.i} {self.j}'

class Erbast():
    instance_count = 0

    def __init__(self, i, j):
        self.energy = MAX_ENERGY_E                          # when a Erbast is born, its energy is the maximum energy (100), represents the strenght of the individual
        self.lifetime = random.randint(1, MAX_LIFE_E)       # lifetime is choosen randomly between 0 and MAX_LIFE_E (10000)
        self.age = 0                                        # when as Erbast is born, the age is set to 0
        self.social_attitude = random.uniform(0,1)          # the social attitude of as Erbast in choosen randomly between 0 and 1
        self.i = i
        self.j = j
        self.death = False
        self.movement = False

    #To see the methods of the class
    def __str__ (self) :
        return f'{self.energy} {self.lifetime} {self.age} {self.social_attitude} {self.i} {self.j}'

# Class World: insert the individuals in the world map
class WorldInitialization:
    # Initialization of the world
    def __init__(self):
        self.terrainMap = self.loadTerrain()
        self.PrideMap = self.loadPride()
        self.HerdMap = self.loadHerd()

    # Initialization of the terrainMap
    def loadTerrain(self):
        terrainMap = np.zeros((NUMCELLS, NUMCELLS))
        m = np.ones((10, 10)) # matrix to have a smoother transition between the colors of the cells
        # 10x10 matrix m

        # Defining water
        for i in range(10):
                m[0][:] = 0
                m[-1][:] = 0
                m[i][0] = 0
                m[i][-1] = 0
        
        # Defining the density of vegetobs within the matrix
        for i in range(10):
            for j in range(10):
                if m[i][j] != 0 and (random.uniform(0.0, 1.0) > (1 - TERRAIN_PROB)):
                    m[i][j] = random.randint(1, 10)
                else:
                    m[i][j] = 0

        m = (m / 10.0) * 100
        for i in range(NUMCELLS):
            for j in range(NUMCELLS):
                i1 = (i // 10)
                j1 = (j // 10)
                terrainMap[i][j] = m[i1][j1]
                # From which we get that each value of the 100x100 matrix is:
                 # 0: water
                 # 1: terrain
                 # 2-10: vegetob density
        terrainMap = np.rint(terrainMap).astype(int)
        # Filters to have a gradient (smooth transition from water to terrain and vegetobs)
        terrainMap = median_filter(terrainMap, 10)
        terrainMap = median_filter(terrainMap, 5)
        return terrainMap
    
    # Initialization of the prideMap
    def loadPride(self):
        PrideMap = [[[] for _ in range(NUMCELLS)] for _ in range(NUMCELLS)]
        n = 1
        while 1 <= n <= MAX_NUMBER_C:
            i = random.randint(0, NUMCELLS-1)
            j = random.randint(0, NUMCELLS-1)
            if self.terrainMap[i][j] != 0: # No water and no Herd
                c = Carviz(i, j)
                Carviz.instance_count += 1
                PrideMap[i][j].append(c)
                n += 1
        return PrideMap

    # Initializaation of the herdMap
    def loadHerd(self):
        HerdMap = [[[] for _ in range(NUMCELLS)] for _ in range(NUMCELLS)]
        n = 1
        while 1 <= n <= MAX_NUMBER_E:
            i = random.randint(0, NUMCELLS-1)
            j = random.randint(0, NUMCELLS-1)
            if self.terrainMap[i][j] != 0 and len(self.PrideMap[i][j]) == 0: # No water and no Pride
                e = Erbast(i, j)
                Erbast.instance_count += 1
                HerdMap[i][j].append(e)
                n += 1
        return HerdMap
    
# ---------------------------------------------------------------------------------------------------------
# Display class: Show the world and actions of the individuals

class Display:
    def __init__(self, worldInit):
        # To access the maps defined above:
        self.world = worldInit

        self.terrainColorCodes = [
            "#52D7FF", # water ("cyan")
            "#A1683E", # earth ("brown")
            "#81F65F", # 1 < vegetob < 10
            "#75DF56", # 10 < vegetob < 20 
            "#6ACF4D", # 20 < vegetob < 30
            "#60BD45", # 30 < vegetob < 40
            "#75BB62", # 40 < vegetob < 50
            "#4B9436", # 50 < vegetob < 60 
            "#40862B", # 60 < vegetob < 70 
            "#377027", # 70 < vegetob < 80
            "#29541C", # 80 < vegetob < 90
            "#254C19", #  90 < vegetob < 100
            "#152B0E" # vegetob = 100
        ]

        self.terrainTickLabels = [
            "water",
            "terrain",
            "1 < vegetob <= 10",
            "10 < vegetob <= 20",
            "20 < vegetob <= 30",
            "30 < vegetob <= 40",
            "40 < vegetob <= 50",
            "50 < vegetob <= 60",
            "60 < vegetob <= 70",
            "70 < vegetob <= 80",
            "80 < vegetob <= 90",
            "90 < vegetob < 100",
            "vegetob = 100"
        ]

        # In the following color codes we add 00 or FF to make it invisible or visible (respectively)
        self.prideColorCodes = [
            "#FFFFFF00", # no animal - white
            "#EE7367FF", # 1...10
            "#D34C3EFF", # 11...20 
            "#E61313FF", # 21...30
            "#C91010FF", # 31...40
            "#A80C0CFF", # 41...60
            "#8E0909FF", # 61...80
            "#700707FF", # 81...99
            "#480404FF"  # 100
        ]

        self.prideTicketLabels = [
            "no Pride",
            "1...10",
            "11...20",
            "21...30",
            "31...40",
            "41...60",
            "61...80",
            "81...99",
            "100"
        ]

        self.herdColorCodes = [
            "#FFFFFF00", # no animal - white
            "#DBBBF1FF", # 1...100
            "#D49EF9FF", # 101...200 
            "#B456F6FF", # 201...300
            "#8B03EBFF", # 301...400
            "#6D01B9FF", # 401...600
            "#693695FF", # 601...800
            "#550896FF", # 801...999
            "#45146EFF"  # 1000
        ]

        self.herdTicketlabels = [
            "no Herd ",
            "1...100",
            "101...200",
            "201...300",
            "301...400",
            "401...600",
            "601...800",
            "801...999",
            "1000"
        ]

        self.scatter_herd, self.scatter_pride, self.img_terrain, self.fig, self.ax, self.visualization_terrain, self.visualization_pride, self.visualization_herd = self.showAllMaps()

    def show(self):
        plt.ion()  # Enable interactive mode
        plt.show(block=True)
    
    def showAllMaps(self):
        fig = plt.figure(figsize=(14, 7))
        gs = fig.add_gridspec(1, 2, width_ratios=[3, 1])

        ax = fig.add_subplot(gs[0])
        ax.set_title('World Display')

        # TERRAIN MAP
        self.visualization_terrain = np.zeros((NUMCELLS, NUMCELLS))
        for i in range(NUMCELLS):
            for j in range(NUMCELLS):
                if self.world.terrainMap[i][j] == 0:                                                 self.visualization_terrain[i][j] = 0
                elif self.world.terrainMap[i][j] == 1:                                               self.visualization_terrain[i][j] = 1
                elif self.world.terrainMap[i][j] > 1 and self.world.terrainMap[i][j] <= 10:          self.visualization_terrain[i][j] = 2
                elif self.world.terrainMap[i][j] > 10 and self.world.terrainMap[i][j] <= 20:         self.visualization_terrain[i][j] = 3
                elif self.world.terrainMap[i][j] > 20 and self.world.terrainMap[i][j] <= 30:         self.visualization_terrain[i][j] = 4
                elif self.world.terrainMap[i][j] > 30 and self.world.terrainMap[i][j] <= 40:         self.visualization_terrain[i][j] = 5
                elif self.world.terrainMap[i][j] > 40 and self.world.terrainMap[i][j] <= 50:         self.visualization_terrain[i][j] = 6
                elif self.world.terrainMap[i][j] > 50 and self.world.terrainMap[i][j] <= 60:         self.visualization_terrain[i][j] = 7
                elif self.world.terrainMap[i][j] > 60 and self.world.terrainMap[i][j] <= 70:         self.visualization_terrain[i][j] = 8
                elif self.world.terrainMap[i][j] > 70 and self.world.terrainMap[i][j] <= 80:         self.visualization_terrain[i][j] = 9
                elif self.world.terrainMap[i][j] > 80 and self.world.terrainMap[i][j] <= 90:         self.visualization_terrain[i][j] = 10
                elif self.world.terrainMap[i][j] > 90 and self.world.terrainMap[i][j] < 100:         self.visualization_terrain[i][j] = 11
                elif self.world.terrainMap[i][j] >= 100:                                             self.visualization_terrain[i][j] = 12

        terrain_colors = [matplotlib.colors.hex2color(code) for code in self.terrainColorCodes]
        terrain_cmap = matplotlib.colors.ListedColormap(terrain_colors)
        norm_terrain = matplotlib.colors.Normalize(vmin=0, vmax=12)
        # Display the matrix:
        self.img_terrain = ax.matshow(self.visualization_terrain, cmap=terrain_cmap, norm=norm_terrain)

        # PRIDE MAP
        self.visualization_pride = np.ones((NUMCELLS, NUMCELLS))
        for i in range(0, NUMCELLS):
            for j in range(0, NUMCELLS):
                nbrPride = len(self.world.PrideMap[i][j])
                if nbrPride == 0:                            self.visualization_pride[i][j] = 0 
                elif nbrPride > 0 and nbrPride <= 10:        self.visualization_pride[i][j] = 1 
                elif nbrPride > 10 and nbrPride <= 20:       self.visualization_pride[i][j] = 2 
                elif nbrPride > 20 and nbrPride <= 30:       self.visualization_pride[i][j] = 3 
                elif nbrPride > 30 and nbrPride <= 40:       self.visualization_pride[i][j] = 4 
                elif nbrPride > 40 and nbrPride <= 60:       self.visualization_pride[i][j] = 5 
                elif nbrPride > 60 and nbrPride <= 80:       self.visualization_pride[i][j] = 6 
                elif nbrPride > 80 and nbrPride <= 99:       self.visualization_pride[i][j] = 7 
                elif nbrPride >=100:                         self.visualization_pride[i][j] = 8

        cmap_pride = matplotlib.colors.ListedColormap([matplotlib.colors.hex2color(code) for code in self.prideColorCodes if code != "#FFFFFF00"])
        norm_pride = matplotlib.colors.Normalize(vmin=0, vmax=8)

        pride_x = []
        pride_y = []
        pride_colors = []
        for i in range(0, 100):
            for j in range(0, 100):
                if len(self.world.PrideMap[i][j]) > 0:
                    pride_x.append(j)
                    pride_y.append(i)
                    pride_colors.append(self.visualization_pride[i][j])
        self.scatter_pride = ax.scatter(pride_x, pride_y, c=pride_colors, cmap=cmap_pride, norm=norm_pride, label='Pride', alpha=1, edgecolors='w')

        # HERD MAP
        self.visualization_herd = np.ones((NUMCELLS, NUMCELLS))
        for i in range(0, NUMCELLS):
            for j in range(0, NUMCELLS):
                nbrHerd = len(self.world.HerdMap[i][j])
                if nbrHerd == 0:                          self.visualization_herd[i][j] = 0                
                elif nbrHerd > 0 and nbrHerd <= 100:      self.visualization_herd[i][j] = 1                 
                elif nbrHerd > 100 and nbrHerd <= 200:    self.visualization_herd[i][j] = 2                
                elif nbrHerd > 200 and nbrHerd <= 300:    self.visualization_herd[i][j] = 3                 
                elif nbrHerd > 300 and nbrHerd <= 400:    self.visualization_herd[i][j] = 4                
                elif nbrHerd > 400 and nbrHerd <= 600:    self.visualization_herd[i][j] = 5                
                elif nbrHerd > 400 and nbrHerd <= 600:    self.visualization_herd[i][j] = 5                
                elif nbrHerd > 400 and nbrHerd <= 600:    self.visualization_herd[i][j] = 5                
                elif nbrHerd > 600 and nbrHerd <= 800:    self.visualization_herd[i][j] = 6                
                elif nbrHerd > 800 and nbrHerd <= 999:    self.visualization_herd[i][j] = 7 
                elif nbrHerd >= 1000:                     self.visualization_herd[i][j] = 8

        cmap_herd = matplotlib.colors.ListedColormap([matplotlib.colors.hex2color(code) for code in self.herdColorCodes if code != "#FFFFFF00"])
        norm_herd = matplotlib.colors.Normalize(vmin=0, vmax=8)

        herd_x = []
        herd_y = []
        herd_colors = []
        for i in range(0, 100):
            for j in range(0, 100):
                if len(self.world.HerdMap[i][j]) > 0:
                    herd_x.append(j)
                    herd_y.append(i)
                    herd_colors.append(self.visualization_herd[i][j])

        self.scatter_herd = ax.scatter(herd_x, herd_y, c=herd_colors, cmap=cmap_herd, norm=norm_herd, label='Herd', alpha=1, edgecolors='w')

        # Add the colorbars for terrain, pride, and herd
        divider = make_axes_locatable(ax)
        cax_terrain = divider.append_axes("right", size="5%", pad=0.1)
        cax_pride = divider.append_axes("right", size="5%", pad=1.4)
        cax_herd = divider.append_axes("right", size="5%", pad=1.2)

        colorbar_terrain = fig.colorbar(self.img_terrain, cax=cax_terrain)
        colorbar_terrain.locator = matplotlib.ticker.FixedLocator([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        colorbar_terrain.ax.set_yticklabels(self.terrainTickLabels)
        colorbar_terrain.ax.tick_params(labelsize='small')

        colorbar_pride = fig.colorbar(self.scatter_pride, cax=cax_pride)
        colorbar_pride.locator = matplotlib.ticker.FixedLocator([0, 1, 2, 3, 4, 5, 6, 7, 8])
        colorbar_pride.ax.set_yticklabels(self.prideTicketLabels)
        colorbar_pride.ax.tick_params(labelsize='small')

        colorbar_herd = fig.colorbar(self.scatter_herd, cax=cax_herd)
        colorbar_herd.locator = matplotlib.ticker.FixedLocator([0, 1, 2, 3, 4, 5, 6, 7, 8])
        colorbar_herd.ax.set_yticklabels(self.herdTicketlabels)
        colorbar_herd.ax.tick_params(labelsize='small')

        return self.scatter_herd, self.scatter_pride, self.img_terrain, fig, ax, self.visualization_terrain, self.visualization_pride, self.visualization_herd

class DayInPlanisuss():
    def __init__(self, worldInit, display, planisuss_properties):
        # Taking from the above classes
        self.world = worldInit
        self.display = display
        self.planisuss_properties = planisuss_properties
        # time interval between an iteration and another (a day and another)
        self.interval = 400
        self.speed = 400
        # Passing time and frames
        self.current_frame = -1
        self.days = 0
        self.months = 0
        self.years = 0
        self.decades = 0
        self.centuries = 0
        # Pausing restarting the animation
        self.paused = False
        # Stopping the animation
        self.terminate = False
        # Resetting the animation
        self.restart = False
        # Initialize statistics attributes
        self.numPrides = 0
        self.numHerds = 0
        self.numErbast = 0
        self.numCarviz = 0
        self.mediaVegetob = 0
        self.mediaPride = 0
        self.mediaHerds = 0
        # Store the initial state of the maps
        self.initial_terrainMap = np.copy(worldInit.terrainMap)
        self.initial_PrideMap = copy.deepcopy(worldInit.PrideMap)
        self.initial_HerdMap = copy.deepcopy(worldInit.PrideMap)
        # Buttons
        self.create_buttons()
        # Connect the click event for fetching cell properties
        self.state_history = []
        self.display.fig.canvas.mpl_connect('button_press_event', self.on_click_properties)
        self.click_detected = False
        self.display.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.cell_info_box = None
        # For the animation
        self.animated = self.animate()
        
    # Update of the terrain map
    def update_terrain(self, terrain):
        for i in range(NUMCELLS):
            for j in range(NUMCELLS):
                if self.world.terrainMap[i][j] == 0:                                                 self.display.visualization_terrain[i][j] = 0
                elif self.world.terrainMap[i][j] == 1:                                               self.display.visualization_terrain[i][j] = 1
                elif self.world.terrainMap[i][j] > 1 and self.world.terrainMap[i][j] <= 10:          self.display.visualization_terrain[i][j] = 2
                elif self.world.terrainMap[i][j] > 10 and self.world.terrainMap[i][j] <= 20:         self.display.visualization_terrain[i][j] = 3
                elif self.world.terrainMap[i][j] > 20 and self.world.terrainMap[i][j] <= 30:         self.display.visualization_terrain[i][j] = 4
                elif self.world.terrainMap[i][j] > 30 and self.world.terrainMap[i][j] <= 40:         self.display.visualization_terrain[i][j] = 5
                elif self.world.terrainMap[i][j] > 40 and self.world.terrainMap[i][j] <= 50:         self.display.visualization_terrain[i][j] = 6
                elif self.world.terrainMap[i][j] > 50 and self.world.terrainMap[i][j] <= 60:         self.display.visualization_terrain[i][j] = 7
                elif self.world.terrainMap[i][j] > 60 and self.world.terrainMap[i][j] <= 70:         self.display.visualization_terrain[i][j] = 8
                elif self.world.terrainMap[i][j] > 70 and self.world.terrainMap[i][j] <= 80:         self.display.visualization_terrain[i][j] = 9
                elif self.world.terrainMap[i][j] > 80 and self.world.terrainMap[i][j] <= 90:         self.display.visualization_terrain[i][j] = 10
                elif self.world.terrainMap[i][j] > 90 and self.world.terrainMap[i][j] < 100:         self.display.visualization_terrain[i][j] = 11
                elif self.world.terrainMap[i][j] >= 100:                                             self.display.visualization_terrain[i][j] = 12
        return self.display.visualization_terrain
    
    # Update of the scatter plot for the Prides
    def update_scatterPride(self):
        new_positions_prideMap = []
        for i in range(NUMCELLS):
            for j in range(NUMCELLS):
                if self.world.PrideMap[i][j] != []:
                    for carviz in self.world.PrideMap[i][j][:]:
                        if isinstance(carviz, Carviz):
                            carviz.i = i
                            carviz.j = j
                            if carviz.death == False:
                                new_positions_prideMap.append([carviz.j, carviz.i])
                            else:
                                if Carviz.instance_count > 0:
                                    Carviz.instance_count -= 1
                                else:
                                    carviz.instance_count = 0
                                self.world.PrideMap[i][j].remove(carviz)
        if len(new_positions_prideMap) == 0:
            new_positions_prideMap = np.empty((0, 2))
        else:
            new_positions_prideMap = np.array(new_positions_prideMap)

        self.display.scatter_pride.set_offsets(new_positions_prideMap)
        return new_positions_prideMap
    
    # Counting of the number of Prides
    def num_Prides(self):
        numPrides = 0
        for i in range(NUMCELLS):
            for j in range(NUMCELLS):
                if len(self.world.PrideMap[i][j]) > 1:
                    numPrides += 1
        return numPrides

    # Update of the scatter plot for the Herds
    def update_scatterHerd(self):
        new_positions_herdMap = []
        for i in range(NUMCELLS):
            for j in range(NUMCELLS):
                if self.world.HerdMap[i][j] != []:
                    for erbast in self.world.HerdMap[i][j][:]:
                        if isinstance(erbast, Erbast):
                            erbast.i = i
                            erbast.j = j
                            if erbast.death == False:
                                new_positions_herdMap.append([erbast.j, erbast.i])
                            else:
                                if Erbast.instance_count > 0:
                                    Erbast.instance_count -= 1
                                else:
                                    Erbast.instance_count = 0
                                self.world.HerdMap[i][j].remove(erbast)
        if len(new_positions_herdMap) == 0:
            new_positions_herdMap = np.empty((0, 2))
        else:
            new_positions_herdMap = np.array(new_positions_herdMap)
        self.display.scatter_herd.set_offsets(new_positions_herdMap)
        return new_positions_herdMap
    
    # Count of the number of Herds
    def num_Herds(self):
        numHerds = 0
        for i in range(NUMCELLS):
            for j in range(NUMCELLS):
                if len(self.world.HerdMap[i][j]) > 1:
                    numHerds += 1
        return numHerds

    # Media of the vegeotob
    def mediaOfVegetob(self):
        numVegetob = 0
        for i in range(NUMCELLS):
            for j in range(NUMCELLS):
                if self.world.terrainMap[i][j] > 0:
                    numVegetob += self.world.terrainMap[i][j]
        mediaVegetob = numVegetob / (NUMCELLS**2)
        return int(mediaVegetob)

    # Media of the energy of the Pride
    def mediaOfEnergy_carviz(self):
        numEnergy = 0
        for i in range(NUMCELLS):
            for j in range(NUMCELLS):
                if len(self.world.PrideMap[i][j]) >= 1:
                    for carviz in self.world.PrideMap[i][j]:
                        if isinstance(carviz, Carviz):
                            numEnergy += carviz.energy
        if Carviz.instance_count > 0:
            mediaEnergyCarviz = numEnergy / Carviz.instance_count
        else:
            mediaEnergyCarviz = 0
        return int(mediaEnergyCarviz)

    # Media of the energy of the herd
    def mediaOfEnergy_erbast(self):
        numEnergy = 0
        for i in range(NUMCELLS):
            for j in range(NUMCELLS):
                if len(self.world.HerdMap[i][j]) >= 1:
                    for erbast in self.world.HerdMap[i][j]:
                        if isinstance(erbast, Erbast):
                            numEnergy += erbast.energy
        if Erbast.instance_count > 0:
            mediaEnergyErbast = numEnergy / Erbast.instance_count
        else:
            mediaEnergyErbast = 0
        return int(mediaEnergyErbast)
   
    # Growing of the Vegetob
    def growing_vegetob(self):
        for i in range(NUMCELLS-1):
            for j in range(NUMCELLS-1):
                if 1 <= self.world.terrainMap[i][j] <= 101:
                    self.world.terrainMap[i][j] += GROWING
                    if self.world.terrainMap[i][j] > MAX_VEGETOB:
                        self.world.terrainMap[i][j] = MAX_VEGETOB
                if (
                    self.world.terrainMap[i-1][j+1] == 100 and
                    self.world.terrainMap[i][j+1] == 100 and
                    self.world.terrainMap[i+1][j+1] == 100 and
                    self.world.terrainMap[i-1][j] == 100 and
                    self.world.terrainMap[i+1][j] == 100 and
                    self.world.terrainMap[i-1][j-1] == 100 and
                    self.world.terrainMap[i][j-1] == 100 and
                    self.world.terrainMap[i+1][j-1] == 100
                ):
                    if self.world.PrideMap[i][j] != []:
                        for carviz in self.world.PrideMap[i][j]:
                            if isinstance(carviz, Carviz):
                                carviz.death = True
                                print("Carviz dead, overwhelmed by vegetob")
                    if self.world.HerdMap[i][j] != []:
                        for erbast in self.world.HerdMap[i][j]:
                            if isinstance(erbast, Erbast):
                                erbast.death = True
                                print("Erbast dead, overwhelmed by vegetob")
                else:
                    self.world.terrainMap[i][j]
        return self.update_terrain(self.world.terrainMap)

    # Movement of the Prides or Carviz    
    def update_movementPride(self):
        for i in range(NUMCELLS):
            for j in range(NUMCELLS):
                if self.world.PrideMap[i][j] != []:
                    for pride_member in self.world.PrideMap[i][j][:]:
                        if isinstance(pride_member, Carviz):
                            if pride_member.death == False:
                                moves_C = [
                                    (i - NEIGHBORHOOD_C, j + NEIGHBORHOOD_C),
                                    (i, j + NEIGHBORHOOD_C),
                                    (i + NEIGHBORHOOD_C, j + NEIGHBORHOOD_C),
                                    (i - NEIGHBORHOOD_C, j),
                                    (i + NEIGHBORHOOD_C, j),
                                    (i - NEIGHBORHOOD_C, j - NEIGHBORHOOD_C),
                                    (i, j - NEIGHBORHOOD_C),
                                    (i + NEIGHBORHOOD_C, j - NEIGHBORHOOD_C)
                                ]
                                pride_member.movement = False
                                next_i = i
                                next_j = j

                                # The carviz or Pride wants to move
                                if (pride_member.social_attitude > 0.5 or pride_member.energy > 50) or (pride_member.social_attitude > 0.5 and pride_member.energy > 50):
                                    # Towards the Herds
                                    next_move = max(moves_C, key=lambda pos: len(self.world.HerdMap[max(0, min(NUMCELLS-1, pos[0]))][max(0, min(NUMCELLS-1, pos[1]))]))
                                    next_i = max(0, min(NUMCELLS-1, next_move[0]))
                                    next_j = max(0, min(NUMCELLS-1, next_move[1]))
                                    if self.world.HerdMap[next_i][next_j] != []:
                                        pass
                                    else:
                                        # Towards higher vegetob densities
                                        next_move = max(moves_C, key=lambda pos: self.world.terrainMap[max(0, min(NUMCELLS-1, pos[0]))][max(0, min(NUMCELLS-1, pos[1]))])
                                        next_i = max(0, min(NUMCELLS-1, next_move[0]))
                                        next_j = max(0, min(NUMCELLS-1, next_move[1]))
                                        if 0 < self.world.terrainMap[next_i][next_j] < 70:
                                            pass
                                        else:
                                            # Escaping from the vegetob with too high density
                                            next_move = min(moves_C, key=lambda pos: self.world.terrainMap[max(0, min(NUMCELLS-1, pos[0]))][max(0, min(NUMCELLS-1, pos[1]))])
                                            next_i = max(0, min(NUMCELLS-1, next_move[0]))
                                            next_j = max(0, min(NUMCELLS-1, next_move[1]))
                                            if self.world.terrainMap[next_i][next_j] > 70:
                                                pass
                                            else:
                                                if (pride_member.social_attitude > 0.5 or pride_member.energy > 80) or (pride_member.social_attitude > 0.5 and pride_member.energy > 80):
                                                    next_move = random.choice(moves_C)
                                                    next_i = max(0, min(NUMCELLS-1, next_move[0]))
                                                    next_j = max(0, min(NUMCELLS-1, next_move[1]))
                                                # If we arrive here the carviz have no reason to move
                                                else:
                                                    self.world.PrideMap[i][j]
                                                    pride_member.i = i
                                                    pride_member.j = j

                                if self.world.terrainMap[next_i][next_j] != 0:
                                    if len(self.world.PrideMap[next_i][next_j]) > 1:
                                        for carviz in self.world.PrideMap[next_i][next_j]:
                                            if isinstance(carviz, Carviz):
                                                pride_socialAttitudes = [carviz.social_attitude]
                                                # The group in the next group has too low social attitude, so they will fight
                                                if sum(pride_socialAttitudes) < 0.5 * len(self.world.PrideMap[next_i][next_j]):
                                                    pride_1 = self.world.PrideMap[i][j].copy()
                                                    pride_2 = self.world.PrideMap[next_i][next_j].copy()
                                                    
                                                    self.world.PrideMap[i][j].clear()
                                                    self.world.PrideMap[next_i][next_j].clear()
                                                    
                                                    winner = self.fight(pride_1, pride_2)
                                                    if winner == pride_1:
                                                        for carviz in pride_1:
                                                            self.world.PrideMap[next_i][next_j].append(carviz)
                                                            carviz.movement = True
                                                            carviz.social_attitude += 0.2
                                                    else:
                                                        for carviz in pride_2:
                                                            self.world.PrideMap[next_i][next_j].append(carviz)
                                                            carviz.movement = True
                                                            carviz.social_attitude += 0.2
                                                    print(f"Fight in cell ({i},{j}). Winner: {'Pride 1' if winner == pride_1 else 'Pride 2'}")
                                                    
                                                else:
                                                    # Further check
                                                    if pride_member in self.world.PrideMap[i][j] and pride_member.death == False:
                                                        self.world.PrideMap[next_i][next_j].append(pride_member)
                                                        self.world.PrideMap[i][j].remove(pride_member)
                                                        pride_member.i = next_i
                                                        pride_member.j = next_j
                                                        pride_member.energy -= 1  # Movement costs each individual one point of energy
                                                        pride_member.movement = True
                                    # There are no Carviz in the next cell
                                    else:
                                        if pride_member in self.world.PrideMap[i][j] and pride_member.death == False:
                                            self.world.PrideMap[next_i][next_j].append(pride_member)
                                            self.world.PrideMap[i][j].remove(pride_member)
                                            pride_member.i = next_i
                                            pride_member.j = next_j
                                            pride_member.energy -= 1  # Movement costs each individual one point of energy
                                            pride_member.movement = True
                                # The carviz or the pride decides not to move
                                else:
                                    self.world.PrideMap[i][j]
                                    pride_member.i = i
                                    pride_member.j = j
                                
        return self.world.PrideMap

    # Movement of the Herds or Erbast
    def update_movementHerd(self):
        for i in range(NUMCELLS):
            for j in range(NUMCELLS):
                if self.world.HerdMap[i][j] != []:
                    for herd_member in self.world.HerdMap[i][j][:]:
                        if isinstance(herd_member, Erbast):
                            if herd_member.death == False:
                                moves_E = [
                                    (i - NEIGHBORHOOD_E, j + NEIGHBORHOOD_E),
                                    (i, j + NEIGHBORHOOD_E),
                                    (i + NEIGHBORHOOD_E, j + NEIGHBORHOOD_E),
                                    (i - NEIGHBORHOOD_E, j),
                                    (i + NEIGHBORHOOD_E, j),
                                    (i - NEIGHBORHOOD_E, j - NEIGHBORHOOD_E),
                                    (i, j - NEIGHBORHOOD_E),
                                    (i + NEIGHBORHOOD_E, j - NEIGHBORHOOD_E)
                                ]
                                herd_member.movement = False
                                next_i = i
                                next_j = j

                                # The Erbast or the Herd wants to move
                                if (herd_member.social_attitude > 0.5 or herd_member.energy > 50) or (herd_member.social_attitude > 0.5 and herd_member.energy > 50):
                                    if 0 < self.world.terrainMap[i][j] <= 50:
                                        # Towards the Erbast
                                        next_move = max(moves_E, key=lambda pos: self.world.terrainMap[pos[0]][pos[1]])
                                        next_i = max(0, min(NUMCELLS-1, next_move[0]))
                                        next_j = max(0, min(NUMCELLS-1, next_move[1]))
                                        if self.world.terrainMap[next_i][next_j] != 0:
                                            pass
                                        else:
                                            # Escaping from the vegetob with too high density
                                            next_move = min(moves_E, key=lambda pos: self.world.terrainMap[max(0, min(NUMCELLS-1, pos[0]))][max(0, min(NUMCELLS-1, pos[1]))])
                                            next_i = max(0, min(NUMCELLS-1, next_move[0]))
                                            next_j = max(0, min(NUMCELLS-1, next_move[1]))
                                            if self.world.terrainMap[next_i][next_j] > 70:
                                                pass
                                            else:
                                                # Escaping from the Prides
                                                next_move = min(moves_E, key=lambda pos: len(self.world.HerdMap[pos[0]][pos[1]]))
                                                next_i = max(0, min(NUMCELLS-1, next_move[0]))
                                                next_j = max(0, min(NUMCELLS-1, next_move[1]))
                                                if self.world.PrideMap[next_i][next_j] == []:
                                                    pass
                                                else:
                                                    if (herd_member.social_attitude > 0.5 or herd_member.energy > 70) or (herd_member.social_attitude > 0.5 and herd_member.energy > 70):
                                                        next_move = random.choice(moves_E)
                                                        next_i = max(0, min(NUMCELLS-1, next_move[0]))
                                                        next_j = max(0, min(NUMCELLS-1, next_move[1]))
                                                    # If we arrive here the erbast have no reason to move
                                                    else:
                                                        self.world.HerdMap[i][j]
                                                        herd_member.movement = False
                                                        herd_member.i = i
                                                        herd_member.j = j

                                if self.world.terrainMap[next_i][next_j] != 0:
                                    self.world.HerdMap[next_i][next_j].append(herd_member)
                                    self.world.HerdMap[i][j].remove(herd_member)
                                    herd_member.i = next_i
                                    herd_member.j = next_j
                                    herd_member.energy -= 1  # Movement costs each individual one point of energy
                                    herd_member.movement = True
                                else:
                                    # Stay in place since it decided not to move
                                    self.world.HerdMap[i][j]
                                    herd_member.movement = False
                                    herd_member.i = i
                                    herd_member.j = j

        return self.world.HerdMap
 
    # Grazing of the Erbast
    def grazing(self):
        for i in range(NUMCELLS):
            for j in range(NUMCELLS):
                if self.world.HerdMap[i][j] != []:
                    # Erbast that did not move
                    no_moving_e = [erbast for erbast in self.world.HerdMap[i][j] if isinstance(erbast, Erbast) and not erbast.movement and not erbast.death]
                    if no_moving_e:
                        # vegetob density greater than number of Erbasts
                        if self.world.terrainMap[i][j] >= len(no_moving_e):
                            for erbast in no_moving_e:
                                erbast.energy += 1
                                self.world.terrainMap[i][j] -= 1
                                print(f'vegetob eaten by erbast')
                        # vegetob density lower than number of Erbast
                        else: 
                            #sort the Erbast in ascending order based on their current energy
                            no_moving_e.sort(key=lambda x: x.energy)
                            #assign the energy from the Erbast with lower energy
                            for k in range(self.world.terrainMap[i][j]):
                                no_moving_e[k].energy += 1
                                self.world.terrainMap[i][j] -= 1
                            #decrease social attitude of the individuals that didn't eat
                            for erbast in no_moving_e[self.world.terrainMap[i][j]:]:
                                erbast.social_attitude -= 0.2
        return self.update_terrain(self.world.terrainMap) #self.world.HerdMap

    # Fighting between carviz: called in movement
    def fight(self, pride_1, pride_2):
        winner = None

        #remove champion with lower energy 
        while len(pride_1) >= 1 and len(pride_2) >= 1:
            #define the champions
            for carviz_1 in pride_1:
                if isinstance(carviz_1, Carviz):
                    champion_1 = max(pride_1, key=lambda carviz: carviz_1.energy)

            for carviz_2 in pride_2:
                if isinstance(carviz_2, Carviz):
                    champion_2 = max(pride_2, key=lambda carviz: carviz_2.energy)

            if champion_1.energy >= champion_2.energy:
                champion_2.death = True
                pride_2.remove(champion_2)
                Carviz.instance_count -= 1
                print("Carviz dead, lost a fight")
            else:
                champion_1.death = True
                pride_1.remove(champion_1)
                Carviz.instance_count -= 1
                print("Carviz dead, lost a fight")
            
        if pride_2 == []:
            winner = pride_1
        if pride_1 == []:
            winner = pride_2

        return winner

    # Hunting of the Carviz
    def hunt(self):
        for i in range(NUMCELLS):
            for j in range(NUMCELLS):
                pride = self.world.PrideMap[i][j]
                if len(pride) == 1:
                    for carviz in pride:
                        if isinstance(carviz, Carviz):
                            if not carviz.movement and not carviz.death: # No movement, so no fight
                                if len(self.world.HerdMap[i][j]) > 0: #check there are erbast in the cell
                                    strongest_erbast = max(self.world.HerdMap[i][j], key=lambda erbast: erbast.energy) #the strongest erbast
                                    energy_pride = sum(carviz.energy for carviz in pride)
                                    prob_success = energy_pride / (energy_pride + strongest_erbast.energy)

                                    #hunt is successfull
                                    if random.random() < prob_success:
                                        energy_carviz = strongest_erbast.energy // len(pride) #energy to give to each carviz
                                        spare_energy = strongest_erbast.energy % len(pride) #spare energy

                                        for carviz in pride:
                                            carviz.energy += energy_carviz
                                    
                                        #assign spare energy 
                                        pride.sort(key=lambda carviz: carviz.energy) #sort the pride components by their energy in ascending order
                                        pride[0].energy += spare_energy #assign the spare energy to the carviz with lower energy

                                        #increase social attitude of winning pride components
                                        for carviz in pride:
                                            carviz.social_attitude += 0.2
                                    
                                        #the erbast dies
                                        strongest_erbast.death = True
                                        print(f'Erbast dead because was hunted')
                                
                                    #hunt is unsuccessful
                                    else:
                                        #pride memebers' social attitude decrases
                                        for carviz in pride:
                                            carviz.social_attitude -= max(carviz.social_attitude - 0.2, 0) #ensure social attitude doesn't go below 0
                                        #herd members' social attitude increases 
                                        for erbast in self.world.HerdMap[i][j]:
                                            erbast.social_attitude += 0.2
                                        #fruitless assault costs energy to a random individual in the pride
                                        random_carviz = random.choice(pride)
                                        random_carviz.energy -= max(random_carviz.energy - 0.2, 0) #ensure energy doesn't go below 0

        return self.world.HerdMap, self.world.PrideMap
    
    # Aging of the animals
    def aging(self):
        for i in range(NUMCELLS):
            for j in range(NUMCELLS):
                if self.world.PrideMap[i][j] != [] and self.world.HerdMap[i][j] != []:
                    for carviz in self.world.PrideMap[i][j]:
                        if isinstance(carviz, Carviz):
                            if carviz.death == False:
                                carviz.i = i
                                carviz.j = j
                                carviz.age += 1
                                if carviz.age > 1:
                                    if carviz.age // 10 == 0:
                                        carviz.energy -= 2
                    for erbast in self.world.HerdMap[i][j]:
                        if isinstance(erbast, Erbast):
                            if erbast.death == False:
                                erbast.i = i 
                                erbast.j = j
                                erbast.age += 1
                                if erbast.age > 1:
                                    if erbast.age % 10 == 0:
                                        erbast.energy -= 2
        return self.world.PrideMap, self.world.HerdMap
    
    # Spawn of the animals
    def spawning(self):
        for i in range(NUMCELLS):
            for j in range(NUMCELLS):
                if self.world.PrideMap[i][j] != []:
                    for carviz in self.world.PrideMap[i][j]:
                        if isinstance(carviz, Carviz):
                            if carviz.death == False:
                                carviz.i = i
                                carviz.j = j
                                first_offspring = None
                                second_offspring = None
                                if carviz.age >= carviz.lifetime and carviz.energy > 0:
                                    if len(self.world.PrideMap[i][j]) <= MAX_PRIDE:
                                        first_offspring = Carviz(carviz.i, carviz.j)
                                        Carviz.instance_count += 1
                                        first_offspring.age = 0
                                        first_offspring.energy = random.randint(1, carviz.energy)
                                        first_offspring.lifetime = carviz.lifetime
                                        first_offspring.social_attitude = carviz.social_attitude
                                        self.world.PrideMap[i][j].append(first_offspring)

                                        second_offspring = Carviz(carviz.i, carviz.j)
                                        Carviz.instance_count += 1
                                        second_offspring.age = 0
                                        second_offspring.energy = carviz.energy - first_offspring.energy
                                        second_offspring.lifetime = carviz.lifetime
                                        second_offspring.social_attitude = carviz.social_attitude
                                        self.world.PrideMap[i][j].append(second_offspring)
                                    carviz.death = True
                                    print("Dead carviz, two new born")
                                elif carviz.energy <= 0:
                                    if len(self.world.PrideMap[i][j]) <= MAX_PRIDE:
                                        offspring = Carviz(carviz.i, carviz.j)
                                        Carviz.instance_count += 1
                                        offspring.age = 0
                                        offspring.energy = random.randint(1, MAX_ENERGY_C)
                                        offspring.lifetime = carviz.lifetime
                                        offspring.social_attitude = carviz.social_attitude
                                        self.world.PrideMap[i][j].append(first_offspring)

                                    carviz.death = True
                                    print("Dead carviz by end of available energy, one new born")

                if self.world.HerdMap[i][j] != []:
                    for erbast in self.world.HerdMap[i][j]:
                        if isinstance(erbast, Erbast):
                            if erbast.death == False:
                                erbast.i = i
                                erbast.j = j
                                first_offspring = None
                                second_offspring = None
                                if erbast.age >= erbast.lifetime:
                                    if len(self.world.HerdMap[i][j]) <= MAX_HERD and erbast.energy > 0:
                                        first_offspring = Erbast(erbast.i, erbast.j)
                                        Erbast.instance_count += 1
                                        first_offspring.age = 0
                                        first_offspring.energy = random.randint(1, erbast.energy)
                                        first_offspring.lifetime = erbast.lifetime
                                        first_offspring.social_attitude = erbast.social_attitude
                                        self.world.HerdMap[i][j].append(first_offspring)

                                        second_offspring = Erbast(erbast.i, erbast.j)
                                        Erbast.instance_count += 1
                                        second_offspring.age = 0
                                        second_offspring.energy = erbast.energy - first_offspring.energy
                                        second_offspring.lifetime = erbast.lifetime
                                        second_offspring.social_attitude = erbast.social_attitude
                                        self.world.HerdMap[i][j].append(second_offspring)

                                    erbast.death = True
                                    print("Dead erbast, two new born")

                                if erbast.energy <= 0:
                                    if len(self.world.HerdMap[i][j]) <= MAX_HERD and erbast.energy > 0:
                                        first_offspring = Erbast(erbast.i, erbast.j)
                                        Erbast.instance_count += 1
                                        first_offspring.age = 0
                                        first_offspring.energy = random.randint(1, MAX_ENERGY_E)
                                        first_offspring.lifetime = erbast.lifetime
                                        first_offspring.social_attitude = erbast.social_attitude
                                        self.world.HerdMap[i][j].append(first_offspring)

                                        second_offspring = Erbast(erbast.i, erbast.j)
                                        Erbast.instance_count += 1
                                        second_offspring.age = 0
                                        second_offspring.energy = erbast.energy - first_offspring.energy
                                        second_offspring.lifetime = erbast.lifetime
                                        second_offspring.social_attitude = erbast.social_attitude
                                        self.world.HerdMap[i][j].append(second_offspring)

                                    erbast.death = True
                                    print("Dead erbast, two new born")
        return self.world.PrideMap, self.world.HerdMap

    # Climate catastrophe: every 10 days there is drought for which some of the Vegetob lose density
    def drought(self):
        for i in range(NUMCELLS):
            for j in range(NUMCELLS):
                if self.world.terrainMap[i][j] > 1:
                    if self.days > 1:
                        if self.days % 10 == 0:
                            self.world.terrainMap[i][j] -= 5
                        else:
                            self.world.terrainMap[i][j]
                else:
                    self.world.terrainMap[i][j]
        return self.update_terrain(self.world.terrainMap)
    
    # Catastrophe: a meteorite hits the world and causes the death of the species every 10 days
    def meteorite(self):
        if self.days > 1 and self.days % 10 == 0:
            square_size = random.randint(4, 8)  #side of the square
            impact_i = random.randint(0, NUMCELLS - square_size)
            impact_j = random.randint(0, NUMCELLS - square_size)

            for i in range(impact_i, impact_i + square_size):
                for j in range(impact_j, impact_j + square_size):
                    if self.world.terrainMap[i][j] > 1: 
                        self.world.terrainMap[i][j] -= 5
                        if len(self.world.PrideMap[i][j]) >= 1 or len(self.world.HerdMap[i][j]) >= 1:
                            for carviz in self.world.PrideMap[i][j]:
                                if isinstance(carviz, Carviz):
                                    carviz.death = True
                                    print(f'Carviz dead becase of meteorite')
                                
                            for erbast in self.world.HerdMap[i][j]:
                                if isinstance(erbast, Erbast):
                                    erbast.death = True
                                    print(f'Erbast dead becase of meteorite')
                    
            print(f'Meteorite impact at cells form ({impact_i}, {impact_j}) to ({impact_i + square_size - 1}, {impact_j + square_size - 1})')

        return self.world.PrideMap, self.world.HerdMap

    # Increment time counters
    def increment_time(self):
        if self.days > 0:
            if self.days % 10 == 0:
                self.months += 1
                if self.months > 0:
                    if self.months % 10 == 0:
                        self.years += 1
                        if self.years > 0:
                            if self.years % 10 == 0:
                                self.decades += 1
                                if self.decades > 0:
                                    if self.decades % 10 == 0:
                                        self.centuries += 1

    # Update statistics for the simulation
    def update_statistics(self):
        self.numPrides = self.num_Prides()
        self.numHerds = self.num_Herds()
        self.numErbast = Erbast.instance_count
        self.numCarviz = Carviz.instance_count
        self.mediaVegetob = self.mediaOfVegetob()
        self.mediaPride = self.mediaOfEnergy_carviz()
        self.mediaHerds = self.mediaOfEnergy_erbast()

        print(f'Planisuss world - Day {self.days}')
        print(f"The number of Carviz in the simulation is: {self.numCarviz}")
        print(f"The number of Prides in the simulation is: {self.numPrides}")
        print(f"The number of Erbast in the simulation is: {self.numErbast}")
        print(f"The number of Herds in the simulation is: {self.numHerds}")
        print(f"The media of Vegetob in the simulation is: {self.mediaVegetob}")
        print(f"Number of months that have passed {self.months}")
        print(f"Number of years that have passed {self.years}")
        print(f"Number of decades that have passed {self.decades}")
        print(f"Number of centuries that have passed {self.centuries}")

        if self.planisuss_properties:
            self.planisuss_properties.update_plot_popsVsTime(None)
    
    # Save the current state
    def save_state(self):
        state = {
            'terrainMap': np.copy(self.world.terrainMap),
            'PrideMap': copy.deepcopy(self.world.PrideMap),
            'HerdMap': copy.deepcopy(self.world.HerdMap),
            'days': self.days,
            'months': self.months,
            'years': self.years,
            'decades': self.decades,
            'centuries': self.centuries,
            'visualization_terrain': np.copy(self.display.visualization_terrain),
            'visualization_pride': np.copy(self.display.visualization_pride),
            'visualization_herd': np.copy(self.display.visualization_herd)
        }
        self.state_history.append(state)
        return self.state_history.append(state)

    # Load the previous state
    def load_previous_state(self):
        if self.state_history != []:
            state = self.state_history.pop()
            self.world.terrainMap = state['terrainMap']
            self.world.PrideMap = state['PrideMap']
            self.world.HerdMap = state['HerdMap']
            self.days = state['days']
            self.months = state['months']
            self.years = state['years']
            self.decades = state['decades']
            self.centuries = state['centuries']
            self.display.visualization_terrain = state['visualization_terrain']
            self.display.visualization_pride = state['visualization_pride']
            self.display.visualization_herd = state['visualization_herd']

        return self.world.terrainMap, self.world.PrideMap, self.world.HerdMap

    # Update the state of the world
    def update_world_state(self):
        # Movement
        self.update_movementPride()
        self.update_movementHerd()
        # Grazing
        eatenVegetob = self.grazing()
        self.display.img_terrain.set_array(eatenVegetob)
        # Hunt
        self.hunt()
        # Aging
        self.aging()
        # Reproduction
        self.spawning()
        # Growing
        growingVegetob = self.growing_vegetob()
        self.display.img_terrain.set_array(growingVegetob)
        # Drought
        drought = self.drought()
        self.display.img_terrain.set_array(drought)
        # Meteorite
        self.meteorite()

        self.save_state()

    # Update the display with new data
    def update_display(self):
        self.update_scatterHerd()
        self.update_scatterPride()
        self.display.ax.set_title(f'Planisuss world - Day {self.days}')
        self.display.fig.canvas.draw()

    def create_pause_button(self):
        ax_pause = plt.axes([0.7, 0.01, 0.1, 0.05])
        self.button_pause = Button(ax_pause, 'Pause')
        self.button_pause.on_clicked(self.toggle_pause)

    def toggle_pause(self, event):
        self.paused = not self.paused
        if self.paused:
            self.button_pause.label.set_text('Restart')
            print('Animation paused.')
            self.animated.event_source.stop()
            if self.planisuss_properties and self.planisuss_properties.anim:
                self.planisuss_properties.anim.event_source.stop()
                self.planisuss_properties.update_plot_popsVsTime(None)
        else:
            self.button_pause.label.set_text('Pause')
            print('Animation unpaused.')
            self.animated.event_source.start()
            if self.planisuss_properties and self.planisuss_properties.anim:
                self.planisuss_properties.anim.event_source.start()
                self.planisuss_properties.update_plot_popsVsTime(None)
    
    # Create a stop button
    def create_terminate_button(self):
        ax_terminate = plt.axes([0.4, 0.01, 0.1, 0.05])
        self.button_terminate = Button(ax_terminate, 'Terminate')
        self.button_terminate.on_clicked(self.toggle_terminate)

    # Toggle pause state
    def toggle_terminate(self, event):
        self.terminate = not self.terminate
        if self.terminate:
            self.button_terminate.label.set_text('Terminate')
            print('Animation stopped.')
            self.animated.event_source.stop()
            if self.planisuss_properties and self.planisuss_properties.anim:
                self.planisuss_properties.anim.event_source.stop() 
                self.planisuss_properties.update_plot_popsVsTime(None)

    # Create a reset button
    def create_reset_button(self):
        ax_reset = plt.axes([0.8, 0.01, 0.1, 0.05])
        self.button_reset = Button(ax_reset, 'Reset')
        self.button_reset.on_clicked(self.toggle_reset)

    # Toggle restart state
    def toggle_reset(self, event):
        print('Animation restarting...')
        self.animated.event_source.stop()
        self.reset_state()
        # Restart the animation
        self.animated = self.animate()
        self.animated.event_source.start()
        if self.planisuss_properties and self.planisuss_properties.anim:
            self.planisuss_properties.anim.event_source.stop()
            self.planisuss_properties.reset_data()  # Reset the data in PlanisussProperties
            self.planisuss_properties.update_plot_popsVsTime(None)
            self.planisuss_properties.anim = self.planisuss_properties.setup_animation()  # Restart the animation
            self.planisuss_properties.anim.event_source.start()

    # Reset the state of the simulation
    def reset_state(self):
        self.current_frame = -1
        self.days = 0
        self.months = 0
        self.years = 0
        self.decades = 0
        self.centuries = 0
        self.numPrides = 0
        self.numHerds = 0
        self.numErbast = 0
        self.numCarviz = 0
        self.mediaVegetob = 0

        # Reset the world maps to their initial state
        Carviz.instance_count = 0
        Erbast.instance_count = 0

        self.world.terrainMap = np.copy(self.initial_terrainMap)

        # Empty the maps before re-initializing
        self.world.PrideMap = [[] for _ in range(NUMCELLS)]
        for i in range(NUMCELLS):
            self.world.PrideMap[i] = [[] for _ in range(NUMCELLS)]

        self.world.HerdMap = [[] for _ in range(NUMCELLS)]
        for i in range(NUMCELLS):
            self.world.HerdMap[i] = [[] for _ in range(NUMCELLS)]

        # Reinitialize PrideMap with old instances
        for i in range(NUMCELLS):
            for j in range(NUMCELLS):
                if self.initial_PrideMap[i][j]:
                    self.world.PrideMap[i][j] = []
                    for carviz in self.initial_PrideMap[i][j]:
                        new_carviz = Carviz(i, j)
                        new_carviz.energy = carviz.energy
                        new_carviz.lifetime = carviz.lifetime
                        new_carviz.age = carviz.age
                        new_carviz.social_attitude = carviz.social_attitude
                        new_carviz.death = carviz.death
                        new_carviz.movement = carviz.movement
                        self.world.PrideMap[i][j].append(new_carviz)

        # Reinitialize HerdMap with old instances
        for i in range(NUMCELLS):
            for j in range(NUMCELLS):
                if self.initial_HerdMap[i][j]:
                    self.world.HerdMap[i][j] = []
                    for erbast in self.initial_HerdMap[i][j]:
                        new_erbast = Erbast(i, j)
                        new_erbast.energy = erbast.energy
                        new_erbast.lifetime = erbast.lifetime
                        new_erbast.age = erbast.age
                        new_erbast.social_attitude = erbast.social_attitude
                        new_erbast.death = erbast.death
                        new_erbast.movement = erbast.movement
                        self.world.HerdMap[i][j].append(new_erbast)

        initialized_terrain = self.update_terrain(self.world.terrainMap)
        self.display.img_terrain.set_array(initialized_terrain)

        self.update_scatterPride()
        self.update_scatterHerd()

        self.display.fig.canvas.draw()
    
    # Create speed up button
    def create_speedUp_button(self):
        ax_speedup = plt.axes([0.5, 0.01, 0.1, 0.05])
        self.button_speedup = Button(ax_speedup, 'SpeedUp')
        self.button_speedup.on_clicked(self.toggle_speedUp)

    # Function to speed up the animation
    def increase_speed(self):
        self.speed -= 100
        print(f'New speed: {self.speed}')
    
    # Toggle speed up state
    def toggle_speedUp(self, event):
        print(f'Animation speed increased')
        self.increase_speed()
        self.animated.event_source.stop()
        self.animated.event_source.interval = self.speed
        self.animated.event_source.start()
        if self.planisuss_properties:
            self.planisuss_properties.update_plot_popsVsTime(None)

    # Create a slow down button
    def create_slowDown_button(self):
        ax_slowdown = plt.axes([0.6, 0.01, 0.1, 0.05])
        self.button_slowdown = Button(ax_slowdown, 'SlowDown')
        self.button_slowdown.on_clicked(self.toggle_slowDown)

    # Function to slow down
    def decrease_speed(self):
        self.speed += 100
        print(f'New speed: {self.speed}')

    # Toggle slow down state
    def toggle_slowDown(self, event):
        print(f'Animation speed decreased')
        self.decrease_speed()
        self.animated.event_source.stop()
        self.animated.event_source.interval = self.speed
        self.animated.event_source.start()
        if self.planisuss_properties:
            self.planisuss_properties.update_plot_popsVsTime(None)
    
    # Create all buttons
    def create_buttons(self):
        self.create_pause_button()
        self.create_terminate_button()
        self.create_reset_button()
        self.create_speedUp_button()
        self.create_slowDown_button()

    # Cell inspection
    def on_click_properties(self, event):
        if self.paused or self.terminate:
            ix, iy = event.xdata, event.ydata
            print(f"Click detected at coordinates: ({ix}, {iy})")
            if ix is not None and iy is not None:
                cell_x = int(ix)
                cell_y = int(iy)
                if 0 <= cell_x < NUMCELLS and 0 <= cell_y < NUMCELLS:
                    print(f"Valid click within bounds at cell ({cell_x}, {cell_y})")
                    if self.world.terrainMap[cell_y][cell_x] != 0:
                        self.show_cell_properties(cell_x, cell_y)
                        self.click_detected = True
                else:
                    print("Click is out of bounds.")
            else:
                print("Invalid click position.")
        else:
            print("Cannot inspect cell properties while simulation is running.")

    def show_cell_properties(self, x, y):
        terrain_value = self.world.terrainMap[y][x]
        pride_members = self.world.PrideMap[y][x]
        herd_members = self.world.HerdMap[y][x]
        
        info_text = "To get back the plot click r \n"
        info_text += f"Cell ({x}, {y}) properties:\n"
        info_text += f"  Terrain value: {terrain_value}\n"
        info_text += f"  Pride members: {len(pride_members)}\n"
        for member in pride_members:
            info_text += f"    Carviz - Energy: {member.energy}, Age: {member.age}, Social Attitude: {member.social_attitude}\n"
        info_text += f"  Herd members: {len(herd_members)}\n"
        for member in herd_members:
            info_text += f"    Erbast - Energy: {member.energy}, Age: {member.age}, Social Attitude: {member.social_attitude}\n"

        print(f"Cell ({x}, {y}) properties:")
        print(f"  Terrain value: {terrain_value}")
        print(f"  Pride members: {len(pride_members)}")
        for member in pride_members:
            print(f"    Carviz - Energy: {member.energy}, Age: {member.age}, Social Attitude: {member.social_attitude}")
        print(f"  Herd members: {len(herd_members)}")
        for member in herd_members:
            print(f"    Erbast - Energy: {member.energy}, Age: {member.age}, Social Attitude: {member.social_attitude}")

        # Remove the old text box if it exists
        if self.cell_info_box:
            self.cell_info_box.remove()

        # Create a new text box with updated information
        self.cell_info_box = AnchoredText(info_text, loc="lower left", prop=dict(size=10), frameon=True, bbox_to_anchor=(0.1, 0.01),
                                          bbox_transform=self.display.fig.transFigure)
        self.cell_info_box.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
        self.display.ax.add_artist(self.cell_info_box)
        self.display.fig.canvas.draw()

    def on_key_press(self, event):
        if self.click_detected and event.key == 'r':  # 'r' is the key for re-get the plot
            print("Undoing last action")
            # Start the animation
            self.animated.event_source.start()
            if self.planisuss_properties and self.planisuss_properties.anim:
                self.planisuss_properties.anim.event_source.start()
            # Load the previous state    
            self.load_previous_state()
            self.update_display()
            self.display.fig.canvas.draw()
            if self.planisuss_properties:
                self.planisuss_properties.update_plot_popsVsTime(None)
                self.planisuss_properties.fig.canvas.draw()
            # Function to stop the animation again after it starts
            def restop_animation():
                self.animated.event_source.stop()
                if self.planisuss_properties and self.planisuss_properties.anim:
                    self.planisuss_properties.anim.event_source.stop()
            # Use after to schedule the stop after 100 milliseconds
            self.display.fig.canvas.get_tk_widget().after(100, restop_animation)

    # Update the graph
    def update(self, frame):
        if frame != self.current_frame:
            self.current_frame = frame
            # Passing of time
            self.increment_time()
            # Update the count of Herds, Prides, Erbast and Carviz in the simulation
            self.update_statistics()
            # Actions in a day
            self.update_world_state()
            # Update the graphs
            self.update_display()

            self.days += 1
            # End the animation if certain conditions are met
            if frame >= NUMDAYS - 1 or self.numErbast < 0 or self.numCarviz < 0:
                self.animated.event_source.stop()

        return self.display.scatter_pride, self.display.scatter_herd, self.display.img_terrain

    # Animation
    def animate(self):
        self.animated = plt_anim.FuncAnimation(self.display.fig, self.update, frames=NUMDAYS, interval=self.interval, blit=True)
        return self.animated

class PlanisussProperties:
    def __init__(self, DayInPlanisuss):
        self.DayInPlanisuss = DayInPlanisuss
        self.ax_world = self.DayInPlanisuss.display.ax
        self.interval = self.DayInPlanisuss.interval
        self.fig = self.DayInPlanisuss.display.fig
        gs = self.fig.add_gridspec(1, 2, width_ratios=[3, 1])
        self.ax_plot = self.fig.add_subplot(gs[1])
        self.days_data = []                # Initialized number of days
        self.numCarviz_data = []           # Initialized number of Carviz in the map
        self.numErbast_data = []           # Initialized number of Erbast in the map
        self.mediaVegetob_data = []        # Initialized mean of the vegetobs in the map
        self.mean_energy_carviz_data = []  # Initialize mean energy data for Carviz
        self.mean_energy_erbast_data = []  # Initialize mean energy data for Erbast

        self.line_carviz, = self.ax_plot.plot([], [], lw=2, color='red', label='numCarviz')
        self.line_erbast, = self.ax_plot.plot([], [], lw=2, color='purple', label='numErbast')
        self.line_vegetob, = self.ax_plot.plot([], [], lw=2, color='green', label='mediaVegetob')
        self.ax_plot.set_title("Population Vs Time")
        self.ax_plot.legend(loc='lower left')

        self.displaying_mean_energy = False  # Initialize the attribute

        self.anim = self.setup_animation()
        
        # Connect the click event
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def on_click(self, event):
        if event.inaxes == self.ax_plot:
            self.toggle_mean_energy()

    def toggle_mean_energy(self):
        self.displaying_mean_energy = not self.displaying_mean_energy
        if self.displaying_mean_energy:
            self.ax_plot.set_title("Mean Energy Vs Time")
        else:
            self.ax_plot.set_title("Population Vs Time")
        self.update_plot_popsVsTime(None)
        self.fig.canvas.draw()

    def setup_animation(self):
        return plt_anim.FuncAnimation(self.fig, self.update_plot_popsVsTime, frames=NUMDAYS, interval=self.interval, blit=True)

    def update_plot_popsVsTime(self, frame):  
        day = self.DayInPlanisuss.days
        if frame is not None:
            self.days_data.append(day)

            self.numCarviz_data.append(self.DayInPlanisuss.numCarviz)
            self.numErbast_data.append(self.DayInPlanisuss.numErbast)
            self.mediaVegetob_data.append(self.DayInPlanisuss.mediaVegetob)

            self.mean_energy_carviz_data.append(self.DayInPlanisuss.mediaPride)
            self.mean_energy_erbast_data.append(self.DayInPlanisuss.mediaHerds)

        # Keep only the last 20 days
        self.days_data = self.days_data[-20:]
        self.numCarviz_data = self.numCarviz_data[-20:]
        self.numErbast_data = self.numErbast_data[-20:]
        self.mediaVegetob_data = self.mediaVegetob_data[-20:]
        self.mean_energy_carviz_data = self.mean_energy_carviz_data[-20:]
        self.mean_energy_erbast_data = self.mean_energy_erbast_data[-20:]

        if self.displaying_mean_energy:
            self.line_carviz.set_data(self.days_data, self.mean_energy_carviz_data)
            self.line_erbast.set_data(self.days_data, self.mean_energy_erbast_data)
            self.line_vegetob.set_data([], [])
        else:
            self.line_carviz.set_data(self.days_data, self.numCarviz_data)
            self.line_erbast.set_data(self.days_data, self.numErbast_data)
            self.line_vegetob.set_data(self.days_data, self.mediaVegetob_data)

        if len(self.days_data) > 1:
            x_min, x_max = self.days_data[0], self.days_data[-1]
            if x_min == x_max:
                x_min -= 1
                x_max += 1
            self.ax_plot.set_xlim(x_min, x_max)
        else:
            self.ax_plot.set_xlim(0, 1)

        if self.displaying_mean_energy:
            if self.mean_energy_carviz_data and self.mean_energy_erbast_data:
                y_max = max(max(self.mean_energy_carviz_data), max(self.mean_energy_erbast_data), 1) + 10
            else:
                y_max = 10
            self.ax_plot.set_ylim(0, y_max)
        else:
            if self.numCarviz_data and self.numErbast_data and self.mediaVegetob_data:
                y_max = max(max(self.numCarviz_data), max(self.numErbast_data), max(self.mediaVegetob_data)) + 10
            else:
                y_max = 10
            self.ax_plot.set_ylim(0, y_max)

        return self.line_carviz, self.line_erbast, self.line_vegetob

    def reset_data(self):
        self.days_data = []
        self.numCarviz_data = []
        self.numErbast_data = []
        self.mediaVegetob_data = []
        self.mean_energy_carviz_data = []
        self.mean_energy_erbast_data = []

    def show(self):
        plt.show()

#------------------------------------------------------------------------------------------------------------------
# Calling the classes

if __name__ == '__main__':
    world_init = WorldInitialization()
    display = Display(worldInit=world_init)
    day = DayInPlanisuss(worldInit=world_init, display=display, planisuss_properties=None)
    planisuss_properties = PlanisussProperties(day)
    day.planisuss_properties = planisuss_properties  # Link the properties to the day
    planisuss_properties.show()
