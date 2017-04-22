from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class BaseModel(db.Model):
    """Base data model for all objects"""
    __abstract__ = True

    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        """Define a base way to print models"""
        return '%s(%s)' % (self.__class__.__name__, {
            column: value
            for column, value in self._to_dict().items()
        })

    def json(self):
        """
                Define a base way to jsonify models, dealing with datetime objects
        """
        return {
            column: value if not isinstance(value, datetime.date) else value.strftime('%Y-%m-%d')
            for column, value in self._to_dict().items()
        }


class User(BaseModel,db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Numeric, unique=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    gender = db.Column(db.String(20))
    locale = db.Column(db.String(20))
    timezone = db.Column(db.Integer)

    def __init__(self, user_id,first_name,last_name,gender,locale,timezone):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.gender=gender
        self.locale=locale
        self.timezone=timezone
       

    def __repr__(self):
        return '<User %r>' %self.user_id
    