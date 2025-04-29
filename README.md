# skype-archiving
Messy script to take the downloaded json files of archived skype chats because I don't want to move to teams.

After exporting data from skype, it will include a messier `messages.json` file, which is intended to be readout by this script and converted into markdown files for easier reference.

Inputs should be modified in `readout-chats.py` before running. There is an additional option to convert from markdown to PDF files using `pandoc` which I haven't tested thoroughly so it's off by default.