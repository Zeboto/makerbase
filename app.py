import toml
from flask import Flask
from makerbase import MakerBase

with open('config.toml', 'r', encoding='utf-8') as fp:
    config = toml.load(fp)

app = Flask(__name__)
db = MakerBase(config)


########## Drawers #############
@app.route('/search_drawer/<drawer_name>', methods=['GET'])
def search_drawer(drawer_name):
    return db.search_item(drawer_name)

@app.route('/highlight_drawer/<drawer_id>', methods=['GET'])
def highlight_drawer(drawer_id):
    db.start_search(int(drawer_id))
    return {
        "message":"Success", 
        }, 200


@app.route('/create_drawer/<drawer_name>/<id>', methods=['POST'])
def create_drawer(drawer_name, id):
    result = db.create_drawer(drawer_name, id)
    return {
        "message":"Success", 
        "data":{
            "id":str(result.inserted_id)
            }
        }, 200

##########  Items  #############
@app.route('/search_item/<item_name>', methods=['GET'])
def search_item(item_name):
    return db.search_item(item_name)

@app.route('/create_item/<item_name>/<drawer_id>/<user>/<quantity>', methods=['POST'])
def create_item(item_name, drawer_id, user, quantity):
    result = db.create_item(item_name, drawer_id, user, quantity)
    return {
        "message":"Success", 
        "data":{
            "id":str(result.inserted_id)
            }
        }, 200

@app.route('/add_item/<item_id>/<user>/<quantity>', methods=['POST'])
def add_item(item_id, user, quantity):
    db.add_item(item_id, user, quantity)
    return {
        "message":"Success"
        }, 200

@app.route('/remove_item/<item_id>/<user>/<quantity>', methods=['POST'])
def remove_item(item_id, user, quantity):
    db.remove_item(item_id, user, quantity)
    return {
        "message":"Success"
        }, 200

@app.route('/borrow_item/<item_id>/<user>/<quantity>', methods=['POST'])
def borrow_item(item_id, user, quantity):
    db.borrow_item(item_id, user, quantity)
    return {
        "message":"Success"
        }, 200

@app.route('/return_item/<item_id>/<user>/<quantity>', methods=['POST'])
def return_item(item_id, user, quantity):
    db.return_item(item_id, user, quantity)
    return {
        "message":"Success"
        }, 200

if __name__ == '__main__':
   app.run()