from flask import Flask, render_template, redirect, url_for, flash, request
from models import db, User, Category, Item, Bid
from forms import BidForm, ItemForm
from datetime import datetime
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auction.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


def seed_data():
    """Seed initial categories and a dummy user if DB is empty."""
    if Category.query.count() == 0:
        categories = ['Electronics', 'Clothing', 'Collectibles', 'Books', 'Sports', 'Other']
        for name in categories:
            db.session.add(Category(name=name))
        db.session.commit()

    if User.query.count() == 0:
        demo = User(
            username='demo',
            email='demo@auction.com',
            password_hash=generate_password_hash('demo123')
        )
        db.session.add(demo)
        db.session.commit()


@app.before_request
def create_tables():
    db.create_all()
    seed_data()


# ── Home: all open auctions ──────────────────────────────────────────────────

@app.route('/')
def index():
    now = datetime.utcnow()
    items = Item.query.filter(Item.status == 'open', Item.end_time > now).order_by(Item.end_time.asc()).all()
    categories = Category.query.all()
    selected_cat = request.args.get('category', type=int)
    if selected_cat:
        items = [i for i in items if i.category_id == selected_cat]
    return render_template('index.html', items=items, categories=categories, selected_cat=selected_cat)


# ── Item detail + bidding ────────────────────────────────────────────────────

@app.route('/item/<int:item_id>', methods=['GET', 'POST'])
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    form = BidForm()

    if form.validate_on_submit():
        if not item.is_open():
            flash('This auction has ended.', 'error')
            return redirect(url_for('item_detail', item_id=item_id))

        min_bid = item.current_price() + 0.01
        if form.amount.data < min_bid:
            flash(f'Bid must be higher than the current price of ${item.current_price():.2f}.', 'error')
            return redirect(url_for('item_detail', item_id=item_id))

        # Get or create a user by name (simplified — no real auth)
        user = User.query.filter_by(username=form.bidder_name.data).first()
        if not user:
            user = User(
                username=form.bidder_name.data,
                email=f'{form.bidder_name.data}@placeholder.com',
                password_hash=generate_password_hash('placeholder')
            )
            db.session.add(user)
            db.session.flush()

        bid = Bid(item_id=item.id, bidder_id=user.id, amount=form.amount.data)
        db.session.add(bid)
        db.session.commit()
        flash(f'Bid of ${form.amount.data:.2f} placed successfully!', 'success')
        return redirect(url_for('item_detail', item_id=item_id))

    bids = Bid.query.filter_by(item_id=item_id).order_by(Bid.placed_at.desc()).all()
    return render_template('item.html', item=item, form=form, bids=bids)


# ── Create a new listing ─────────────────────────────────────────────────────

@app.route('/item/new', methods=['GET', 'POST'])
def create_item():
    form = ItemForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.seller_name.data).first()
        if not user:
            user = User(
                username=form.seller_name.data,
                email=f'{form.seller_name.data}@placeholder.com',
                password_hash=generate_password_hash('placeholder')
            )
            db.session.add(user)
            db.session.flush()

        item = Item(
            seller_id=user.id,
            category_id=form.category_id.data,
            title=form.title.data,
            description=form.description.data,
            starting_price=form.starting_price.data,
            end_time=form.end_time.data,
            status='open'
        )
        db.session.add(item)
        db.session.commit()
        flash('Your item has been listed!', 'success')
        return redirect(url_for('index'))

    return render_template('create.html', form=form)


# ── Close an auction manually ────────────────────────────────────────────────

@app.route('/item/<int:item_id>/close', methods=['POST'])
def close_item(item_id):
    item = Item.query.get_or_404(item_id)
    item.status = 'closed'
    db.session.commit()
    flash('Auction closed.', 'success')
    return redirect(url_for('item_detail', item_id=item_id))


if __name__ == '__main__':
    app.run(debug=True)