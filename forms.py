from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SelectField, DateTimeLocalField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class BidForm(FlaskForm):
    amount = FloatField('Your Bid ($)', validators=[
        DataRequired(),
        NumberRange(min=0.01, message='Bid must be greater than zero.')
    ])
    bidder_name = StringField('Your Name', validators=[DataRequired()])
    submit = SubmitField('Place Bid')


class ItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    starting_price = FloatField('Starting Price ($)', validators=[
        DataRequired(),
        NumberRange(min=0.01, message='Starting price must be greater than zero.')
    ])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    end_time = DateTimeLocalField('Auction End Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    seller_name = StringField('Your Name', validators=[DataRequired()])
    submit = SubmitField('List Item')