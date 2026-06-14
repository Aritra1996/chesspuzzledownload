import os

from fasthtml.common import *
from dotenv import load_dotenv

load_dotenv()

_HERE = os.path.dirname(os.path.abspath(__file__))
app, rt = fast_app(pico=False, static_path=_HERE,
                   secret_key=os.getenv("SECRET_KEY") or os.urandom(16).hex())
