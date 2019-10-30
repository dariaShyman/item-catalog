#! /usr/bin/env python

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


# User table for login logic
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    # Return user object data in easily serializeable format
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture,
        }


# Category table for grouping items
class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    slug = Column(String(250), nullable=False)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Return category object data in easily serializeable format
    @property
    def serialize(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'name': self.name,
            'user_id': self.user_id,
        }


# Item table
class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    slug = Column(String(250), nullable=False)
    name = Column(String(250), nullable=False)
    description = Column(String(250))
    address = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category, backref='items')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Return item object data in easily serializeable format
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'slug': self.slug,
            'name': self.name,
            'description': self.description,
            'address': self.address,
            'category_id': self.category_id,
            'user_id': self.user_id,
        }


engine = create_engine('sqlite:///appdata.db')

Base.metadata.create_all(engine)
