![gimmich](/gimmich.gif)

# gimmich

gimmich is a GUI for immich to make bulk uploading/downloading using your immich server easy.

- Immich API based.
- Supports multiple paths at once.
- Securely stores credential info between sessions.
- Create albums based on user specified label and/or based on the directory name.
- Import descriptions from text files of the same name as the image file. eg: image01.png and image01.txt. This is
useful for importing machine learning datasets.
- Export those same descriptions back to text file captions
- Import/export tags from text files using delimiters.
- Import tags based on directory name or user input.
- Bulk download based on albums, tags, or people.
- Smart search based bulk downloader.


## Requirements

- Python 3.12


## Installation

- Download or clone this repo using git. `git clone https://github.com/Meatfucker/gimmich`
- Run either start_windows.bat or start_linux.sh depending on your OS. It will create the venv, install any needed dependencies, and then start gimmich.

## TODO

- Make standalone exe
- Fix upload caption progress bars

