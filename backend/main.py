import os
import sys
import threading

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Electron picks a free port and passes it in PORT, "python main.py" uses 5000
    port = int(os.environ.get("PORT", "5000"))

    # No debug / auto reload inside the desktop app: packaged with PyInstaller
    # (sys.frozen) or started by Electron (DESKTOP=1). The reloader starts a second
    # process that Electron couldn't stop when the window is closed
    desktop = getattr(sys, "frozen", False) or os.environ.get("DESKTOP") == "1"

    if desktop:
        # Electron keeps our stdin open. When Electron closes (even if it crashes or is
        # killed) stdin ends: stop too, so the backend never stays running alone
        def exit_when_electron_closes():
            try:
                sys.stdin.read()
            finally:
                os._exit(0)

        threading.Thread(target=exit_when_electron_closes, daemon=True).start()

    app.run(host="127.0.0.1", port=port, debug=not desktop, use_reloader=not desktop, threaded=True)
