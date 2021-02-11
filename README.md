# VLC-Youtube
A python GUI application that plays video and audio from local storage or Youtube

# Requirements
As of February 11, 2021:
```
pip install youtube-search-python==1.4.0
pip install pytube==10.4.1
```
OR
[version 1.4.0] [youtubesearchpython](https://pypi.org/project/youtube-search-python/1.4.0/)
[version 10.4.1] [pytube](https://pypi.org/project/pytube/10.4.1/)

Versions other than the ones mentioned above may break the code so it is advisable to install those versions until further testing has been done on other ones.

# How to use
Use as a python script:
```
python vlcTube.py
```
OR
Make an executable file using pytinstaller:
1. Install pyinstaller
    ```
    pip install pyinstaller
    ```
2. Make an executable file
    ```
    pyinstaller --onefile -w vlcTube.py
    ```
3. The .exe file is all you need in the `dist` folder
    ```
    dist/vlcTube.exe
    ```
# Notes
- Should work with Python 3.6 or later 
- Only tested for Windows 10
