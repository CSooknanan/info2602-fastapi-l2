import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select, or_, col  # Added or_ and col for Exercise 1
from sqlalchemy.exc import IntegrityError

cli = typer.Typer()

@cli.command()
def initialize():
    """ Deletes all tables and creates a fresh database with a 'bob' user. """
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        # Using keyword arguments so it doesn't throw the TypeError
        bob = User(username='bob', email='bob@mail.com', password='bobpass') # Create a new user (in memory)
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        print("Database Initialized")

@cli.command()
def get_user(username:str):
    """ Finds a single user by their exact username. """
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found!')
            return
        print(user)


@cli.command()
def get_all_users():
    """ Lists every user currently in the database. """
    with get_session() as db:
        all_users = db.exec(select(User)).all()
        if not all_users:
            print("No users found")
        else:
            for user in all_users:
                print(user)

@cli.command()
def change_email(username: str, new_email:str):
    """ Updates the email for an existing user. """
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to update email.')
            return
        user.email = new_email
        db.add(user)
        db.commit()
        print(f"Updated {user.username}'s email to {user.email}")

@cli.command()
def create_user(username: str, email:str, password: str):
    """ Creates a new user and saves them to the database. """
    with get_session() as db: # Get a connection to the database
        newuser = User(username, email, password)
        try:
            db.add(newuser)
            db.commit()
        except IntegrityError as e:
            db.rollback() #let the database undo any previous steps of a transaction
            #print(e.orig) #optionally print the error raised by the database
            print("Username or email already taken!") #give the user a useful message
        else:
            print(newuser) # print the newly created user

@cli.command()
def delete_user(username: str):
    """ Deletes a user from the database. """
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to delete user.')
            return
        db.delete(user)
        db.commit()
        print(f'{username} deleted')

@cli.command()
def find_user(query: str):
    """ Exercise 1: Finds a user using a partial match of their email OR username. """
    with get_session() as db:
        statement = select(User).where(
            or_(
                col(User.username).contains(query),
                col(User.email).contains(query)
            )
        )
        results = db.exec(statement).all()
        if not results:
            print(f"No users found matching: {query}")
        else:
            for user in results:
                print(user)

@cli.command()
def list_users(limit: int = 10, offset: int = 0):
    """ Exercise 2: Lists the first N users using a limit and offset. """
    with get_session() as db:
        statement = select(User).limit(limit).offset(offset)
        results = db.exec(statement).all()
        if not results:
            print("No users found.")
        else:
            for user in results:
                print(user)



if __name__ == "__main__":
    cli()