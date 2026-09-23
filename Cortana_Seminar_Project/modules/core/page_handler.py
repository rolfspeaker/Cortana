
import customtkinter as ctk

pages: dict[str, ctk.CTkFrame] = {}
current_page: str | None = None # Decided to make this a string variable rather than a reference to the object itself so that we'd be able to get the name of the frame itself if need be

def navigate_to_page(page_title: str):
    if page_title not in pages:
        raise ValueError(f"Page unknown or yet to be initialized: {page_title}")

    if current_page == page_title:
        return

    if current_page is not None: # If the user is currently on a page
        pages[current_page].place_forget() # Render the page out of sight

    pages[page_title].place( # Replace the former page with a new one
        x=0, y=0, relwidth=1, relheight=1
    )
    current_page = page_title