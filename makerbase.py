from pymongo import MongoClient
import datetime


class MakerBase:

    def __init__(self,config):
        # Create a connection using MongoClient
        client = MongoClient(config['database']['url'])

        self.db = client['makerbase']

    def search_drawer(self, drawer_name):
        results = [x for x in self.db['items'].find(
            {"category": {'$regex': drawer_name}})]
        return results

    def create_drawer(self, drawer_name, id):
        self.db["drawers"].insert_one(
            {
                "drawer_id": id,
                "category": drawer_name,
                "created": datetime.datetime.now(),
            }
        )

    def locate_drawer(drawer_id):
        raise NotImplementedError

    def search_item(self, item_name):
        results = [x for x in self.db['items'].find(
            {"item_name": {'$regex': item_name}})]
        return results

    def create_item(self, item_name, drawer_id, user_id, quantity):
        self.db["items"].insert_one(
            {
                "drawer_id": drawer_id,
                "item_name": item_name,
                "history": [
                    {
                        "action": "add",
                        "quantity": quantity,
                        "user_id": user_id,
                        "datetime": datetime.datetime.now(),
                    }
                ],

            }
        )
        self.calculate_fields()

    def add_item(self, item_id, user_id, quantity):
        self.db["items"].update_one(
            { '_id': item_id },
            { '$push': { 
                'history': {
                        "action": "add",
                        "quantity": quantity,
                        "user_id": user_id,
                        "datetime": datetime.datetime.now(),
                    }
                }
            }
        )
        self.calculate_fields()

    def remove_item(self, item_id, user_id, quantity):
        self.db["items"].update_one(
            { '_id': item_id },
            { '$push': { 
                'history': {
                        "action": "remove",
                        "quantity": quantity,
                        "user_id": user_id,
                        "datetime": datetime.datetime.now(),
                    }
                }
            }
        )
        self.calculate_fields()
    
    def borrow_item(self, item_id, user_id, quantity):
        self.db["items"].update_one(
            { '_id': item_id },
            { '$push': { 
                'history': {
                        "action": "borrow",
                        "quantity": quantity,
                        "user_id": user_id,
                        "datetime": datetime.datetime.now(),
                    }
                }
            }
        )
        self.calculate_fields()
    
    def return_item(self, item_id, user_id, quantity):
        self.db["items"].update_one(
            { '_id': item_id },
            { '$push': { 
                'history': {
                        "action": "return",
                        "quantity": quantity,
                        "user_id": user_id,
                        "datetime": datetime.datetime.now(),
                    }
                }
            }
        )
        self.calculate_fields()

    def calculate_fields(self):
        result = self.db['items'].aggregate([
            {
                '$addFields': {
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
                                        }, '$$hh.quantity', {
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
