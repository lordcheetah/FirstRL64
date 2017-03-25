#!/usr/bin/env python

import math
import tcod as libtcod
import textwrap
import shelve
import random
import sys

# use graphics?
USE_GRAPHICS = False

# screen size
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

# size of map portion shown on screen
CAMERA_WIDTH = 80
CAMERA_HEIGHT = 43

LIMIT_FPS = 20

# map size
MAP_WIDTH = 100
MAP_HEIGHT = 100

COLORS = {'desaturated_red':(128,64,64),'lightest_red':(255,191,191),'lighter_red':(255,166,166),'light_red':(255,115,115),'red':(255,0,0),'dark_red':(191,0,0),'darker_red':(128,0,0),
          'desaturated_flame':(128,80,64),'lightest_flame':(255,207,191),'lighter_flame':(255,188,166),'light_flame':(255,149,115),'flame':(255,63,0),'dark_flame':(191,47,0),'darker_flame':(128,32,0),'darkest_flame':(64,16,0),
          'desaturated_orange':(128,96,64),'lightest_orange':(255,223,191),'lighter_orange':(255,210,166),'light_orange':(255,185,115),'orange':(255,127,0),'dark_orange':(191,95,0),'darker_orange':(128,64,0),'darkest_orange':(64,32,0),
          'desaturated_amber':(128,112,64),'lightest_amber':(255,239,191),'lighter_amber':(255,233,166),'light_amber':(255,220,115),'amber':(255,191,0),'dark_amber':(191,143,0),'darker_amber':(128,96,0),'darkest_amber':(64,48,0),
          'desaturated_yellow':(128,128,64),'lightest_yellow':(255,255,191),'lighter_yellow':(255,255,166),'light_yellow':(255,255,115),'yellow':(255,255,0),'dark_yellow':(191,191,0),'darker_yellow':(128,128,0),'darkest_yellow':(64,64,0),
          'lime':(191,255,0),
          'chartreuse':(127,255,0),
          'desaturated_green':(64,128,64),'lightest_green':(191,255,191),'lighter_green':(166,255,166),'light_green':(115,255,115),'green':(0,255,0),'dark_green':(0,191,0),'darker_green':(0,128,0),'darkest_green':(0,64,0),
          'sea':(0,255,127),
          'turquoise':(0,255,191),
          'light_cyan':(115,255,255),'cyan':(0,255,255),'dark_cyan':(0,191,191),
          'sky':(0,191,255),
          'azure':(0,127,255),
          'desaturated_blue':(64,64,128),'lightest_blue':(191,191,255),'lighter_blue':(166,166,255),'light_blue':(115,115,255),'blue':(0,0,255),'dark_blue':(0,0,191),'darker_blue':(0,0,128),'darkest_blue':(0,0,64),
          'han':(63,0,255),
          'desaturated_violet':(96,64,128),'lightest_violet':(223,191,255),'lighter_violet':(210,166,255),'light_violet':(185,115,255),'violet':(127,0,255),'dark_violet':(95,0,191),'darker_violet':(64,0,128),'darkest_violet':(32,0,64),
          'purple':(191,0,255),
          'fuchsia':(255,0,255),
          'magenta':(255,0,191),
          'pink':(255,0,127),
          'crimson':(255,0,63),
          'brass':(191,151,96), # metallic colors
          'copper':(196,136,124),
          'gold':(229,191,0),
          'silver':(203,203,203),
          'celadon':(172,255,175), # misc colors
          'peach':(255,159,127),
          'lightest_grey':(223,223,223),'lighter_grey':(191,191,191),'light_grey':(159,159,159),'grey':(127,127,127),'dark_grey':(95,95,95),'darker_grey':(63,63,63),'darkest_grey':(31,31,31),  # grey scale
          'lightest_sepia':(222,211,195),'lighter_sepia':(191,171,143),'light_sepia':(158,134,100),'sepia':(127,101,63),'dark_sepia':(94,75,47),'darker_sepia':(63,50,31),'darkest_sepia':(31,24,15), # sepia
          'black':(0, 0, 0), 'white':(255, 255, 255) # black and white
          }

'''color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)'''

color_dark_wall = (0, 0, 100)
color_light_wall = (130, 110, 50)
color_dark_ground = (50, 50, 150)
color_light_ground = (200, 180, 50)

# params for dungeon gen
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 50

FOV_ALGO = 0  # default Field of Vision algorithim
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

# GUI size and coords
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

# Message bar
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

INVENTORY_WIDTH = 50

HEAL_AMOUNT = 40
LIGHTNING_DAMAGE = 40
LIGHTNING_RANGE = 5
CONFUSE_NUM_TURNS = 10
CONFUSE_RANGE = 8
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 25

PLAYER_DAMAGE_SELF = True

LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150
LEVEL_SCREEN_WIDTH = 40

CHARACTER_SCREEN_WIDTH = 30

DEPTH = 10
MIN_SIZE = 5
FULL_ROOMS = False

BASE_SPEED = 60

wall_tile = 256
floor_tile = 257
player_tile = 258
orc_tile = 259
troll_tile = 260
scroll_tile = 261
healingpotion_tile = 262
sword_tile = 263
shield_tile = 264
stairsdown_tile = 265
dagger_tile = 266

SQUARED_TORCH_RADIUS = TORCH_RADIUS * TORCH_RADIUS
fov_torchx = 0.0
noise = libtcod.noise_new(2)

class Game_Time:
    def __init__(self):
        self.centisec = 0
        self.sec = 0
        self.min = 0
        self.hour = 0
        self.day = 0
        self.year = 0
        self.speed = BASE_SPEED
        self.actspeed = BASE_SPEED/self.speed
        self.name = "game_time"

    def __str__(self):
        return str(self.year).zfill(4) + "." + str(self.day).zfill(3) + " " + str(self.hour).zfill(2) + ":" + str(self.min).zfill(2) + ":" + str(self.sec).zfill(2)

    def update(self):
        self.centisec += 1
        if self.centisec == 10:
            self.sec += 1
        if self.sec == 60:
            self.min += 1
        if self.min == 60:
            self.hour += 1
        if self.hour == 24:
            self.day += 1
        if self.day == 365:
            self.year += 1
        self.centisec = self.centisec % 10
        self.sec = self.sec % 60
        self.min = self.min % 60
        self.hour = self.hour % 24
        self.day = self.day % 365

