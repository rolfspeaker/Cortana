from modules.gui import application_window as window # Import the application_window script from the GUI folder
from modules.core import database as SQL_database

if __name__ == "__main__":
    SQL_database.initialize_database() # Initialize the SQL database
    application = window.initialize();