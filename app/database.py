from sqlalchemy.orm import sessionmaker, relationship, Session, declarative_base
from sqlalchemy import create_engine, insert, Column, Integer, String, Date, Float, ForeignKey, MetaData, Table
from decouple import config

from app.config import get_logger

logger = get_logger()
# Get database configuration from environment variables
DATABASE_USER = config('POSTGRES_USER')
DATABASE_PASSWORD = config('POSTGRES_PASSWORD')
DATABASE_HOST = config('POSTGRES_HOST')
DATABASE_NAME = config('POSTGRES_DB')

# Define the database URL
DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"


# Create a SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the SQLAlchemy Base class
Base = declarative_base()

# Dependency function to get a database session


def get_db() -> Session:
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()

# Define a model for the market table


class Market(Base):
    """
    A model representing the market table.

    Attributes:
        id (int): The primary key of the market record.
        option (str): The name of option.
        option_type (str): The type of option (e.g. call, put).
        underlying_price (float, optional): The price of the underlying asset.
        strike_price (float, optional): The strike price of the option.
        time_to_expiry (float, optional): The time to expiry of the option in years.
        risk_free_rate (float, optional): The risk-free interest rate.
        implied_volatility (float, optional): The implied volatility of the option.
    """

    __tablename__ = "market"

    id = Column(Integer, primary_key=True, index=True)
    option = Column(String, nullable=False)
    option_type = Column(String, nullable=False)
    underlying_price = Column(Float, nullable=True)
    strike_price = Column(Float, nullable=True)
    time_to_expiry = Column(Float, nullable=True)
    risk_free_rate = Column(Float, nullable=True)
    implied_volatility = Column(Float, nullable=True)


# Create the database tables
logger.info("Creating Tables")
Base.metadata.create_all(bind=engine, checkfirst=True)
logger.info("Tables created successfully")

# Add some dummy records to the market table


def add_dummy_data(db: Session):
    """
    Adds dummy data to the Market table in the database.

    Parameters:
    - db: SQLAlchemy Session object, for database interaction

    Returns:
    - None
    """
    if not db.query(Market).first():
        # If the table is empty, add some dummy data
        db.execute(insert(Market).values(
            option='BRN',
            option_type='call',
            underlying_price=75.0,
            strike_price=100.0,
            time_to_expiry=0.25,
            risk_free_rate=0.01,
            implied_volatility=0.2,
        ))
        db.execute(insert(Market).values(
            option='HH',
            option_type='put',
            underlying_price=2.0,
            strike_price=10.0,
            time_to_expiry=0.5,
            risk_free_rate=0.02,
            implied_volatility=0.25,
        ))
        db.commit()

        logger.info("Dummy data inserted successfully")


add_dummy_data(SessionLocal())


def drop_table(table_name):
    # Get a reference to the table you want to drop
    table = Table(table_name, Base.metadata)

    # Drop the table
    table.drop(bind=engine)

    logger.info("%s table dropped", table_name)
    return {'message': 'Table dropped.'}


# Drop table
# drop_table('market')
