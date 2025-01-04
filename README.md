![gimmich](/gimmich-screenshot.png)

# gimmich

gimmich is a GUI frontend for immich to make bulk uploading to your image server easy.

- Immich API based
- Supports multiple paths at once
- Securely stores credential info between sessions
- Create albums based on user specified label and/or based on the directory name
- Import descriptions from text files of the same name as the image file. eg: image01.png and image01.txt. This is
useful for importing machine learning datasets.
- Import tags from text files using delimiters
- Import tags based on directory name or user input


## Requirements

- Python 3.12
- customtkinter `pip install customtkinter`
- keyring `pip install keyring`

## Installation

- Download or clone this repo using git. `git clone https://github.com/Meatfucker/gimmich`
- Run `python gimmich.py`

## TODO

- Add bulk downloading tab with various criteria to bulk download assets
