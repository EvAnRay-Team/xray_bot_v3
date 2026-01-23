import os

# Project Root
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# Source Directory
SRC_PATH = os.path.join(ROOT_PATH, "src")

# Resources Directory
RESOURCE_PATH = os.path.join(ROOT_PATH, "resources")
STATIC_PATH = os.path.join(RESOURCE_PATH, "static")

# Runtime Data Directory
DATA_PATH = os.path.join(ROOT_PATH, "data")

# Resource Sub-paths
FONT_PATH = os.path.join(STATIC_PATH, "font")
TAROT_PATH = os.path.join(STATIC_PATH, "tarot")

# Cover Paths
MAIMAIDX_STATIC_PATH = os.path.join(STATIC_PATH, "maimaidx")
NORMAL_COVER_PATH = os.path.join(MAIMAIDX_STATIC_PATH, "normal_cover")
ABSTRACT_COVER_PATH = os.path.join(MAIMAIDX_STATIC_PATH, "abstract_cover")
