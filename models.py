from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('Item', backref='seller', lazy=True, foreign_keys='Item.seller_id')
    bids = db.relationship('Bid', backref='bidder', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    items = db.relationship('Item', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'


class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    starting_price = db.Column(db.Float, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(10), default='open')  # 'open' or 'closed'

    bids = db.relationship('Bid', backref='item', lazy=True)

    def current_price(self):
        if self.bids:
            return max(b.amount for b in self.bids)
        return self.starting_price

    def bid_count(self):
        return len(self.bids)

    def is_open(self):
        return self.status == 'open' and datetime.utcnow() < self.end_time

    def __repr__(self):
        return f'<Item {self.title}>'


class Bid(db.Model):
    __tablename__ = 'bid'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    bidder_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    placed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Bid {self.amount} on Item {self.item_id}>'