class Object:
    # this is a generic object: the player, a monster, an item, the stairs...
    # it's always represented by a character on screen
    def __init__(self, x, y, char, name, color, blocks=False, always_visible=False, fighter=None, ai=None, item=None,
                 equipment=None, speed=-1):
        self.name = name
        self.blocks = blocks
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.always_visible = always_visible
        self.speed = speed
        self.actspeed = BASE_SPEED/(self.speed)
        if self.speed > -1:
            initiative = libtcod.random_get_int(0,0,9)
            schedule.scheduleEvent(self, self.actspeed + initiative)

        self.fighter = fighter
        if self.fighter:  # let fighter know who owns it
            self.fighter.owner = self

        self.ai = ai
        if self.ai:  # let ai know who owns it
            self.ai.owner = self

        self.item = item
        if self.item:  # let the item know who owns it
            self.item.owner = self

        self.equipment = equipment
        if self.equipment:  # let Equipment component know who owns it
            self.equipment.owner = self

            # there must be an Item component for Equipment to work
            self.item = Item()
            self.item.owner = self

    def do_turn(self):
        if self.ai != None:
            self.ai.take_turn()
        if self.speed > -1:
            schedule.scheduleEvent(self, self.actspeed)

    def move(self, dx, dy):
        if not is_blocked(self.x + dx, self.y + dy):
            # move by given amount
            self.x += dx
            self.y += dy

    def move_towards(self, target_x, target_y):
        # vector from this object to the target and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # normalize it to length 1 (preserving direction), then round it and
        # convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def move_astar(self, target):
        # create fov map
        fov = libtcod.map_new(map_width, map_height)

        # scan map for blocked walls
        for y1 in range(map_height):
            for x1 in range(map_width):
                libtcod.map_set_properties(fov, x1, y1, not map[x1][y1].block_sight, not map[x1][y1].blocked)

                # scan for blocked objs that aren't self or target
        for obj in objects:
            if obj.blocks and obj != self and obj != target:
                # set tile as a wall so it can be navigated around
                libtcod.map_set_properties(fov, obj.x, obj.y, True, False)

        # allocate A* path
        # 1.41 is cost of normal diagonal cost of moving. set to 0.0 to prohibit diagonals
        my_path = libtcod.path_new_using_map(fov)

        # compute path between self's coords and target's coords
        libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        # check if path exists, if so check if less than 25 tiles. short paths keep ai from wandering around too much
        if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
            # find next coords in computed path
            x, y = libtcod.path_walk(my_path, True)
            if x or y:
                # set self's coords to next path tile
                self.x = x
                self.y = y
            else:
                # keep old move function as back if no paths
                self.move_towards(target.x, target.y)

            # delete path to free mem
            libtcod.path_delete(my_path)
        else:
            self.move_towards(target.x, target.y)

    def move_dijkstra(self, target):
        fov = libtcod.map_new(map_width, map_height)

        for y1 in range(map_height):
            for x1 in range(map_width):
                libtcod.map_set_properties(fov, x1, y1, not map[x1][y1].block_sight, not map[x1][y1].blocked)

        for obj in objects:
            if obj.blocks and obj != self and obj != target:
                libtcod.map_set_properties(fov, obj.x, obj.y, True, False)

        path_dijk = libtcod.dijkstra_new(fov)

        path_dijk_dist = 0.0

        # compute dijkstra grid (distance from px,py)
        libtcod.dijkstra_compute(path_dijk, self.x, self.y)
        # get the maximum distance (needed for rendering)
        for y in range(map_height):
            for x in range(map_width):
                d = libtcod.dijkstra_get_distance(path_dijk, x, y)
                if d > path_dijk_dist:
                    path_dijk_dist = d
        # compute path from px,py to dx,dy
        libtcod.dijkstra_path_set(path_dijk, target.x, target.y)

        if not libtcod.dijkstra_is_empty(path_dijk) and libtcod.dijkstra_size(path_dijk) < 50:
            x, y = libtcod.dijkstra_path_walk(path_dijk)
            if x or y:
                self.x = x
                self.y = y

        libtcod.dijkstra_delete(path_dijk)

    def move_dijkstramap(self, target):
        x, y = map_dijk_player.dirTowardsGoal(self.x, self.y)
        if x or y:
            self.x += x
            self.y += y

    def draw(self):
        # set the color and then draw the character that represents this object at its position
        if (libtcod.map_is_in_fov(fov_map, self.x, self.y) or
                (self.always_visible and map[self.x][self.y].explored)):
            (x, y) = to_camera_coordinates(self.x, self.y)

            if x is not None:
                libtcod.console_set_default_foreground(con, self.color)
                libtcod.console_put_char(con, x, y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        # erase the character that represents this object
        (x, y) = to_camera_coordinates(self.x, self.y)
        if x is not None:
            libtcod.console_put_char(con, x, y, ' ', libtcod.BKGND_NONE)

    def distance_to(self, other):
        # return the distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        # return dist to coords
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def send_to_back(self):
        # make this object drawn first so all others appear above it if they're in the same tile
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def take_turn(self):
        pass


class Fighter:
    # combat related properties and methods
    def __init__(self, hp, defense, power, xp, death_function=None):
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.xp = xp
        self.death_function = death_function

    def __str__(self):
        return self.id

    def take_damage(self, damage):
        # apply damage if possible
        if damage > 0:
            self.hp -= damage
            # check for death, call death func if app
            if self.hp <= 0:
                schedule.cancelEvent(self.owner)
                function = self.death_function
                if function is not None:
                    function(self.owner)
                if self.owner != player:  # give player xp
                    player.fighter.xp += self.xp

    def attack(self, target):
        # a simple formula for attack damage
        damage = self.power - target.fighter.defense

        if damage > 0:
            # make the target take damage
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
            target.fighter.take_damage(damage)
        else:
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')

    def heal(self, amount):
        # heal by amount w/o going over max
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    @property
    def power(self):
        bonus = sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
        return self.base_power + bonus

    @property
    def defense(self):  # return def by summing bonuses
        bonus = sum(equipment.defense_bonus for equipment in get_all_equipped(self.owner))
        return self.base_defense + bonus

    @property
    def max_hp(self):  # return max_hp by summing bonuses
        bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
        return self.base_max_hp + bonus


class BasicMonster:
    # AI for basic monster
    def __init__(self):
        self.player_seen = False

    def take_turn(self):
        # a basic monster takes turn. if pc can see it, it can see pc
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y) or self.player_seen == True:
            self.player_seen = True

            # move towards pc if far
            if monster.distance_to(player) >= 2:
                # monster.move_towards(player.x, player.y)
                monster.move_dijkstramap(player)

            # attack if pc is alive
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)


class ConfusedMonster:
    # AI for confused monster
    def __init__(self, old_ai, num_turns=CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns

    def take_turn(self):
        if self.num_turns > 0:  # still confused
            # move in rand dir
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1
        else:  # restore prev ai (this one will be deleted)
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' is no longer confused!', COLORS['red'])


class Item:
    # an item that can be picked up an used
    def __init__(self, use_function=None):
        self.use_function = use_function

    def pick_up(self):
        # add to player's inventory and remove from map
        if len(inventory) >= 26:
            message('Your inventory is full, cannot pick up ' + self.owner.name + '.', COLORS['red'])
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', COLORS['green'])

            # special case: auto equip if equipment slot isn't used
            equipment = self.owner.equipment
            if equipment and get_equipped_in_slot(equipment.slot) is None:
                equipment.equip()

    def drop(self):
        # special case: if obj has Equipment coponent, dequip it
        if self.owner.equipment:
            self.owner.equipment.dequip()

        # add to map and remove from inventory, drop on pc coords
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('You dropped a ' + self.owner.name + '.', COLORS['yellow'])

    def use(self):
        # special case: if object has Equipment component, use action is to equip/dequip
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return

        # call use_function if it is defined
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                inventory.remove(self.owner)  # destroy after use, unless cancelled


class Tile:
    # a tile of the map and its properties
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked

        # by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

        # all tiles start unexplored
        self.explored = False


class Rect:
    # a rectangle on the map. used to make a room
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return (center_x, center_y)

    def intersect(self, other):
        # returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class Equipment:
    # object that can be equipped for bonuses. auto adds item component
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        self.slot = slot
        self.is_equipped = False

        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus

    def toggle_equip(self):  # toggle equip status
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()

    def equip(self):
        # if slot already used, dequip what's there
        old_equipment = get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()

        # equip obj and show msg
        self.is_equipped = True
        message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', COLORS['light_green'])

    def dequip(self):
        # dequip obj and show msg
        if not self.is_equipped: return
        self.is_equipped = False
        message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', COLORS['light_yellow'])

