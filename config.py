import os

class Config:
    # PostgresSQL Database URI
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://mohamed:1234@localhost/tahoai')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
