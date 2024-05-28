from Market import db, bcrypt, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    items = db.relationship('Item', backref='owned_user', lazy=True)
    
    def __repr__(self):
        return f'User {self.username}'
    
    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
    
    def password_check(self, password_attempt):
        return bcrypt.check_password_hash(self.password_hash, password_attempt)
    
    def can_sell(self, item_obj):
        return item_obj in self.items
    
    def delete_user(user_id):
        user = User.query.filter_by(id=user_id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(length=1024), nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'Item {self.name}'
    
    @property
    def prettier_price(self):
            return f'{int(self.price) if self.price == int(self.price) else self.price} $'
        
    def buy(self, user):
        self.owner = user.id
        db.session.commit()
    
    def sell(self, user):
        self.owner = None
        db.session.commit()
    
    def delete_item(item_id):
        item = Item.query.filter_by(id=item_id).first()
        if item:
            db.session.delete(item)
            db.session.commit()
            return True
        return False
    
    def update_item(self, name, price, barcode, description):
        self.name = name
        self.price = price
        self.barcode = barcode
        self.description = description
        self.owner = None 
        db.session.commit()