class PriorityQueue:
    def __init__(self):
        self.__queue = []

    def __len__(self):
        return len(self.__queue)

    def enqueue(self, value, priority = 0.0):
        """
            Append a new element to the queue
            according to its priority.
        """

        tuple = [priority, value]

        # Insert the tuple in sorted position in the queue.  If a
        # tuple with equal priority is encountered, the new tuple is
        # inserted after it.

        finalPos = 0
        high = len(self)
        while finalPos < high:
            middle = (finalPos + high) // 2
            if tuple[0] < self.__queue[middle][0]:
                high = middle
            else:
                finalPos = middle + 1

        self.__queue.insert(finalPos, tuple)

    def adjustPriorities(self, add):
        """
            Increases all priorities.
        """

        for v in self.__queue:
            v[0] += add

    def dequeue(self):
        """
            Pop the value with the lowest priority.
        """

        return self.__queue.pop(0)[1]

    def dequeueWithKey(self):
        """
            Pop the (priority, value) tuple with the lowest priority.
        """

        return self.__queue.pop(0)

    def erase(self, value):
        """
            Removes an element from the queue by value.
        """

        self.__erase(value, lambda a, b: a == b)

    def erase_ref(self, value):
        """
            Removes an element from the queue by reference.
        """

        self.__erase(value, lambda a, b: a is b)

    def __erase(self, value, test):
        """
            All tupples t are removed from the queue
            if test(t[1], value) evaluates to True.
        """

        i = 0
        while i < len(self.__queue):
            if test(self.__queue[i][1], value):
                del self.__queue[i]
            else:
                i += 1

class TimeSchedule(object):
    """
        Represents a series of events that occur over time.
    """

    def __init__(self):
        self.__scheduledEvents = PriorityQueue()

    def scheduleEvent(self, event, delay = 0.0):
        """
            Schedules an event to occur after a certain delay.
        """

        if event is not None:
            self.__scheduledEvents.enqueue(event, delay)

    def nextEvent(self):
        """
            Dequeues and returns the next event to occur.
        """

        time, event = self.__scheduledEvents.dequeueWithKey()
        self.__scheduledEvents.adjustPriorities(-time)

        return event

    def cancelEvent(self, event):
        """
            Cancels a pending event.
        """

        self.__scheduledEvents.erase_ref(event)


def handle_keys():
    global key

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  # exit game

    if game_state == 'playing':
        # movement keys
        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
            player_move_or_attack(0, -1)

        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
            player_move_or_attack(0, 1)

        elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
            player_move_or_attack(-1, 0)

        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
            player_move_or_attack(1, 0)

        elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
            player_move_or_attack(-1, -1)

        elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
            player_move_or_attack(1, -1)

        elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
            player_move_or_attack(-1, 1)

        elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
            player_move_or_attack(1, 1)

        elif key.vk == libtcod.KEY_KP5:
            pass  # do nothing, wait for monster to come to you

        else:
            # test for other keys
            key_char = chr(key.c)

            if key_char == 'g':
                # pick up item
                for object in objects:  # look for an item in pc's tile
                    if object.x == player.x and object.y == player.y and object.item:
                        object.item.pick_up()
                        break

            if key_char == 'i':
                # show inventory; uf uten selected, use it
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()

            if key_char == 'd':
                # show inventory; if item selected drop it
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()

            if key_char == ',':
                # go down stairs, if pc is on them
                if stairs.x == player.x and stairs.y == player.y:
                    next_level()

            if key_char == 'c':
                # show char info
                level_up_xp = LEVEL_UP_BASE + int(player.level * LEVEL_UP_FACTOR)
                msgbox(
                    'Character Information\n\nLevel: ' + str(player.level) + '\nExperience: ' + str(player.fighter.xp) +
                    '\nExperience to level up: ' + str(level_up_xp) + '\n\nMaximum HP: ' + str(player.fighter.max_hp) +
                    '\nAttack: ' + str(player.fighter.power) + '\nDefense: ' + str(player.fighter.defense),
                    CHARACTER_SCREEN_WIDTH)

            return 'didnt-take-turn'


def make_map():
    global map, objects, stairs, map_height, map_width

    # list of objects with just pc
    objects = [player]

    map_width = from_dungeon_level([[80, 1],[90,4],[100,8]])
    map_height = from_dungeon_level([[43, 1],[60,6],[100,10]])

    # fill map with "unblocked" tiles
    map = [[Tile(True)
            for y in range(map_height)]
           for x in range(map_width)]

    rooms = []
    num_rooms = 0

    for r in range(MAX_ROOMS):
        # random width and height
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        # random position without going out of bounds
        x = libtcod.random_get_int(0, 0, map_width - w - 2)
        y = libtcod.random_get_int(0, 0, map_height - h - 2)

        new_room = Rect(x, y, w, h)

        # see if new room overlaps old ones
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            # no intersections, this room is valid

            # paint room to map
            create_room(new_room)

            # center coords of new room
            (new_x, new_y) = new_room.center()

            if num_rooms == 0:
                # start player in first room
                player.x = new_x
                player.y = new_y
            else:
                # remaining rooms
                # connect it to the previous room with a tunnel

                # center coords of prev room
                (prev_x, prev_y) = rooms[num_rooms - 1].center()

                # 50/50 horiz or vert tunnel
                if libtcod.random_get_int(0, 0, 1) == 1:
                    # first move horiz then vert
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    # first move v, then h
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

            # add contents to this room
            place_objects(new_room)

            # append new room
            rooms.append(new_room)
            num_rooms += 1

    # create stairs at center of last room
    if USE_GRAPHICS:
        stairs = Object(new_x, new_y, stairsdown_tile, 'stairs', COLORS['white'], always_visible=True)
    else:
        stairs = Object(new_x, new_y, '<', 'stairs', COLORS['white'], always_visible=True)
    objects.append(stairs)
    stairs.send_to_back()  # so it's drawn below monsters


