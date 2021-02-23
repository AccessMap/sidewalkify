import os
import sys

poetry_python_lib = os.path.expanduser("~/.poetry/lib")
sys.path.append(os.path.realpath(poetry_python_lib))

from poetry.masonry.builders.sdist import SdistBuilder
from poetry.factory import Factory

factory = Factory()
poetry = factory.create_poetry(os.path.dirname(__file__))

sdist_builder = SdistBuilder(poetry, None, None)
setuppy_blob = sdist_builder.build_setup()

with open("setup.py", "wb") as unit:
    unit.write(setuppy_blob)
    unit.write(b"\n# This setup.py was autogenerated using poetry.\n")