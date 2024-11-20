from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, Order, Item, OrderItem
import uuid
from datetime import datetime
from functools import wraps
from dotenv import load_dotenv
import os


app = Flask(__name__)

# Will see later
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the Database
db.init_app(app)

with app.app_context():
    db.create_all()

# Load variables from .env file
load_dotenv('config.env')

# get credentials from the environment
USERNAME = os.getenv('NAME')
PASSWORD = os.getenv('PASSWORD')

# create a item
@app.post('/item')
def create_item():
    try:
        data = request.get_json()
        if 'name' not in data or 'price' not in data:
            return jsonify({'ERROR': 'Missing parameters'}), 400

        name = data.get('name')
        description = data.get('description')
        price = data.get('price')

        item = Item(name=name, description=description, price=price)

        db.session.add(item)
        db.session.commit()
        return jsonify({'message': 'Item created!', 'item_id': item.item_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'ERROR': e}), 500


# get all items
@app.get('/items')
def get_items():
    items = Item.query.all()
    items_list = []
    for item in items:
        items_list.append({
            "id": item.item_id,
            "name": item.name,
            "description": item.description,
            "price": item.price
        })

    return jsonify(items_list), 200


# create a order
@app.post('/order')
def create_order():
    data = request.get_json()
    try:
        if 'customer_id' not in data or 'items' not in data:
            return jsonify({'ERROR': 'Missing parameters'}), 400
        order_id = str(uuid.uuid4())
        customer_id = data.get('customer_id')
        timestamp = datetime.now()
        items = data.get('items')
        total = 0.0

        order_items = []
        for item in items:
            if 'id' not in item or 'qty' not in item:
                return jsonify({'ERROR': 'Missing parameters'}), 400
            
            item_id = item.get('id')
            quantity = item.get('qty')

            item_data = Item.query.filter_by(item_id=item_id).first()
            if not item_data:
                return jsonify({'ERROR': 'Item with id: {item_id} not found'}), 404
            
            order_item = OrderItem(
                order_id=order_id, 
                item_id=item_id,
                quantity=quantity
            )
            order_items.append(order_item)
            total += item_data.price * quantity

        order = Order(
            order_id=order_id, 
            customer_id=customer_id, 
            timestamp=timestamp, 
            total_amount = total
        )
        db.session.add(order)
        db.session.bulk_save_objects(order_items)

        db.session.commit()

        return jsonify({'message': 'Order created!!', 'order_id': order_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'ERROR': e}), 500


# get an order
@app.get('/order/<order_id>')
def get_order(order_id):
    try:
        order = Order.query.filter_by(order_id=order_id).first()
       
        if not order:
            return jsonify({'ERROR': 'Order not found'}), 404
        
        order_items = OrderItem.query.filter_by(order_id=order_id).all()
        items = []
        for cur_item in order_items:
            item_id = cur_item.item_id
            quantity = cur_item.quantity

            item = Item.query.get(item_id)
            items.append({
                'name': item.name,
                'description': item.description,
                'price': item.price,
                'quantity': quantity
            })

        return jsonify({
            'order_id': order.order_id,
            'customer_id': order.customer_id,
            'timestamp': order.timestamp,
            'status': order.status,
            'items': items,
            'amount': order.total_amount
        }), 200
    except Exception as e:
        return jsonify({'ERROR': e}), 500


# Basic Authentication middleware
def authenticate_user(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != USERNAME or auth.password != PASSWORD:
            return jsonify({'ERROR': 'Authentication error'}), 404
        return f(*args, **kwargs)
    return wrapper


# fetch order status
@app.get('/order/status/<order_id>')
def get_order_status(order_id):
    try:
        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            return jsonify({'ERROR': 'Order not found'}), 404
        
        return jsonify({
            'status': order.status,
            'order_id': order.order_id
        }), 200

    except Exception as e:
        return jsonify({'ERROR': e}), 500


# update order status
@app.put('/order/status/<order_id>')
@authenticate_user
def updates_order_status(order_id):
    try:
        data = request.get_json()
        if data is None or 'status' not in data:
            return jsonify({'error': 'Missing "status" parameter'}), 400

        order = Order.query.filter_by(order_id=order_id).first()
        if not order:
            return jsonify({'ERROR': 'Order not found'}), 404

        valid_status = ["Order Placed", "Processing", "Shipped","Delivered"]
        updated_status = data['status']
        if updated_status not in valid_status:
            return jsonify({'ERROR': f'{updated_status} is not a valid status'}), 400

        order.status = updated_status
        db.session.commit()

        return jsonify({
            'order_id': order.order_id,
            'message': 'Order status updated',
            'status': order.status
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'ERROR': e}), 500


# update the order
@app.put('/order/update/<order_id>')
def update_order(order_id):
    try:
        data = request.get_json()
        if not data or 'items' not in data:
            return jsonify({'ERROR': 'Missing parameters or nothing to update'}), 400
        
        order = Order.query.filter_by(order_id=order_id).first()
        if not order:
            return jsonify({'ERROR': 'Order not found'}), 404

        # check if order is already Shipped or Delivered
        if order.status == "Shipped" or order.status == "Delivered":
            return jsonify({'message': 'Order update window expired!!'}), 400
        
        # remove the old items
        OrderItem.query.filter_by(order_id=order_id).delete()

        # add new items
        total_amount = 0.0
        items = []
        for item in data['items']:
            item_id = item['id']
            quantity = item['qty']
            item_data = Item.query.get(item_id)

            if not item_data:
                return jsonify({'ERROR': f'Cannot add item with item id: {item_id}'}), 400
            
            new_item = OrderItem(
                order_id=order_id,
                item_id=item_id,
                quantity=quantity
            )        

            total_amount += item_data.price * quantity
            items.append({
                'name': item_data.name,
                'price': item_data.price,
                'quantity': quantity
            })
            db.session.add(new_item)
        
        # Update order details
        order.status = "Order Placed"
        order.total_amount = total_amount
        order.timestamp = datetime.now()

        db.session.commit()

        return jsonify({
            'message': 'Order updated successfully',
            'order_id': order.order_id,
            'amount': order.total_amount,
            'items': items
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'ERROR': e}), 500


# delete order
@app.delete('/order/cancel/<order_id>')
def cancel_order(order_id):
    try:
        order = Order.query.filter_by(order_id=order_id).first()
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        # if order is already shipped or delivered
        if order.status == "Shipped" or order.status == "Delivered":
            return jsonify({'message': 'Order cancellation window is expired!!'}), 400
        
        # delete order_items entries
        OrderItem.query.filter_by(order_id=order_id).delete()

        # delete order from 'orders' table
        db.session.delete(order)

        db.session.commit()
        return jsonify({'message': 'Order deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'ERROR': e}), 500


if __name__ == '__main__':
    app.run()