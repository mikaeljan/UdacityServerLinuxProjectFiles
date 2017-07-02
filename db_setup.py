from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()
# ================================================
# DB Classes
# ========User========


class User(Base):
    """Class for User instances """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            "email": self.email
        }

# ========Category========
class Category(Base):
    """Class for Category instances"""
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


# ========Item========
class Item(Base):
    """Class for Item instances"""
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    book_title = Column(String(80), nullable=False)
    description = Column(String(450))
    # Integers for price?
    price = Column(String(8))
    year_published = Column(Integer)
    author = Column(String(80))
    created_on = Column(DateTime(timezone=True), server_default=func.now())
    updated_on = Column(DateTime(timezone=True), onupdate=func.now())

    creator_id = Column(Integer, ForeignKey("user.id"))
    creator = relationship(User)
    category_name = Column(Integer, ForeignKey('category.name'))
    category = relationship(Category)
    # ForeignKeyConstraint(['creator_id', 'category_name'], ['user.id'], ['category.name'] )
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'book_title': self.book_title,
            'description': self.description,
            'author': self.author,
            'price': self.price,
            'creator_id': self.creator_id,
            'category_name': self.category_name
        }

# ==================================================
# engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
engine = create_engine('postgresql://catalog:catalog@localhost/itemscatalog')
Base.metadata.create_all(engine)