def make_bsp():
    global map, objects, stairs, bsp_rooms

    objects = [player]

    map = [[Tile(True) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

    # Empty global list for storing room coordinates
    bsp_rooms = []

    # New root node
    bsp = libtcod.bsp_new_with_size(0, 0, MAP_WIDTH, MAP_HEIGHT)

    # Split into nodes
    libtcod.bsp_split_recursive(bsp, 0, DEPTH, MIN_SIZE + 1, MIN_SIZE + 1, 1.5, 1.5)

    # Traverse the nodes and create rooms
    libtcod.bsp_traverse_inverted_level_order(bsp, traverse_node)

    # Random room for the stairs
    stairs_location = random.choice(bsp_rooms)
    bsp_rooms.remove(stairs_location)
    stairs = Object(stairs_location[0], stairs_location[1], '<', 'stairs', COLORS['white'], always_visible=True)
    objects.append(stairs)
    stairs.send_to_back()

    # Random room for player start
    player_room = random.choice(bsp_rooms)
    bsp_rooms.remove(player_room)
    player.x = player_room[0]
    player.y = player_room[1]

    # Add monsters and items
    for room in bsp_rooms:
        new_room = Rect(room[0], room[1], 2, 2)
        place_objects(new_room)

    initialize_fov()


def traverse_node(node, dat):
    global map, bsp_rooms

    # Create rooms
    if libtcod.bsp_is_leaf(node):
        minx = node.x + 1
        maxx = node.x + node.w - 1
        miny = node.y + 1
        maxy = node.y + node.h - 1

        if maxx == MAP_WIDTH - 1:
            maxx -= 1
        if maxy == MAP_HEIGHT - 1:
            maxy -= 1

        # If it's False the rooms sizes are random, else the rooms are filled to the node's size
        if FULL_ROOMS == False:
            minx = libtcod.random_get_int(None, minx, maxx - MIN_SIZE + 1)
            miny = libtcod.random_get_int(None, miny, maxy - MIN_SIZE + 1)
            maxx = libtcod.random_get_int(None, minx + MIN_SIZE - 2, maxx)
            maxy = libtcod.random_get_int(None, miny + MIN_SIZE - 2, maxy)

        node.x = minx
        node.y = miny
        node.w = maxx - minx + 1
        node.h = maxy - miny + 1

        # Dig room
        for x in range(minx, maxx + 1):
            for y in range(miny, maxy + 1):
                map[x][y].blocked = False
                map[x][y].block_sight = False

        # Add center coordinates to the list of rooms
        bsp_rooms.append(((minx + maxx) / 2, (miny + maxy) / 2))

    # Create corridors
    else:
        left = libtcod.bsp_left(node)
        right = libtcod.bsp_right(node)
        node.x = min(left.x, right.x)
        node.y = min(left.y, right.y)
        node.w = max(left.x + left.w, right.x + right.w) - node.x
        node.h = max(left.y + left.h, right.y + right.h) - node.y
        if node.horizontal:
            if left.x + left.w - 1 < right.x or right.x + right.w - 1 < left.x:
                x1 = libtcod.random_get_int(None, left.x, left.x + left.w - 1)
                x2 = libtcod.random_get_int(None, right.x, right.x + right.w - 1)
                y = libtcod.random_get_int(None, left.y + left.h, right.y)
                vline_up(map, x1, y - 1)
                hline(map, x1, y, x2)
                vline_down(map, x2, y + 1)

            else:
                minx = max(left.x, right.x)
                maxx = min(left.x + left.w - 1, right.x + right.w - 1)
                x = libtcod.random_get_int(None, minx, maxx)
                vline_down(map, x, right.y)
                vline_up(map, x, right.y - 1)

        else:
            if left.y + left.h - 1 < right.y or right.y + right.h - 1 < left.y:
                y1 = libtcod.random_get_int(None, left.y, left.y + left.h - 1)
                y2 = libtcod.random_get_int(None, right.y, right.y + right.h - 1)
                x = libtcod.random_get_int(None, left.x + left.w, right.x)
                hline_left(map, x - 1, y1)
                vline(map, x, y1, y2)
                hline_right(map, x + 1, y2)
            else:
                miny = max(left.y, right.y)
                maxy = min(left.y + left.h - 1, right.y + right.h - 1)
                y = libtcod.random_get_int(None, miny, maxy)
                hline_left(map, right.x - 1, y)
                hline_right(map, right.x, y)

    return True


def vline(map, x, y1, y2):
    if y1 > y2:
        y1, y2 = y2, y1

    for y in range(y1, y2 + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False


def vline_up(map, x, y):
    while y >= 0 and map[x][y].blocked == True:
        map[x][y].blocked = False
        map[x][y].block_sight = False
        y -= 1


def vline_down(map, x, y):
    while y < MAP_HEIGHT and map[x][y].blocked == True:
        map[x][y].blocked = False
        map[x][y].block_sight = False
        y += 1


def hline(map, x1, y, x2):
    if x1 > x2:
        x1, x2 = x2, x1
    for x in range(x1, x2 + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False


def hline_left(map, x, y):
    while x >= 0 and map[x][y].blocked == True:
        map[x][y].blocked = False
        map[x][y].block_sight = False
        x -= 1


def hline_right(map, x, y):
    while x < MAP_WIDTH and map[x][y].blocked == True:
        map[x][y].blocked = False
        map[x][y].block_sight = False
        x += 1

def render_all():
    global fov_map, fov_recompute, fov_torchx
    global color_dark_wall, color_light_wall
    global color_light_ground, color_light_ground
    global game_time, player_turn
    global map_dijk_player

    move_camera(player.x, player.y)

    fov_dx = 0.0
    fov_dy = 0.0
    fov_di = 0.0
    if fov_recompute:
        # recompute FOV if needed
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)
        map_dijk_player = DijkstraMap(player.x, player.y, map_width, map_height, dijkCalbak)
        map_dijk_player.compute()
        libtcod.console_clear(con)

        # slightly change the perlin noise parameter
        fov_torchx += 0.2
        # randomize the light position between -1.5 and 1.5
        tdx = [fov_torchx + 20.0]
        fov_dx = libtcod.noise_get(noise, tdx, libtcod.NOISE_SIMPLEX) * 1.5
        tdx[0] += 30.0
        fov_dy = libtcod.noise_get(noise, tdx, libtcod.NOISE_SIMPLEX) * 1.5
        fov_di = 0.2 * libtcod.noise_get(noise, [fov_torchx], libtcod.NOISE_SIMPLEX)

        # go through all tiles and set their background color
        for y in range(CAMERA_HEIGHT):
            for x in range(CAMERA_WIDTH):
                (map_x, map_y) = (camera_x + x, camera_y + y)
                visible = libtcod.map_is_in_fov(fov_map, map_x, map_y)
                wall = map[map_x][map_y].block_sight
                if not visible:
                    # out of pc fov
                    if map[map_x][map_y].explored:
                        if wall and USE_GRAPHICS:
                            libtcod.console_put_char_ex(con, x, y, wall_tile, COLORS['darkest_orange'], COLORS['black'])
                        elif wall and not USE_GRAPHICS:
                            libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
                        elif USE_GRAPHICS:
                            libtcod.console_put_char_ex(con, x, y, floor_tile, COLORS['darkest_orange'], COLORS['black'])
                        else:
                            libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
                else:
                    # mark it explored since it's visible
                    map[map_x][map_y].explored = True
                    if USE_GRAPHICS:
                        base = COLORS['darkest_orange']
                        light = COLORS['light_orange']
                        if wall:
                            tile = wall_tile
                        else:
                            tile = floor_tile
                    else:
                        if wall:
                            base = color_dark_wall
                            light = color_light_wall
                        else:
                            base = color_dark_ground
                            light = color_light_ground
                        # cell distance to torch (squared)
                    r = float(x - player.x + fov_dx) * (x - player.x + fov_dx) + \
                        (y - player.y + fov_dy) * (y - player.y + fov_dy)
                    if r < SQUARED_TORCH_RADIUS:
                        l = (SQUARED_TORCH_RADIUS - r) / SQUARED_TORCH_RADIUS \
                            + fov_di
                        if l < 0.0:
                            l = 0.0
                        elif l > 1.0:
                            l = 1.0
                        base = libtcod.color_lerp(base, light, l)
                    if USE_GRAPHICS:
                        libtcod.console_put_char_ex(con, x, y, tile, base, COLORS['black'])
                    else:
                        libtcod.console_set_char_background(con, x, y, base,
                                                        libtcod.BKGND_SET)

                    # visible
                    """if wall and USE_GRAPHICS:
                        libtcod.console_put_char_ex(con, x, y, wall_tile, COLORS['white'], COLORS['black'])
                    elif wall and not USE_GRAPHICS:
                        libtcod.console_set_char_background(con, x, y, color_light_wall, libtcod.BKGND_SET)
                    elif USE_GRAPHICS:
                        libtcod.console_put_char_ex(con, x, y, floor_tile, COLORS['white'], COLORS['black'])
                    else:
                        libtcod.console_set_char_background(con, x, y, color_light_ground, libtcod.BKGND_SET)"""

    # draw nonpc objects in the list
    for object in objects:
        if object != player:
            object.draw()
    # draw pc last
    player.draw()

    # swap buffer "con" with screen
    libtcod.console_blit(con, 0, 0, map_width, map_height, 0, 0, 0)

    # prepare to render GUI
    libtcod.console_set_default_background(panel, COLORS['black'])
    libtcod.console_clear(panel)

    if player_turn:
        libtcod.console_set_default_foreground(panel, COLORS['orange'])
        libtcod.console_print_ex(panel, 1, 5, libtcod.BKGND_NONE, libtcod.LEFT, "Player Turn")

    libtcod.console_set_default_foreground(panel, COLORS['light_blue'])
    libtcod.console_print_ex(panel, 1, 6, libtcod.BKGND_NONE, libtcod.LEFT, str(game_time))

    # print game msgs
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1

    # show pc's stats
    render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
               COLORS['light_red'], COLORS['darker_red'])
    libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(dungeon_level))

    # display names of objects under mouse
    libtcod.console_set_default_foreground(panel, COLORS['grey'])
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())

    # blit panel to screen
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)


