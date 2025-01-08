![gimmich](/gimmich.gif)

# gimmich

gimmich is a GUI for immich to make bulk uploading/downloading using your image server easy.

- Immich API based.
- Supports multiple paths at once.
- Securely stores credential info between sessions.
- Create albums based on user specified label and/or based on the directory name.
- Import descriptions from text files of the same name as the image file. eg: image01.png and image01.txt. This is
useful for importing machine learning datasets.
- Export those same descriptions back to text file captions
- Import/export tags from text files using delimiters.
- Import tags based on directory name or user input.
- Preliminary bulk download based on albums, tags, or people.


## Requirements

- Python 3.12
- customtkinter `pip install customtkinter`
- keyring `pip install keyring`
- pillow `pip install pillow`

## Installation

- Download or clone this repo using git. `git clone https://github.com/Meatfucker/gimmich`
- Run `python gimmich.py`

## TODO

- Add bulk downloading for smart search 
- Make upload tab look nicer and unified with the look of the download tab instead of a crusty ol listbox
- Add per pack upload options similar to download ones.
- Make proper installer
- Make standalone exe

