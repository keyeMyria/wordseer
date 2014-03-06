"""

===========
Data Models
===========

This module contains the model-level logic, built on SQLAlchemy.

"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import create_engine, Column, Table, Integer, String, Boolean, ForeignKey, Text
from config import *
from sqlalchemy.orm import relationship, backref, sessionmaker

# create database connection
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)
session = Session()


class Base(object):
    """This is a customized version of SQLAlchemy's Base object.

    It serves to abstract away some of the SQL language and logic to add more
    of a object-oriented style to the models. The language used still mimics
    SQLAlchemy, to avoid confusion.  It also has default configurations that
    apply to all models.

    """

    @declared_attr
    def __tablename__(cls):
        """Define the table name.

        By default, it is the pluraized lower case version of the class name

        """

        # table name should be plural of model name
        import inflect
        return inflect.engine().plural(cls.__name__).lower()

    # Define the primary key
    id = Column(Integer, primary_key=True)

    def save(self):
        """Commits this model instance to the database.

        TODO: should return either True or False depending on its success.
        """
        session.add(self)
        session.commit()

    @classmethod
    def get(cls, id):
        """Look up a single instance based on its primary key.

        The method name is borrowed from Django.

        TODO: should throw an error if not found.

        Args:
          id (int): the primary key of the record.

        Returns:
          An instance of the model, if the record is found.

          Raises an error if not found.

        """
        return session.query(cls).filter(cls.id==id).first()

    @classmethod
    def all(cls):
        """Get all records for this model.

        Returns:
          Query object containing all records in the table for this model.

        """
        return session.query(cls)

    # Criteria-based look-up; see SQLAlchemy docs for use
    @classmethod
    def filter(cls, criteria):
        """Query this model's table based on a criteria.

        See the ORM documentation for SQLAlchemy for the different operators
        that can be used in the criteria parameter.

        Args:
          criteria: an SQLAlchemy-style criteria.

        Returns:
          Query object containing the matching records.

        """
        return session.query(cls).filter(criteria)

# Set the above Base class as the default model.
Base = declarative_base(cls=Base)

class Unit(Base):
    """A model representing a unit (or segment) of text.

    This can be either a full document, a section or chapter of a document,
    an act in a play, or anything that is made of sentences.

    Units are hierarchical; one unit can contain many children units.

    Attributes:
      unit_type (str): the unit type (document, section, etc.).
      number (int): a sequencing number (e.g. 2 for chapter 2).

    Relationships:
      belongs to: parent (Unit)
      has many: children (Unit)

    TODO: implement relationships

    """

    unit_type = Column(String(64), index = True)
    number = Column(Integer, index = True)

class Sentence(Base):
    """A model representing a sentence.

    The sentence model is treated like "leaf" units. It has a link to its
    parent unit. Sentences contain words (the model), and also stores its
    own raw text, for use in search results.

    Attributes:
      unit_id: a link to the unit containing the sentence.
      text: the raw text of the sentence.

    Relationships:
      belongs to: unit
      has many: words

    NOTE: should test sentence reconstruction using the actual word model.

    """

    unit_id = Column(Integer, ForeignKey('unit.id'))
    text = Column(Text, index = True)

    # Relationships
    unit = relationship("Unit", backref=backref("sentences"))

    words = relationship("Word",
        secondary="word_in_sentence",
        backref="sentences"
    )

class Word(Base):
    """A model representing a word.

    Words are the most basic building blocks of everything.

    Attributes:
      word (str): the word

    Relationships:
      has many: sentences

    """

    word = Column(String, index = True)

class Property(Base):
    """A model representing a property of a unit.

    Metadata about units are stored as properties, which have a link to the
    unit it belongs to. Any form of metadata can be assigned to a unit, making
    them extensible and flexible.

    Attributes:
      unit_id: the primary key of the unit it belongs to
      name: the name of the property
      value: the value of the property

    Relationships:
      belongs to: unit

    """

    # Schema
    unit_id = Column(Integer, ForeignKey('unit.id'))
    property_name = Column(String, index = True)
    property_value = Column(String, index = True)

    # Relationships
    unit = relationship("Unit", backref=backref("metadata", uselist=False))

# Many-to-many table between this model and the Word model
word_in_sentence = Table("word_in_sentence", Base.metadata,
    Column('word_id', Integer, ForeignKey('word.id')),
    Column('sentence_id', Integer, ForeignKey('sentence.id'))
)

class Log(Base):
    """
    A log entry, which is recorded in the database.
    """

    __tablename__ = "log"

    log_item = Column(String(100), nullable = False, primary_key = True)
    item_vaslue = Column(Text, nullable = False)
