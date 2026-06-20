import os

os.environ.setdefault("WPD_PROFILE", "belgium_only")
os.environ.setdefault("WPD_PUBLIC_PREVIEW", "true")
os.environ.setdefault("WPD_APP_TITLE", "Belgian Politics Data")
os.environ.setdefault("WPD_EXPOSE_COUNTRIES", "belgium")

from engine_app import main


main()
