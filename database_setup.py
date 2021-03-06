#!usr/bin/env python

import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Users(Base):
    """ Table definition 'Users' """

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }


class Categories(Base):
    """ Table definition 'Categories' """

    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(Users)

    @property
    def serialize(self):
        """ Return object data in easily serializeable format """
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id
        }


class Items(Base):
    """ Table definition 'Items' """

    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(400))
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship(Categories)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(Users)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
            'category_id': self.category_id
        }


engine = create_engine('sqlite:///catalog.db',connect_args={'check_same_thread': False})


Base.metadata.create_all(engine)

print('Finished creating the database!')