def create_room(room):
    global map
    # go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False


def create_h_tunnel(x1, x2, y):
    global map
    # horizontal tunnel
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False


def create_v_tunnel(y1, y2, x):
    global map
    # vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False


def place_objects(room):
    global schedule
    # max num of monsters/room
    max_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]])

    # chance of each monster
    monster_chances = {}
    monster_chances['Klingon'] = 80  # Klingons always show up, even if other monsters have 0 chance
    monster_chances['Romulan'] = from_dungeon_level([[15, 3], [30, 5], [60, 7]])

    # max items/room
    max_items = from_dungeon_level([[1, 1], [2, 4]])

    # chance of each item
    item_chances = {}
    item_chances['biogel'] = 35  # biogel always shows up
    item_chances['tesla coil'] = from_dungeon_level([[25, 4]])
    item_chances['plasma ball'] = from_dungeon_level([[25, 6]])
    item_chances['confusion hack'] = from_dungeon_level([[10, 2]])
    item_chances['lightsaber'] = from_dungeon_level([[5, 4]])
    item_chances['shield'] = from_dungeon_level([[15, 8]])

    # rand num of monsters
    num_monsters = libtcod.random_get_int(0, 0, max_monsters)

    for i in range(num_monsters):
        # rand pos for monster
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        # only place if tile not blocked
        if not is_blocked(x, y):
            choice = random_choice(monster_chances)
            if choice == 'Klingon':
                # create a Klingon
                fighter_component = Fighter(hp=20, defense=0, power=4, xp=35, death_function=monster_death)
                ai_component = BasicMonster()

                if USE_GRAPHICS:
                    monster = Object(x, y, orc_tile, 'Klingon', COLORS['dark_flame'], blocks=True,
                                     fighter=fighter_component, ai=ai_component, speed=9)
                else:
                    monster = Object(x, y, 'K', 'Klingon', COLORS['dark_flame'], blocks=True,
                                 fighter=fighter_component, ai=ai_component, speed=9)

            elif choice == 'Romulan':
                # create a Romulan
                fighter_component = Fighter(hp=30, defense=2, power=8, xp=100, death_function=monster_death)
                ai_component = BasicMonster()

                if USE_GRAPHICS:
                    monster = Object(x, y, troll_tile, 'Romulan', COLORS['darker_red'], blocks=True, fighter=fighter_component,
                                     ai=ai_component, speed=12)
                else:
                    monster = Object(x, y, 'R', 'Romulan', COLORS['darker_red'], blocks=True, fighter=fighter_component,
                                 ai=ai_component, speed=12)

            objects.append(monster)

    # rand num of items
    num_items = libtcod.random_get_int(0, 0, max_items)

    for i in range(num_items):
        # rand pos for item
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        # check for block
        if not is_blocked(x, y):
            choice = random_choice(item_chances)
            if choice == 'biogel':
                # create biogel
                item_component = Item(use_function=cast_heal)
                if USE_GRAPHICS:
                    item = Object(x, y, healingpotion_tile, 'biogel', COLORS['violet'], item=item_component)
                else:
                    item = Object(x, y, '!', 'biogel', COLORS['violet'], item=item_component)
            elif choice == 'tesla coil':
                # create telsa coil
                item_component = Item(use_function=cast_lightning)
                if USE_GRAPHICS:
                    item = Object(x, y, scroll_tile, 'tesla coil', COLORS['light_yellow'], item=item_component)
                else:
                    item = Object(x, y, '#', 'tesla coil', COLORS['light_yellow'], item=item_component)
            elif choice == 'plasma ball':
                # create plasma ball
                item_component = Item(use_function=cast_fireball)
                if USE_GRAPHICS:
                    item = Object(x, y, scroll_tile, 'plasma ball', COLORS['light_yellow'], item=item_component)
                else:
                    item = Object(x, y, '#', 'plasma ball', COLORS['light_yellow'], item=item_component)
            elif choice == 'confusion hack':
                # create confuse hack
                item_component = Item(use_function=cast_confuse)
                if USE_GRAPHICS:
                    item = Object(x, y, scroll_tile, 'confusion hack', COLORS['light_yellow'], item=item_component)
                else:
                    item = Object(x, y, '#', 'confusion hack', COLORS['light_yellow'], item=item_component)
            elif choice == 'lightsaber':
                # create lightsaber
                equipment_component = Equipment(slot='right hand', power_bonus=3)
                if USE_GRAPHICS:
                    item = Object(x, y, sword_tile, 'lightsaber', COLORS['sky'], equipment=equipment_component)
                else:
                    item = Object(x, y, '/', 'lightsaber', COLORS['sky'], equipment=equipment_component)
            elif choice == 'shield':
                # create shield
                equipment_component = Equipment(slot='left hand', defense_bonus=1)
                if USE_GRAPHICS:
                    item = Object(x, y, shield_tile, 'shield', COLORS['darker_orange'], equipment_component)
                else:
                    item = Object(x, y, '[', 'shield', COLORS['darker_orange'], equipment_component)

            objects.append(item)
            item.send_to_back()  # items appear below other objects
            item.always_visible = True


def is_blocked(x, y):
    # test the map tile
    if map[x][y].blocked:
        return True

    # check for blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False


def player_move_or_attack(dx, dy):
    global fov_recompute

    # coords pc is moving to/attacking
    x = player.x + dx
    y = player.y + dy

    # attempt to find attackable obj
    target = None
    for object in objects:
        if object.fighter and object.x == x and object.y == y:
            target = object
            break

    if target is not None:
        player.fighter.attack(target)
    else:
        player.move(dx, dy)
        fov_recompute = True


def player_death(player):
    # game over
    global game_state
    message('You died!', COLORS['red'])
    game_state = 'dead'

    # pc now corpse
    player.char = '%'
    player.color = COLORS['dark_red']


