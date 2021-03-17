from app import db
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime

class Filer(db.Model):
    __tablename__ = 'filers'
    
    id = db.Column(db.Integer, primary_key=True)
    ein = db.Column(db.Integer)
    name = db.Column(db.String)
    addressLine1 = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    postal_code = db.Column(db.String)
    last_updated = db.Column(db.DateTime)

    def __init__(self, ein, name, addressLine1, city, state, postal_code ):
        self.ein = ein
        self.name = name
        self.addressLine1 = addressLine1
        self.city = city
        self.state = state
        self.postal_code = postal_code
        self.last_updated = datetime.now()

    def serialize(self):
        return {
                "id": self.id,
                "name": self.name,
                "address": self.addressLine1,
                "city": self.city,
                "state": self.state,
                "postal_code": self.postal_code,
                "last_update": self.last_updated.strftime('%m/%d/%Y %H:%M:%S')
                }
    
    def __repr__(self):
        return '<name {}>'.format(self.name)

class Recipient(db.Model):
    __tablename__ = 'recipients'

    id = db.Column(db.Integer, primary_key=True)
    ein = db.Column(db.Integer)
    name = db.Column(db.String)
    addressLine1 = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    postal_code = db.Column(db.String)
    filer_ein = db.Column(db.Integer)
    grant_amount = db.Column(db.Integer)
    grant_purpose = db.Column(db.String)
    last_updated = db.Column(db.DateTime)

    def __init__(self, ein, name, addressLine1, city, state, postal_code, filer_ein, grant_amount, grant_purpose ):
        self.ein = ein
        self.name = name
        self.addressLine1 = addressLine1
        self.city = city
        self.state = state
        self.postal_code = postal_code
        self.filer_ein = filer_ein
        self.grant_amount = grant_amount
        self.grant_purpose = grant_purpose
        self.last_updated = datetime.now()

    def serialize(self):
        return {
                "id": self.id,
                "name": self.name,
                "address": self.addressLine1,
                "city": self.city,
                "state": self.state,
                "postal_code": self.postal_code,
                "grant_amount": self.grant_amount,
                "grant_purpose": self.grant_purpose,
                "last_update": self.last_updated.strftime('%m/%d/%Y %H:%M:%S')
                }

    def __repr__(self):
        return '<name {}>'.format(self.name)
