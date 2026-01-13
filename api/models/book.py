from api.main import db

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(10), nullable=False, default='GBP')
    rating = db.Column(db.Float, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    img_url = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(500), nullable=False, unique=True)
    
    def __repr__(self):
        return f'<Book {self.title}>'
    
    __table_args__ = (
        db.Index('idx_title_category', 'title', 'category'),
    )