def monster_death(monster):
    # monster now corpse, no longer block
    # attacked and doesn't move
    message(monster.name.capitalize() + ' is dead! You gain ' + str(monster.fighter.xp) + ' experience points.',
            COLORS['orange'])
    monster.char = '%'
    monster.color = COLORS['dark_red']
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name

    monster.send_to_back()


def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    # render progress bar
    # width of bar
    bar_width = int(float(value) / maximum * total_width)

    # render background
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    # render bar
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    # centered text with values
    libtcod.console_set_default_foreground(panel, COLORS['white'])
    libtcod.console_print_ex(panel, x + int(total_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER,
                             name + ': ' + str(value) + '/' + str(maximum))


def message(new_msg, color=COLORS['white']):
    # split message if necessary
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        # if buffer is full, remove first line
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        # add new line
        game_msgs.append((line, color))


def get_names_under_mouse():
    global mouse

    # return string with names of obj under mouse
    (x, y) = (mouse.cx, mouse.cy)
    (x, y) = (camera_x + x, camera_y + y)  # from screen to map coords

    # create list with names of obj at mouse coords in FOV
    names = [obj.name for obj in objects
             if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]

    names = ', '.join(names)  # join names with commas
    return names.capitalize()


def menu(header, options, width):
    global key, mouse

    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    # calc total height for header (after autowrap) and one line per optio
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height

    # create offscreen console that represents menu window
    window = libtcod.console_new(width, height)

    # print header with autowrap
    libtcod.console_set_default_foreground(window, COLORS['white'])
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    # print all options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ')' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    # blit contents of window to console
    x = int(SCREEN_WIDTH / 2) - int(width / 2)
    y = int(SCREEN_HEIGHT / 2) - int(height / 2)
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    # compute x and y offsets to convert console pos to men pos
    x_offset = x  # x is the left edge of menu
    y_offset = y + header_height  # subtract height of header from top edge of menu

    while True:
        # present root console to player and check for input
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if (mouse.lbutton_pressed):
            (menu_x, menu_y) = (mouse.cx - x_offset, mouse.cy - y_offset)
            # check if click is within menu and on choice
            if menu_x >= 0 and menu_x < width and menu_y >= 0 and menu_y < height - header_height:
                return menu_y

        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            return None  # cancel if player right-clicked or pressed esc

        if key.vk == libtcod.KEY_ENTER and key.lalt:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        # convert ASCII to index, return it if valid
        index = key.c - ord('a')
        if index >= 0 and index < len(options): return index
        #  if pc pressed a letter that's not an option, return none
        if index >= 0 and index <= 26: return None


def inventory_menu(header):
    # show menu with each item in inventory
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in inventory:
            text = item.name
            # show additional info, if it's equiped
            if item.equipment and item.equipment.is_equipped:
                text = text + ' (on ' + item.equipment.slot + ')'
            options.append(text)

    index = menu(header, options, INVENTORY_WIDTH)
    # if item was chosen, return it
    if index is None or len(inventory) == 0: return None
    return inventory[index].item


def cast_heal():
    # heal pc
    if player.fighter.hp == player.fighter.max_hp:
        message('You are already at full health.', COLORS['red'])
        return 'cancelled'

    message('Your wounds start to feel better!', COLORS['light_violet'])
    player.fighter.heal(HEAL_AMOUNT)


def cast_lightning():
    # damage nearest enemy
    monster = closest_monster(LIGHTNING_RANGE)
    if monster is None:  # no enemy within range
        message('No ememy is close enough to strike.', COLORS['red'])
        return 'cancelled'

    # zap it!
    message('A lightning bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
            + str(LIGHTNING_DAMAGE) + ' hit points.', COLORS['light_cyan'])
    monster.fighter.take_damage(LIGHTNING_DAMAGE)


def closest_monster(max_range):
    # find nearest enemy in range and FOV
    closest_enemy = None
    closest_dist = max_range + 1  # start with slightly more than max range

    for object in objects:
        if object.fighter and not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y):
            # calc dist between object and player
            dist = player.distance_to(object)
            if dist < closest_dist:  # it's closer so remember it
                closest_enemy = object
                closest_dist = dist
            return closest_enemy


def cast_confuse():
    # ask pc for target to confuse
    message('Left-click an enemy to confuse it, or right-click to cancel.', COLORS['light_cyan'])
    monster = target_monster(CONFUSE_RANGE)
    if monster is None: return 'cancelled'

    # replace monster's ai with confused one; after turns it will restore old ai
    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster  # tell the new component who owns it
    message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', COLORS['light_green'])


def target_tile(max_range=None):
    # return pos of tile left clicked in pc's fov (optionally in range) or none if right clicked
    global key, mouse
    while True:
        # render screen. this erases inventory and shows names of objects under mouse
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        render_all()

        (x, y) = (mouse.cx, mouse.cy)
        (x, y) = (camera_x + x, camera_y + y)  # from screen to map coords

        if (mouse.lbutton_pressed and libtcod.map_is_in_fov(fov_map, x, y, ) and
                (max_range is None or player.distance(x, y) <= max_range)):
            return (x, y)

        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            return (None, None)  # cancel if pc right clicked or pressed esc


def target_monster(max_range=None):
    # return a clicked monster inside fov up to range or none if right clicked
    while True:
        (x, y) = target_tile(max_range)
        if x is None:  # cancelled
            return None

        # return first clicked monster, otherwise loop
        for obj in objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != player:
                return obj


def cast_fireball():
    # ask pc for target tile to fireball
    message('Left-click a target tile for the plasma-ball, or right-click to cancel.', COLORS['light_cyan'])
    (x, y) = target_tile()
    if x is None: return 'cancelled'
    message('The fireball explodes, burning everything within ' + str(FIREBALL_RADIUS) + ' tiles!', COLORS['orange'])

    for obj in objects:  # damage every fighter in range, including pc
        if (obj.distance(x, y) <= FIREBALL_RADIUS) and obj.fighter and (PLAYER_DAMAGE_SELF or obj != player):
            message('The ' + obj.name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points.', COLORS['orange'])
            obj.fighter.take_damage(FIREBALL_DAMAGE)

def init_schedule():
    global game_time, schedule

    game_time = Game_Time()
    schedule = TimeSchedule()

    schedule.scheduleEvent(game_time, game_time.actspeed)


def new_game():
    global player, inventory, game_msgs, game_state, dungeon_level

    init_schedule()

    # create pc
    fighter_component = Fighter(hp=100, defense=1, power=2, xp=0, death_function=player_death)
    if USE_GRAPHICS:
        player = Object(0, 0, player_tile, 'player', COLORS['white'], blocks=True, fighter=fighter_component, speed=10)
    else:
        player = Object(0, 0, '@', 'player', COLORS['white'], blocks=True, fighter=fighter_component, speed=10)

    player.level = 1
    dungeon_level = 1

    make_map()
    #make_bsp()

    initialize_fov()

    game_state = 'playing'
    inventory = []

    # create list of game msgs and colors
    game_msgs = []

    # initial equipment
    equipment_component = Equipment(slot='right hand', power_bonus=2)
    if USE_GRAPHICS:
        obj = Object(0, 0, dagger_tile, 'dagger', COLORS['sky'], equipment=equipment_component)
    else:
        obj = Object(0, 0, '-', 'dagger', COLORS['sky'], equipment=equipment_component)
    inventory.append(obj)
    equipment_component.equip()
    obj.always_visible = True

    # welcome message
    message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Alien Kings.', COLORS['red'])


def initialize_fov():
    global fov_recompute, fov_map, fov_torchx
    fov_recompute = True

    libtcod.console_clear(con)  # unexplored areas start black (default back color)

    # create fov map, using generated map
    fov_map = libtcod.map_new(map_width, map_height)
    for y in range(map_height):
        for x in range(map_width):
            libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)
    # 1d noise for the torch flickering
    fov_noise = libtcod.noise_new(1, 1.0, 1.0)
    fov_torchx = 0.0


