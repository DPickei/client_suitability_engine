import sqlalchemy
from src.database.models import Base
from src.database import shared

def get_engine():
    """Returns an SQLAlchemy engine connected to the database."""
    db_path = shared.get_db_path()
    engine = sqlalchemy.create_engine(f"sqlite:///{db_path}", echo=True)  # Set echo=True for debugging SQL commands
    return engine

def initialize_database():
    """Creates all tables defined in models.py."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("Database initialized successfully.")

if __name__ == "__main__":
    initialize_database()
