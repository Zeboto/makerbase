import asyncio
import random

import numpy as np
from rpi_ws281x import Color, PixelStrip


async def clearBoard(strip: PixelStrip, color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()
        
# async define functions which animate LEDs in various ways.
async def colorWipe(strip: PixelStrip, color, wait_ms=50):
    """Wipe color across display a pixel at a await asyncio."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        await asyncio.sleep(wait_ms / 1000.0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)
    
async def rainbow(strip: PixelStrip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        await asyncio.sleep(wait_ms / 1000.0)


async def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(
                (int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        await asyncio.sleep(wait_ms / 1000.0)

drawers = { 
    1: range(1,9), 2: range(9,16), 3: range(16,23), 4: range(23,30),
    5: range(32,39), 6: range(39,46), 7: range(46,54), 8: range(54,62),
    9: range(63,71), 10: range(71,78), 11: range(78,85), 12: range(85,92),
    13: range(98,107), 14: range(107,114), 15: range(114,121), 16: range(121,128),
    17: range(130,137), 18: range(137,145), 19: range(145,153), 20: range(153,160),
    21: range(161,168), 22: range(168,176), 23: range(176,183), 24: range(183,191),
    25: range(200,208), 26: range(208,215), 27: range(215,223), 28: range(223,230),
    29: range(230,238), 30: range(238,245), 31: range(245,253), 32: range(253,261),
    33: range(261,270), 34: range(270,277), 35: range(277,284), 36: range(284,291),
    37: range(300,304), 38: range(304,307), 39: range(307,311), 40: range(311,314),
    41: range(314,318), 42: range(318,321), 43: range(321,325), 44: range(325,329),
    45: range(331,334), 46: range(334,338), 47: range(338,342), 48: range(342,346),
    49: range(346,350), 50: range(350,353), 51: range(353,357), 52: range(357,360),
    53: range(362,365), 54: range(365,369), 55: range(369,373), 56: range(373,376),
    57: range(377,380), 58: range(380,383), 59: range(383,387), 60: range(387,391),
    61: range(401,405), 62: range(405,408), 63: range(408,412), 64: range(412,415),
    65: range(416,419), 66: range(419,423), 67: range(423,426), 68: range(427,430),
    69: range(432,435), 70: range(435,438), 71: range(439,442), 72: range(442,446),
    73: range(446,450), 74: range(450,454), 75: range(454,457), 76: range(457,461),
    77: range(464,467), 78: range(467,470), 79: range(470,474), 80: range(474,477),
    81: range(477,481), 82: range(481,485), 83: range(485,488), 84: range(488,492),
    85: range(498,502), 86: range(502,505), 87: range(505,509), 88: range(509,512),
    89: range(513,516), 90: range(516,519), 91: range(520,523), 92: range(523,527),
    93: range(529,532), 94: range(533,536), 95: range(536,540), 96: range(540,544),
    97: range(544,548), 98: range(548,551), 99: range(551,555), 100: range(555,558),
    101: range(560,563), 102: range(563,567), 103: range(567,571), 104: range(571,574), 
    105: range(574,578), 106: range(578,581), 107: range(581,585), 108: range(585,589),
    109: range(601,605), 110: range(605,609), 111: range(609,612), 112: range(612,616),
    113: range(616,620), 114: range(620,623), 115: range(623,627), 116: range(627,630),
    117: range(632,635), 118: range(635,639), 119: range(639,643), 120: range(643,646),
    121: range(646,650), 122: range(650,654), 123: range(654,658), 124: range(658,661),
    125: range(663,667), 126: range(667,671), 127: range(671,674), 128: range(674,678),
    129: range(678,681), 130: range(681,685), 131: range(685,689), 132: range(689,692),}
rows = np.array([range(691,600,-1), range(498,589), range(491,400, -1), range(300,391),  range(290,199, -1),  range(100,191), range(91,0,-1)   ])

async def loading(strip: PixelStrip, stop=None):
    for d,r in drawers.items():
        color = Color(255,0,255)
        for i in r:
            strip.setPixelColor(i, color)
        strip.show()
        await asyncio.sleep(.1)
        color = Color(0,0,0)
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
        if stop == d:
            break

async def find_drawer(strip: PixelStrip, drawer_id):
    await loading(strip)
    await loading(strip, stop=drawer_id)
    color = Color(0,255,0)
    for j in range(4):
        for i in drawers[drawer_id]:
            strip.setPixelColor(i, color)
        strip.show()
        await asyncio.sleep(.5)
        if j == 3:
            break
        for i in drawers[drawer_id]:
            strip.setPixelColor(i, Color(0,0,0))
        strip.show()
        await asyncio.sleep(.3)
    await asyncio.sleep(3)
    await clearBoard(strip, Color(0, 0, 0))



    