def play_game():
    global key, mouse, camera_x, camera_y, schedule, game_time, player_turn, player, fov_recompute

    player_action = None
    player_turn = False

    load_customfont()

    (camera_x, camera_y) = (0, 0)

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        render_all()

        # flush to screen
        libtcod.console_flush()

        if check_level_up():
            continue

        # clear all objects from their old locations before they move
        for object in objects:
            object.clear()

        if (player_turn) or game_state == 'dead':
            # handle keys and if app exit game
            player_action = handle_keys()
            if player_action == 'exit':
                save_game()
                break
            if player_action != 'didnt-take-turn':
                player_turn = False
            fov_recompute = True

        if game_state == 'playing' and player_action != 'didnt-take-turn':

            event = schedule.nextEvent()
            while True:
                if event.name == "player":
                    event.do_turn()
                    player_turn = True
                    break
                elif event.name == "game_time":
                    game_time.update()
                    schedule.scheduleEvent(game_time, game_time.actspeed)
                    fov_recompute = True
                    break
                else:
                    event.do_turn()
                    event = schedule.nextEvent()



def main_menu():
    img = libtcod.image_load('menu_background1.png')

    while not libtcod.console_is_window_closed():
        # show background image
        libtcod.image_blit_2x(img, 0, 0, 0)

        # show game title and credits
        libtcod.console_set_default_foreground(0, COLORS['light_yellow'])
        libtcod.console_print_ex(0, int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 2) - 4, libtcod.BKGND_NONE, libtcod.CENTER,
                                 'TOMBS OF THE ANCIENT ALIEN KINGS')
        libtcod.console_print_ex(0, int(SCREEN_WIDTH / 2), SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.CENTER, 'By James')

        # show options and wait for pc choice
        choice = menu('', ['New Game', 'Continue', 'Quit'], 24)

        if choice == 0:  # new game
            new_game()
            play_game()
        if choice == 1:  # load last game
            try:
                load_game()
            except:
                msgbox('\n No saved game to load.\n', 24)
                continue
            play_game()
        elif choice == 2:  # quit
            break


def save_game():
    # open a new empty shelve (possibly overwriting an old one) to write the game data
    with shelve.open('savegame', 'n', ) as file:
        file['map'] = map
        file['objects'] = objects
        file['player_index'] = objects.index(player)  # index of player in objects list
        file['stairs_index'] = objects.index(stairs)  # same for the stairs
        file['inventory'] = inventory
        file['game_msgs'] = game_msgs
        file['game_state'] = game_state
        file['dungeon_level'] = dungeon_level
        file['game_time'] = game_time


def load_game():
    global map, objects, player, inventory, game_msgs, game_state, dungeon_level, stairs, schedule, game_time

    schedule = TimeSchedule()

    with shelve.open('savegame', 'r') as file:
        map = file['map']
        objects = file['objects']
        player = objects[file['player_index']]  # get index of player in objects list and access it
        stairs = objects[file['stairs_index']]  # same for the stairs
        inventory = file['inventory']
        game_msgs = file['game_msgs']
        game_state = file['game_state']
        dungeon_level = file['dungeon_level']
        game_time = file['game_time']

    schedule.scheduleEvent(game_time, game_time.actspeed)

    for obj in objects:
        if obj.speed > -1:
            initiative = libtcod.random_get_int(0, 0, 9)
            schedule.scheduleEvent(obj, obj.actspeed + initiative)

    initialize_fov()


def msgbox(text, width=50):
    menu(text, [], width)  # use menu() as a sort of message box


def next_level():
    # advance to next level
    global dungeon_level, fov_torchx, schedule

    init_schedule()

    schedule.scheduleEvent(player, player.actspeed)

    message('You take a moment to rest, and recover your strength.', COLORS['light_violet'])
    player.fighter.heal(int(player.fighter.max_hp / 2))  # heal the player by 50%

    fov_torchx = 0.0

    dungeon_level += 1
    message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', COLORS['red'])
    make_map()  # create new level
    #make_bsp()
    initialize_fov()


def check_level_up():
    # see if pc xp is enough to lvlup
    level_up_xp = LEVEL_UP_BASE + int(player.level * LEVEL_UP_FACTOR)
    if player.fighter.xp >= level_up_xp:
        # lvlup
        player.level += 1
        player.fighter.xp -= level_up_xp
        message('Your battle skills grow stronger! You reached level ' + str(player.level) + '!', COLORS['yellow'])

        choice = None
        while choice == None:  # keep asking until a choice is made
            choice = menu('Level up! Choose a stat to raise:\n',
                          ['Constitution (+20 HP, from ' + str(player.fighter.base_max_hp) + ')',
                           'Strength (+1 attack, from ' + str(player.fighter.base_power) + ')',
                           'Agility (+1 defense, from ' + str(player.fighter.base_defense) + ')'], LEVEL_SCREEN_WIDTH)

            if choice == 0:
                player.fighter.base_max_hp += 20
                player.fighter.hp += 20
            elif choice == 1:
                player.fighter.base_power += 1
            elif choice == 2:
                player.fighter.base_defense += 1
        return True

    return False


def random_choice_index(chances):  # choose option from list, returning it's index
    # dice will land on some number between 1 and sum of chances
    dice = libtcod.random_get_int(0, 1, sum(chances))

    # go through all chances, keeping sum
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        # see if dice landed in part that corresponds to choice
        if dice <= running_sum:
            return choice
        choice += 1


def random_choice(chances_dict):
    # choose option from dictionary, return key
    chances = chances_dict.values()
    strings = list(chances_dict)

    return strings[random_choice_index(chances)]


def from_dungeon_level(table):
    # returns value depending on level. table shows what occurs at each level, default 0
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0


def get_equipped_in_slot(slot):  # returns equipment in slot or None if empty
    for obj in inventory:
        if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
            return obj.equipment
    return None


def get_all_equipped(obj):  # returns a list of equipped items
    if obj == player:
        equipped_list = []
        for item in inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list
    else:
        return []  # other obj have no equipment


def move_camera(target_x, target_y):
    global camera_x, camera_y, fov_recompute

    # new camera coords (top left corner of screen rel to map
    x = target_x - int(CAMERA_WIDTH / 2)  # coords so target is at center of screen
    y = target_y - int(CAMERA_HEIGHT / 2)

    # keep camera inside map
    if x < 0: x = 0
    if y < 0: y = 0
    if x > map_width - CAMERA_WIDTH - 1: x = map_width - CAMERA_WIDTH - 1
    if y > map_height - CAMERA_HEIGHT - 1: y = map_height - CAMERA_HEIGHT - 1

    if x != camera_x or y != camera_y: fov_recompute = True

    (camera_x, camera_y) = (x, y)


