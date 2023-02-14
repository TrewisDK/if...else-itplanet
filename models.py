from sqlalchemy import create_engine
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.operators import ilike_op
from sqlalchemy import and_
from sqlalchemy import Column, Integer, String, ARRAY, BigInteger, Float, DateTime, ForeignKey, Table, Double
from sqlalchemy.orm import sessionmaker, Session, relationship

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:VfRFwObDDvvW@127.0.0.1/itplanet"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

Base = declarative_base()

animal_types = Table('animal_types', Base.metadata,
                     Column('animal_id', BigInteger(), ForeignKey('animals.id')),
                     Column('animal_type_id', BigInteger, ForeignKey('animal_type.id'))
                     )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class AnimalType(Base):
    __tablename__ = "animal_type"

    id = Column(BigInteger, primary_key=True)
    animaltype = Column(String)


class LocationPoint(Base):
    __tablename__ = "locations_point"

    id = Column(BigInteger, primary_key=True)
    latitude = Column(Double)
    longitude = Column(Double)


class Animal(Base):
    __tablename__ = "animals"

    id = Column(BigInteger, primary_key=True)
    animalTypes = relationship("AnimalType", secondary=animal_types, backref='animals')
    weight = Column(Float)
    lenght = Column(Float)
    height = Column(Float)
    gender = Column(String)
    lifeStatus = Column(String)
    chippingDateTime = Column(DateTime)
    chipperId = Column(Integer, ForeignKey(User.id))
    chippingLocationId = Column(BigInteger, ForeignKey(LocationPoint.id))
    deathDateTime = Column(DateTime)


class AnimalVisited(Base):
    __tablename__ = "animal_location_visited"

    id = Column(BigInteger, primary_key=True, index=True)
    animal_id = Column(BigInteger, ForeignKey(Animal.id))
    datetime_of_visited_location = Column(DateTime)
    location = Column(BigInteger, ForeignKey(LocationPoint.id))


Base.metadata.create_all(bind=engine)
