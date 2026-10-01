from modules.gui import application_window as window # Import the application_window script from the GUI folder
runtime_data: dict[str, any] = {} # Initialize an empty dictionary to store runtime data

if __name__ == "__main__":
    # Run app and store the application instance in the runtime_data dictionary 
    application = window.initialize(); runtime_data["window"] = application 