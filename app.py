import toml
from flask import Flask
from makerbase import MakerBase

with open('config.toml', 'r', encoding='utf-8') as fp:
    config = toml.load(fp)

app = Flask(__name__)
db = MakerBase(config)


########## Drawers #############
@app.route('/search_drawer/<drawer_name>', method ='GET')
def search_drawer(drawer_name):
    db.search_item(drawer_name)

@app.route('/create_drawer/<drawer_name>/<id>', method ='POST')
def create_drawer(drawer_name, id):
    db.create_drawer(drawer_name, id)

##########  Items  #############
@app.route('/search_item/<item_name>', method ='GET')
def search_item(item_name):
    return db.search_item(item_name)

@app.route('/create_item/<item_name>/<drawer_id>/<user>/<quantity>', method ='POST')
def create_item(item_name, drawer_id, user, quantity):
    db.create_item(item_name, drawer_id, user, quantity)

@app.route('/add_item/<item_id>/<user>/<quantity>', method ='POST')
def add_item(item_id, user, quantity):
    db.add_item(item_id, user, quantity)

@app.route('/remove_item/<item_id>/<user>/<quantity>', method ='POST')
def remove_item(item_id, user, quantity):
    db.remove_item(item_id, user, quantity)

@app.route('/borrow_item/<item_id>/<user>/<quantity>', method ='POST')
def borrow_item(item_id, user, quantity):
    db.borrow_item(item_id, user, quantity)

@app.route('/return_item/<item_id>/<user>/<quantity>', method ='POST')
def return_item(item_id, user, quantity):
    db.return_item(item_id, user, quantity)

if __name__ == '__main__':
   app.run()