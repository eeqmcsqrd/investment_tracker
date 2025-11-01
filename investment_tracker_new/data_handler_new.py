
# data_handler_new.py
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, inspect
from datetime import datetime
import os

DB_FILE = 'investment_data_new.db'
OLD_CSV_FILE = 'investment_data.csv'

def get_engine():
    """Creates and returns a SQLAlchemy engine."""
    return create_engine(f'sqlite:///{DB_FILE}')

def init_database():
    """Initializes the database and tables if they don't exist."""
    engine = get_engine()
    if not os.path.exists(DB_FILE):
        metadata = sqlalchemy.MetaData()
        sqlalchemy.Table('investments',
            metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
            sqlalchemy.Column('date', sqlalchemy.Date, nullable=False),
            sqlalchemy.Column('investment', sqlalchemy.String, nullable=False),
            sqlalchemy.Column('value', sqlalchemy.Float, nullable=False),
            sqlalchemy.Column('currency', sqlalchemy.String, nullable=False)
        )
        metadata.create_all(engine)
        migrate_from_csv()

def load_data():
    """Loads all data from the SQLite database."""
    engine = get_engine()
    with engine.connect() as connection:
        return pd.read_sql('investments', connection)

def save_data(df):
    """Saves a DataFrame to the SQLite database, replacing existing data."""
    engine = get_engine()
    with engine.connect() as connection:
        df.to_sql('investments', connection, if_exists='replace', index=False)

def add_entry(date, investment, value, currency):
    """Adds a single entry to the database."""
    engine = get_engine()
    with engine.connect() as connection:
        connection.execute(
            sqlalchemy.text(
                """INSERT INTO investments (date, investment, value, currency)
                   VALUES (:date, :investment, :value, :currency)"""
            ),
            [{"date": date, "investment": investment, "value": value, "currency": currency}]
        )
        connection.commit()


def add_bulk_entries(entries):
    """Adds multiple entries to the database."""
    engine = get_engine()
    df = pd.DataFrame(entries)
    with engine.connect() as connection:
        df.to_sql('investments', connection, if_exists='append', index=False)

def migrate_from_csv():
    """Migrates data from the old CSV file to the new SQLite database."""
    if os.path.exists(OLD_CSV_FILE):
        df = pd.read_csv(OLD_CSV_FILE)
        if not df.empty:
            df['Date'] = pd.to_datetime(df['Date'])
            save_data(df)

