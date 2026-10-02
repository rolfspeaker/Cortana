from modules.gui import application_window as window # Import the application_window script from the GUI folder
from modules.core import database 

if __name__ == "__main__":
    database.initialize_database() # Initialize the database
    application = window.initialize();