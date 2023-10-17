import asyncio
import datetime
import json
import random
from threading import Thread

from bson import json_util
from bson.objectid import ObjectId
from pymongo import MongoClient
from rpi_ws281x import Color, PixelStrip

from ledutils import colorWipe, find_drawer, rainbow, rainbowCycle

#  LED strip configuration:
LED_COUNT = 700       # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
# True to invert the signal (when using NPN transistor level shift)
LED_INVERT = False
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
# Create NeoPixel object with appropriate configuration.
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
                   LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()


def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def parse_json(data):
    return json.loads(json_util.dumps(data))

class MakerBase:

    def __init__(self, config):
        # Create a connection using MongoClient
        client = MongoClient(config['database']['url'])

        self.db = client['makerbase']
        self.loop = asyncio.new_event_loop()

        t = Thread(target=start_background_loop,
                   args=(self.loop,), daemon=True)
        t.start()

        self.task = self.loop.create_task(self.idle_animation())

    async def replace_task(self, new_task):
        self.task.cancel()
        await self.task
        self.task = self.loop.create_task(new_task)
        print('created task')

    async def idle_animation(self):
        try:
            animations = [
                colorWipe(strip, Color(255, 20, 0), 10),
                colorWipe(strip, Color(0, 255, 255)),
                colorWipe(strip, Color(0, 0, 255)),
                rainbow(strip),
                rainbowCycle(strip)
            ]
            while True:
                random.shuffle(animations)
                for a in animations:
                    await a
        except asyncio.CancelledError:
            print('cancelled idle')
        finally:
            print('clearing idle task')

    def start_idle(self):
        self.loop.create_task(self.replace_task(self.idle_animation()))

    async def search_animation(self, drawer_id):
        try:
            await find_drawer(strip, drawer_id)
            self.task = self.loop.create_task(self.idle_animation())
        except asyncio.CancelledError:
            print('cancelled search')
        finally:
            print('clearing search task')

    def start_search(self, drawer_id):
        self.loop.create_task(self.replace_task(
            self.search_animation(drawer_id)))

    def search_drawer(self, drawer_name):
        results = [x for x in self.db['items'].find(
            {"category": {'$regex': drawer_name}})]
        return parse_json(results)

    def create_drawer(self, drawer_name, id):
        return self.db["drawers"].insert_one(
            {
                "drawer_id": id,
                "category": drawer_name,
                "created": datetime.datetime.now(),
            }
        )

    def search_item(self, item_name):
        results = [x for x in self.db['items'].find(
            {"item_name": {'$regex': item_name}})]
        return parse_json(results)

    def create_item(self, item_name, drawer_id, user_id, quantity):
        r = self.db["items"].insert_one(
            {
                "drawer_id": drawer_id,
                "item_name": item_name,
                "history": [
                    {
                        "action": "add",
                        "quantity": int(quantity),
                        "user_id": user_id,
                        "datetime": datetime.datetime.now(),
                    }
                ],

            }
        )
        self.calculate_fields(r.inserted_id)
        return r

    def add_item(self, item_id, user_id, quantity):
        self.db["items"].update_one(
            {'_id': ObjectId(item_id)},
            {'$push': {
                'history': {
                    "action": "add",
                    "quantity": int(quantity),
                    "user_id": user_id,
                    "datetime": datetime.datetime.now(),
                }
            }
            }
        )
        self.calculate_fields(item_id)

    def remove_item(self, item_id, user_id, quantity):
        self.db["items"].update_one(
            {'_id': ObjectId(item_id)},
            {'$push': {
                'history': {
                    "action": "remove",
                    "quantity": int(quantity),
                    "user_id": user_id,
                    "datetime": datetime.datetime.now(),
                }
            }
            }
        )
        self.calculate_fields(item_id)

    def borrow_item(self, item_id, user_id, quantity):
        self.db["items"].update_one(
            {'_id': ObjectId(item_id)},
            {'$push': {
                'history': {
                    "action": "borrow",
                    "quantity": int(quantity),
                    "user_id": user_id,
                    "datetime": datetime.datetime.now(),
                }
            }
            }
        )
        self.calculate_fields(item_id)

    def return_item(self, item_id, user_id, quantity):
        self.db["items"].update_one(
            {'_id': ObjectId(item_id)},
            {'$push': {
                'history': {
                    "action": "return",
                    "quantity": int(quantity),
                    "user_id": user_id,
                    "datetime": datetime.datetime.now(),
                }
            }
            }
        )
        self.calculate_fields(item_id)

    def calculate_fields(self, item_id):
        result = self.db['items'].update_one({'_id': ObjectId(item_id)}, [
            {
                '$set': {
                    'current_quantity': {
                        '$sum': {
                            '$map': {
                                'input': '$history',
                                'as': 'hh',
                                'in': {
                                    '$cond': [
                                        {
                                            '$or': [
                                                {
                                                    '$eq': [
                                                        '$$hh.action', 'add'
                                                    ]
                                                }, {
                                                    '$eq': [
                                                        '$$hh.action', 'return'
                                                    ]
                                                }
                                            ]
                                        },
                                        '$$hh.quantity',
                                        {
                                            '$subtract': [
                                                0, '$$hh.quantity'
                                            ]
                                        }
                                    ]
                                }
                            }
                        }
                    },
                    'total_quantity': {
                        '$sum': {
                            '$map': {
                                'input': '$history',
                                'as': 'hh',
                                'in': {
                                    '$cond': [
                                        {
                                            '$eq': [
                                                '$$hh.action', 'add'
                                            ]
                                        }, '$$hh.quantity', {
                                            '$cond': [
                                                {
                                                    '$eq': [
                                                        '$$hh.action', 'remove'
                                                    ]
                                                }, {
                                                    '$subtract': [
                                                        0, '$$hh.quantity'
                                                    ]
                                                }, 0
                                            ]
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            }
        ])
        return result
