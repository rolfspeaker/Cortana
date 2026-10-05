import asyncio
from threading import Lock, Thread
from pathlib import Path

from desktop_notifier import DesktopNotifier, Urgency, Icon, DEFAULT_SOUND


ICON_PATH = Path(__file__).resolve().parents[2] / "images" / "cortana_smile.png"

# Create the notifier later on the thread that will send its notifications
notifier = None
_loop = asyncio.new_event_loop()
_start_lock = Lock()


def _run_loop():
    asyncio.set_event_loop(_loop)
    _loop.run_forever()


_thread = Thread(target=_run_loop, daemon=True)


def start():
    # Prevent two simultaneous requests from starting the thread twice
    with _start_lock:
        if not _thread.is_alive():
            _thread.start()


async def _send_alert(title, message, priority, on_sent=None):
    global notifier

    # This coroutine runs on the notification thread
    # Windows requires the notifier to be created and used on that same thread
    if notifier is None:
        notifier = DesktopNotifier(
            app_name="Cortana",
            app_icon=Icon(path=ICON_PATH),
        )

    urgencies = {
        "low": Urgency.Low,
        "medium": Urgency.Normal,
        "high": Urgency.Critical,
    }
    # Let the reminder checker receive failures through the returned Future
    result = await notifier.send(
        title=title,
        message=message,
        urgency=urgencies.get(priority.lower(), Urgency.Normal),
        sound=None,
    )

    # Audio runs immediately on the notification thread after submission
    # Keep audio failures separate so a successful alert is not retried
    if on_sent is not None:
        try:
            on_sent()
        except Exception as error:
            print(f"Could not play reminder sound: {error}")
    return result


def send_alert(title: str, message: str, priority: str = "Medium", on_sent=None):
    # Queue the send without blocking the GUI
    start()
    return asyncio.run_coroutine_threadsafe(
        _send_alert(title, message, priority, on_sent),
        _loop,
    )
