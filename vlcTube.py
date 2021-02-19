# Import standard packages
import time
import threading

# tkinter for python3
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror

# Import third-party packages
try:
    import vlc
    import youtubesearchpython as ysp
except Exception:
    pass

class VLCTube(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("VLCTube")

        # Positions the window in the center of the screen
        x_pos = int((self.winfo_screenwidth()/2) - (960/2))
        y_pos = int((self.winfo_screenheight()/2) - (540/2))
        self.geometry(f"960x540+{x_pos}+{y_pos-35}")

        # Opens the program maximized
        self.state("zoomed")

        # Creates a menubar
        self.menubar = tk.Menu(self)

        # Adds a file menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.has_added = False
        self.create_file_menu()

        # Displays the menubar
        self.config(menu=self.menubar)

        # Create a vlc player instance
        self.vlc_instance, self.vlc_player = self.create_vlc_instance()

        # The panel where the video will be played
        self.video_panel = tk.Frame(self, background="black")
        self.video_panel.pack(fill=tk.BOTH, expand=1)

        # Control panel frame
        self.control_panel = ttk.Frame(self)
        font_size = tkfont.Font(size=8, weight="bold")
        self.search_status = ttk.Label(self.control_panel, text=f"{5*' '}", font=font_size)
        self.search_entry = ttk.Entry(self.control_panel, width=34)
        self.search_button = ttk.Button(self.control_panel, text="Youtube Search", command=self.start_thread)

        choices = list(range(11))
        self.num_of_result = tk.IntVar(self)
        self.search_dropdown = ttk.OptionMenu(self.control_panel, self.num_of_result, *choices)
        self.num_of_result.set(5)
        self.results_button = ttk.Button(self.control_panel, text="View Results", command=self.list_results)
        self.results = None
        self.control_panel.pack(side=tk.BOTTOM)

        # Video slider frame
        self.timers = ttk.Frame(self)

        # Video slider
        self.timeVar = tk.DoubleVar()
        self.timeSliderLast = 0
        self.timeSlider = tk.Scale(self.timers, variable=self.timeVar, command=self.time_slider,
                                   from_=0, to=1000, orient=tk.HORIZONTAL, length=500,
                                   showvalue=0)
        self.timeSlider.pack(side=tk.BOTTOM, fill=tk.X, expand=1)
        self.timeSliderUpdate = time.time()
        self.timers.pack(side=tk.BOTTOM, fill=tk.X)
        self.timeSlider.configure(state="disable")

        # Video controls
        self.play_button = ttk.Button(self.control_panel, text="Play", width=15, command=self.play_pause)
        self.stop_button = ttk.Button(self.control_panel, text="Stop", width=15, command=self.stop)
        self.volume_button = ttk.Button(self.control_panel, text="Volume", width=15, command=None)
        self.play_button.pack(side=tk.LEFT)
        self.stop_button.pack(side=tk.LEFT)
        self.volume_button.pack(side=tk.LEFT)
        
        self.bind_keys()

        self.tick()

    def create_file_menu(self):
        """ Draws the file menu in the window """
        if not self.has_added:
            self.file_menu.add_command(label="Open", command=self.open, accelerator="Ctrl + O")
            self.file_menu.add_command(label="Youtube Search", command=self.search, accelerator="Ctrl + S")
            self.has_added = True
        self.menubar.add_cascade(label="File", menu=self.file_menu)

    def create_vlc_instance(self):
        """ Creates a vlc instance and a vlc player instance """
        instance = vlc.Instance()
        player_instance = instance.media_player_new()
        self.update()
        return instance, player_instance

    def bind_keys(self):
        """ Bind shortcut keys """
        self.bind("<Control-o>", self.open)
        self.bind("<Control-s>", self.search)
        self.bind("<space>", self.play_pause)
        self.bind("<f>", self.fullscreen)
        self.bind("<Escape>", self.cancel_search)
        self.search_entry.bind("<Return>", self.start_thread)

    def unbind_keys(self):
        """ Unbind shortcut keys if it's fullscreen """
        if self.attributes("-fullscreen"): 
            self.unbind("<Control-o>")
            self.unbind("<Control-s>")
        self.unbind("<Escape>")

    def search(self, event=None):
        """ Draws a search panel next to the video control buttons """
        self.results = None
        self.results_button.pack_forget()
        self.search_status.pack(side=tk.LEFT)
        self.search_button.pack(side=tk.LEFT)
        self.search_entry.pack(side=tk.LEFT)
        self.search_dropdown.pack(side=tk.LEFT)
        self.search_entry.focus()
        self.unbind("<space>")
        self.unbind("<f>")

    def cancel_search(self, event=None):
        """ Removes the search panel """
        self.results = None
        self.search_status.pack_forget()
        self.search_button.pack_forget()
        self.search_entry.pack_forget()
        self.search_dropdown.pack_forget()
        self.results_button.pack_forget()
        self.search_entry.delete(0, tk.END)
        self.bind_keys()
        self.focus()
        
    def start_thread(self, event=None):
        """ Starts a subthread to search the query in the background
            to prevent the GUI from freezing or not responding
        """
        if self.results:
            vid_url = self.results["link"]
            media_title = self.results["title"]

            url_thread = threading.Thread(target=self.get_url, args=(vid_url, media_title))
            url_thread.daemon = True
            url_thread.start()

            self.cancel_search()
            self.search_status.config(text="Fetching...")
            self.search_status.pack(side=tk.LEFT)
            self.results = None
        else:
            query = self.search_entry.get()
            limit = self.num_of_result.get()
            if query and not query.isspace():
                search_thread = threading.Thread(target=self.get_results, args=(query, limit))
                search_thread.daemon = True
                search_thread.start()

                self.cancel_search()
                self.search_status.config(text="Searching...")
                self.search_status.pack(side=tk.LEFT)
            else:
                self.search()

    def get_results(self, query, limit):
        """ Uses the youtubesearchpython package to search Youtube """
        try:
            vid_result = ysp.VideosSearch(f"{query}", limit=limit)
            vid_info = vid_result.result()["result"]

            if limit == 1:
                self.results = vid_info[0]
                self.start_thread()
            else:
                self.results = vid_info
                self.search_status.config(text=f"{5*' '}")
                self.results_button.pack()
        except Exception:
            showerror("Youtube Error", "Cannot retrieve video URL")

    def list_results(self):
        """ Lists the results to a separate window """
        vid_titles = [result["title"] for result in self.results]
        
        top = tk.Toplevel()
        top.title("Search Results")

        x_pos = int((top.winfo_screenwidth()/2) - (500/2))
        y_pos = int((top.winfo_screenheight()/2) - (190/2))
        top.geometry(f"500x190+{x_pos}+{y_pos-35}")
        top.resizable(0, 0)

        list_box = tk.Listbox(top, width=80)
        for title in vid_titles:
            list_box.insert(tk.END, title)
        list_box.pack()

        def select_result():
            selected = list_box.curselection()
            if selected:
                self.results = self.results[selected[0]]
                top.destroy()
                self.start_thread()
        select_button = ttk.Button(top, text="Select", command=select_result)
        select_button.pack(side=tk.BOTTOM)

        list_box.focus()
        top.grab_set()
        top.mainloop()

    def get_url(self, vid_url, media_title):
        """ Uses the youtubesearchpython package to get the stream url """
        try:
            fetcher = ysp.StreamURLFetcher()
            video = ysp.Video.get(vid_url)
            streams = fetcher.getAll(video)

            stream_url = streams["streams"][0]["url"]
            self.search_status.config(text=f"{5*' '}")
            self.play_media(stream_url, media_title)
        except Exception:
            showerror("Youtube Error", "Cannot retrieve video URL")

    def open(self, event=None):
        """ Opens a media file from local storage """
        self.cancel_search()
        file = askopenfilename(title="Choose a media",
                            filetypes=(("mp4 files", "*.mp4"),
                                      ("mov files", "*.mov"),
                                      ("mp3 files", "*.mp3"),
                                      ("all files", "*.*")))
        if file:
            self.play_media(file, file.split("/")[-1])

    def handler(self):
        return self.video_panel.winfo_id()

    def play_pause(self, event=None):
        if self.vlc_player.get_media() and self.vlc_player.is_playing():
            self.vlc_player.pause()
            self.play_button.config(text="Play")
        elif self.vlc_player.get_media() and not self.vlc_player.is_playing():
            self.vlc_player.play()
            self.play_button.config(text="Pause")
        else:
            self.open()
        self.focus()

    def stop(self):
        """ Stops the vlc player """
        self.vlc_player.stop()
        self.vlc_player.set_media(None)
        self.timeSlider.set(0)
        self.timeSlider.configure(state="disable")
        self.play_button.config(text="Play")
        self.title("VLCTube")
        self.focus()

    def play_media(self, file, title):
        """ Plays a file from local storage or a stream url 
            using VLC
        """
        try:
            if self.vlc_player.get_media():
                self.stop()

            self.timeSlider.configure(state="active")
            self.title(f"VLCTube - {title}")
            media = self.vlc_instance.media_new(file)
            self.vlc_player.set_media(media)
            self.vlc_player.set_hwnd(self.handler())
            self.vlc_player.play()
            self.play_button.config(text="Pause")
            time.sleep(1.5)
        except Exception:
            showerror("Error", "Cannot open file")

    def fullscreen(self, event=None):
        screen_state = not self.attributes("-fullscreen") 
        if screen_state:
            self.attributes("-fullscreen", screen_state)
            self.hide_widgets()
            self.unbind_keys()
            self.bind("<Escape>", self.fullscreen)
        else:
            self.attributes("-fullscreen", screen_state)
            self.show_widgets()
            self.unbind_keys()
            self.bind_keys()
        self.focus()

    def hide_widgets(self):
        self.menubar.delete(0, tk.END)
        self.play_button.pack_forget()
        self.stop_button.pack_forget()
        self.volume_button.pack_forget()
        self.control_panel.pack_forget()
        self.timeSlider.pack_forget()
        self.timers.pack_forget()
        self.search_status.pack_forget()
        self.search_entry.pack_forget()
        self.search_button.pack_forget()

    def show_widgets(self):
        self.create_file_menu()
        self.play_button.pack(side=tk.LEFT)
        self.stop_button.pack(side=tk.LEFT)
        self.volume_button.pack(side=tk.LEFT)
        self.control_panel.pack(side=tk.BOTTOM)
        self.timeSlider.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.timers.pack(side=tk.BOTTOM, fill=tk.X)
        
    def time_slider(self, *args):
        if self.vlc_player:
            t = self.timeVar.get()
            if self.timeSliderLast != int(t):
                self.vlc_player.set_time(int(t * 1e3))  # milliseconds
                self.timeSliderUpdate = time.time()

    def tick(self):
        """ Timer tick, update the time slider to the video time """
        if self.vlc_player:
            # since the self.vlc_player.get_length may change while
            # playing, re-set the timeSlider to the correct range
            t = self.vlc_player.get_length() * 1e-3  # to seconds
            if t > 0:
                self.timeSlider.config(to=t)

                t = self.vlc_player.get_time() * 1e-3  # to seconds
                # don't change slider while user is messing with it
                if t > 0 and time.time() > (self.timeSliderUpdate + 2):
                    self.timeSlider.set(t)
                    self.timeSliderLast = int(self.timeVar.get())

                    if self.vlc_player.get_length()-self.vlc_player.get_time() < 350:
                        self.stop()
        # start the 1 second timer again
        self.after(1000, self.tick)

if __name__ == "__main__":
    root = VLCTube()
    root.mainloop()
