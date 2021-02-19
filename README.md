# VLC-Youtube
A python GUI application that plays video and audio from local storage or Youtube

# Requirements
```
pip install youtube-search-python
pip install python-vlc
pip install pytube
```
WARNING: As of February 11, 2021, versions other than the ones mentioned below may break the code so it is advisable to install those versions until further testing has been done on other ones.
```
pip install youtube-search-python==1.4.0
pip install pytube==10.4.1
```

# How to use
Use as a python script:
```
python vlcTube.py
```
Or make an executable file using pytinstaller:
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
