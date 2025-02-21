# core-api/manage.py

from flask.cli import FlaskGroup
from src.app import app
from src.models import db, User, UserSensorData

cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    """Crea la base de datos y las tablas."""
    db.create_all()
    db.session.commit()
    print("Base de datos creada.")

@cli.command("seed_db")
def seed_db():
    """Inserta datos de prueba en la base de datos."""
    user = User(
        username="testuser",
        email="test@example.com",
        password="password",
        name="Test",
        lastname="User",
        address="123 Test St",
        gender="MALE",
        profile="BIKER",
        phone="1234567890"
    )
    db.session.add(user)
    db.session.commit()
    print("Datos de prueba insertados.")

if __name__ == "__main__":
    cli()