def to_camera_coordinates(x, y):
    # convert coords on map to coords on screen
    (x, y) = (x - camera_x, y - camera_y)

    if (x < 0 or y < 0 or x >= CAMERA_WIDTH or y >= CAMERA_HEIGHT):
        return (None, None)  # if it's outside the view, return nothing

    return (x, y)


def load_customfont():
    # index of first custom tile in file
    a = 256

    # "y" is row index. load 6th row in file. increate to load new rows
    for y in range(5,6):
        libtcod.console_map_ascii_codes_to_font(a, 32, 0, y)
        a += 32

DIRS = [(0, -1),
        (1, -1),
        (1, 0),
        (1, 1),
        (0, 1),
        (-1, 1),
        (-1, 0),
        (-1, -1)]


class Dimensions:
    def __init__(self, w, h):
        self.w = w
        self.h = h


class DijkstraMap:
    ''' Constructor.
    goalX x-position of cell that map will 'roll down' to
    goalY y-position of cell that map will 'roll down' to
    mapWidth width of the map
    mapHeight height of the map
    passableCallback a function with two parameters (x, y) that returns true if a map cell is passable'''

    def __init__(self, goalX, goalY, mapWidth, mapHeight, passableCallback):
        self._map = []
        self._goals = []
        self._goals.append((goalX, goalY))

        self._dimensions = Dimensions(mapWidth, mapHeight)

        self._dirs = []
        self._dirs = DIRS

        self._passableCallback = passableCallback

    ''' Establish values for all cells in map.
        call after DijkstraMap(goalX, goalY, mapWidth, mapHeight, passableCallback)'''

    def compute(self):
        if len(self._goals) < 1:
            return
        elif len(self._goals) == 1:
            return self._singlegoalcompute(self._goals[0][0], self._goals[0][1])
        else:
            return self._manygoalcompute()

    def _manygoalcompute(self):
        stillupdating = []
        for i in self._dimensions.w:
            self._map[i] = []
            stillupdating[i] = []
            for j in self._dimensions.h:
                stillupdating[i][j] = True
                self._map[i][j] = sys.maxsize

        for v in self._goals:
            self._map[v.x][v.y] = 0

        passes = 0
        while True:
            nochange = True
            for i in stillupdating:
                for j in stillupdating[i]:
                    if self._passableCallback(i, j):
                        cellChanged = False
                        low = sys.maxsize
                        for v in self._dirs:
                            tx = (i + v[0])
                            ty = (j + v[1])
                            if 0 < tx <= self._dimensions.w and 0 < ty <= self._dimensions.h:
                                val = self._map[tx][ty]
                                if val and val < low:
                                    low = val

                        if self._map[i][j] > low + 2:
                            self._map[i][j] = low + 1
                            cellChanged = True
                            nochange = False

                        if not cellChanged and self._map[i][j] < 1000:
                            stillupdating[i][j] = None
                    else:
                        stillupdating[i][j] = None

            passes += 1

    def _singlegoalcompute(self, gx, gy):
        self._map = [[sys.maxsize for j in range(self._dimensions.h)] for i in range(self._dimensions.w)]

        self._map[gx][gy] = 0

        val = 1
        wq = []
        pq = []
        ds = self._dirs

        wq.insert(0, (gx, gy))

        while True:
            while len(wq) > 0:
                t = wq.pop()
                for d in ds:
                    x = t[0] + d[0]
                    y = t[1] + d[1]
                    if 0 <= x < self._dimensions.w and 0 <= y < self._dimensions.h:
                        if self._passableCallback(x, y) and self._map[x][y] > val:
                            self._map[x][y] = val
                            pq.insert(0, (x, y))

            if len(pq) < 1:
                break
            val += 1
            while len(pq) > 0:
                wq.insert(0, pq.pop())

    ''' Add new goal position.
        Inserts a new cell to be used as a goal.
        gx the new x-value of the goal cell
        gy the new y-value of the goal cell'''

    def addGoal(self, gx, gy):
        self._goals.insert(0, (gx, gy))

    ''' Remove all goals.
        Will delete all goal cells. You must insert another goal before computing.
        You can specify one goal to be inserted after the goal remove takes place.
        The method only checks that the coordinates are provided before setting the new goal cell.
        gx Will use this value as the x-coordinate of a new goal cell to be inserted
        gy Will use this value as the y-coordinate of a new goal cell to be inserted'''

    def removeGoals(self, gx, gy):
        self._goals.clear()
        if gx and gy: self._goals.insert(0, (gx, gy))

    ''' Output map values to console.
        For debugging, will send a comma separated output of cell values to the console.
        returnString Will return the output in addition to sending it to console if true.'''

    def writeMapToConsole(self, returnString):
        ls = ''

        if returnString: ls = ''
        for y in self._dimensions.h:
            s = ''
            for x in self._dimensions.w:
                s = s + self._map[x][y] + ','

            print(s)
            if returnString: ls = ls + s + '\n'

        if returnString: return ls

    ''' Get Width of map.
        return w width of map'''

    def getWidth(self):
        return self._dimensions.w

    ''' Get Height of map.
        return h height of map'''

    def getHeight(self):
        return self._dimensions.h

    ''' Get Dimensions as table.
        dimensions A table of width and height values
        dimensions.w width of map
        dimensions.h height of map'''

    def getDimensions(self):
        return self._dimensions

    ''' Get the map table.
        map A 2d array of map values, access like map[x][y]'''

    def getMap(self):
        return self._map

    ''' Get the x-value of the goal cell.
        :return x x-value of goal cell'''

    def getGoalX(self):
        return self._goals[0].x

    ''' Get the y-value of the goal cell.
        :return y y-value of goal cell'''

    def getGoalY(self):
        return self._goals[0].y

    ''' Get the goal cell as a table.
        goal table containing goal position
        goal.x x-value of goal cell'''

    def getGoal(self):
        return self._goals[0]

    ''' Get the direction of the goal from a given position
        x x-value of current position
        y y-value of current position
        xDir X-Direction towards goal. Either -1, 0, or 1
        yDir Y-Direction towards goal. Either -1, 0, or 1'''

    def dirTowardsGoal(self, x, y):
        low = self._map[x][y]
        if low == 0:
            return 0, 0
        dir = 0, 0
        for v in self._dirs:
            tx = (x + v[0])
            ty = (y + v[1])
            if 0 < tx <= self._dimensions.w and 0 < ty <= self._dimensions.h:
                val = self._map[tx][ty]
                if val < low:
                    low = val
                    dir = v

        if dir:
            return dir[0], dir[1]
        return None

    ''' Run a callback function on every cell in the map
        callback A function with x and y parameters that will be run on every cell in the map'''

    def iterateThroughMap(self, callback):
        for y in self._dimensions.h:
            for x in self._dimensions.w:
                callback(x, y)


def dijkCalbak(x, y):
    global objects

    blocked = False

    for obj in objects:
        if obj.blocks and obj.x == x and obj.y == y:
            blocked = True

    return (not map[x][y].blocked and not blocked)


#############################
# Init and main loop
#############################

if USE_GRAPHICS:
    libtcod.console_set_custom_font('TiledFont.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD, 32, 10)
else:
    # set font
    #libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    #libtcod.console_set_custom_font('terminal16x16_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
    libtcod.console_set_custom_font('terminal10x16_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
# set screen
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial')
libtcod.sys_set_fps(LIMIT_FPS)
# screen buffer
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

mouse = libtcod.Mouse()
key = libtcod.Key()

main_menu()
