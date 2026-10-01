import importlib
import inspect

import pkgutil
import re

import customtkinter as ctk

pages: dict[str, ctk.CTkFrame] = {}
current_page: str | None = None

def discover_page_classes():
    # Find concrete CTkFrame classes defined in the pages package
    from modules.gui import pages as page_package

    discovered: dict[str, type[ctk.CTkFrame]] = {}
    module_names = [page_package.__name__]
    module_names.extend(
        info.name
        for info in pkgutil.walk_packages(
            page_package.__path__, prefix=page_package.__name__ + "."
        )
    )
    for module_name in sorted(module_names):
        module = importlib.import_module(module_name)

        for name, page_class in inspect.getmembers(module, inspect.isclass):
            if (page_class.__module__ != module.__name__ or page_class is ctk.CTkFrame or not issubclass(page_class, ctk.CTkFrame) or inspect.isabstract(page_class) or name.startswith("_")):
                continue

            # LandingPage -> landing; DailyPlannerPage -> daily_planner.
            title = name.removesuffix("Page")
            title = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", title)
            title = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", title).lower()
            if not title:
                raise ValueError(f"Page class requires a descriptive name: {name}")
            if title in discovered:
                raise ValueError(f"Duplicate page title: {title}")
            discovered[title] = page_class

    return discovered


def initialize_pages():
    # Discover, create, and register all pages, initially hidden

    # Each concrete page class in modules.gui.pages must have no-
    # required constructor arguments. Create the root window before calling this
    global current_page
    page_classes = discover_page_classes()
    for page in pages.values():
        page.destroy()
    pages.clear()
    current_page = None

    for title, page_class in page_classes.items():
        page = page_class()
        pages[title] = page
        page.place_forget()


def navigate_to_page(page_title: str):
    global current_page
    #print(pages.keys()); 

    if page_title not in pages:
        raise ValueError(f"Page unknown or yet to be initialized: {page_title}")
    
    if current_page == page_title:
        return
    
    if current_page is not None:
        pages[current_page].place_forget()

    pages[page_title].place(x=0, y=0, relwidth=1, relheight=1)
    current_page = page_title

