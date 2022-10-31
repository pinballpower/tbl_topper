# Bibliotheken laden
from machine import Pin
from neopixel import NeoPixel
from utime import sleep_ms
from math import floor
from random import randrange

COLORMODE_INDEPENDENT = 1
COLORMODE_ALL_ON_THEN_OFF = 2
COLORMODE_SINGLE_BLOCK = 3

# Fade in/out pattern
fade = [ 0,2,4,6,8,10,12,14,16,20,24,28,32,40,48,56,64,72,84,96,110,128,144,160,176,192,224,255 ]

# Number of LEDs
leds = 10

# LEDs are bundles into blocks
led_blocks = [ [0,1,2,3],[4,5],[6,7,8,9]]

# Each block has its own color
block_color = [ [255,0,0],
                [0,255,0],
                [0,0,255] ]
block_state =  [ 0,0,0]
block_turn_on = True;

# color/brightness/and brightess_change for each individual LED
led_color = [[0,0,0]]*leds;
led_brightness = [0]*leds;
led_brightness_step = [0]*leds;

# GPIO pin for WS2812
pin_np = 28

# delay on each update loop
loop_delay = 20

# on/off speed
random_delay = 0
on_off_ratio=2

# color changing mode

# turn on/off blocks completely independent
colormode = COLORMODE_INDEPENDENT

# Turn all blocks on in random order, then off again
#colormode = COLORMODE_ALL_ON_THEN_OFF
keep_all_on_loops = 5
keep_all_off_loops = 2

# Only have a single active block
#colormode = COLORMODE_SINGLE_BLOCK

# Allow only one block to be dimmed in/out at the same time
single_transition = True

# Decide if to cnage a block every n cycles
random_every_n_cycles = 20

# initialize WS2812/NeoPixel
np = NeoPixel(Pin(pin_np, Pin.OUT), leds)

# Functions to tunrn on/off individual LEDs or block.
# These won't directly turn on/off the LED, but set a brightness step that's being used in the main loop
# to dim the LEDs
def turn_off(i):
    if led_brightness_step[i] == 0:
        led_brightness_step[i] = -1
        
    return led_brightness[i] > 0
        
def turn_on(i):
    if led_brightness_step[i] == 0:
        led_brightness_step[i] = 1
        
    return led_brightness[i] == 0

        
def turn_off_block(b):
    res = True
    for i in led_blocks[b]:
        if not(turn_off(i)):
            res = False
    return res
    
def turn_on_block(b):
    res = True
    for i in led_blocks[b]:
        if not(turn_on(i)):
            res = False
    return res

# Initialieze LED colors based on the blocks
for block_index in range(0,len(led_blocks)):
    block = led_blocks[block_index]
    for led_index in block:
        led_color[led_index]=block_color[block_index]
        
    
skip_loops = 0
next_random = 0

# LED update loop
while True:
    
    transition_active = False
    for i in range (leds):
        brightness_index = led_brightness[i]
        brightness = fade[brightness_index]
        brightness_step = led_brightness_step[i];
        if brightness_step != 0:
            transition_active = True
        
        
        brightness_index = brightness_index + brightness_step;
        if brightness_index >= len(fade):
            brightness_index = len(fade)-1
            brightness_step = 0
        
        if brightness_index < 0:
            brightness_index = 0
            brightness_step = 0
            
        led_brightness[i]=brightness_index
        led_brightness_step[i] = brightness_step; 

        np[i] = (floor(led_color[i][0]*brightness/256),
                 floor(led_color[i][1]*brightness/256),
                 floor(led_color[i][2]*brightness/256))
    
    np.write()
    sleep_ms(loop_delay)
    
    if next_random > 0:
        next_random -= 1
        continue
    next_random = random_every_n_cycles
    
    if single_transition and transition_active:
        continue
    
    if (random_delay > 0) and randrange(random_delay) != 0:
        continue
    
    print(block_state)
        
    if colormode == COLORMODE_INDEPENDENT:
        
        # randomly turn on/off blocks
        blockindex = randrange(len(led_blocks))
        print(blockindex)
        if (randrange(2) == 0):
            turn_off_block(blockindex)
            block_state[blockindex]=0
        else:
            turn_on_block(blockindex)
            block_state[blockindex]=1

    if colormode == COLORMODE_ALL_ON_THEN_OFF:
        
        if skip_loops > 0:
            skip_loops -= 1
        else:        
            if block_turn_on:
                if 0 in block_state:
                    ok = False
                    while not(ok):
                        blockindex = randrange(len(led_blocks))
                        ok=turn_on_block(blockindex)
                        block_state[blockindex]=1
                        # Try another block asap as this is already on
                else:
                    block_turn_on=False
                    skip_loops = keep_all_on_loops 
                
            else:
                if 1 in block_state:
                    ok = False
                    while not(ok):
                        blockindex = randrange(len(led_blocks))
                        ok=turn_off_block(blockindex)
                        block_state[blockindex]=0
                else:
                    block_turn_on=True
                    skip_loops = keep_all_off_loops
            
        
    if colormode == COLORMODE_SINGLE_BLOCK:
                
        on_index = randrange(len(led_blocks))
        for block_index in range(0,len(led_blocks)):
            if block_index != on_index:
                turn_off_block(block_index)
            else:
                turn_on_block(on_index)
            

