import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import fnmatch
import os
from pygame import mixer
from PIL import Image, ImageTk
import time


from tkinter import filedialog

# Ask user for their root music folder
root_path = filedialog.askdirectory(title="Select your Music Folder")

# If they cancel, fall back to default (like user's Music directory)
if not root_path:
    import os
    root_path = os.path.expanduser("~/Music")

print("Using root path:", root_path)













canvas = tk.Tk()
canvas.title("Personal Music Player")
canvas.geometry("800x900")
canvas.resizable(False, False)  # Make window non-resizable
canvas.config(bg='black')

rootpath = "/Users/iferdous001/Desktop/music"
pattern = "*.mp3"

mixer.init()

# Playlists storage
playlists = {}
current_playlist = []

# Music player state variables
current_position = 0
song_length = 0
is_playing = False
is_paused = False
position_var = tk.IntVar()
dragging_progress = False

# Load and setup animated GIF
def load_gif(path):
    gif = Image.open(path)
    frames = []
    try:
        while True:
            frames.append(ImageTk.PhotoImage(gif.copy().resize((800, 900), Image.Resampling.LANCZOS)))
            gif.seek(len(frames))
    except EOFError:
        pass
    return frames

def animate_gif(frame_index=0):
    if gif_frames:
        bg_label.config(image=gif_frames[frame_index])
        canvas.after(100, animate_gif, (frame_index + 1) % len(gif_frames))

try:
    gif_frames = load_gif('glow.gif')
except:
    gif_frames = []

bg_label = tk.Label(canvas, bg='black')
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

if gif_frames:
    animate_gif()

prev_img = tk.PhotoImage(file='prev_img.png')
stop_img = tk.PhotoImage(file='stop_img.png')
play_img = tk.PhotoImage(file='play_img.png')
pause_img = tk.PhotoImage(file='pause_img.png')
next_img = tk.PhotoImage(file='next_img.png')

# Hover effects
def on_enter(button):
    button.config(bg='#333333')

def on_leave(button):
    button.config(bg='black')

def select():
    global is_playing, is_paused, song_length, current_position
    if listBox.curselection():
        selected_song = listBox.get(listBox.curselection())
        label.config(text=selected_song)
        song_path = os.path.join(rootpath, selected_song)
        mixer.music.load(song_path)
        mixer.music.play()
        is_playing = True
        is_paused = False
        current_position = 0

        try:
            import mutagen
            audio_file = mutagen.File(song_path)
            if audio_file:
                song_length = int(audio_file.info.length)
            else:
                song_length = 180
        except:
            song_length = 180

        progress_scale.config(to=song_length)

def stop():
    global is_playing, is_paused, current_position
    mixer.music.stop()
    listBox.select_clear('active')
    is_playing = False
    is_paused = False
    current_position = 0
    position_var.set(0)
    time_label.config(text="00:00 / 00:00")

def play_next():
    global is_playing, is_paused, song_length, current_position
    if listBox.curselection():
        current_index = listBox.curselection()[0]
        if current_index < listBox.size() - 1:
            next_song = current_index + 1
            next_song_name = listBox.get(next_song)
            label.config(text=next_song_name)
            song_path = os.path.join(rootpath, next_song_name)
            mixer.music.load(song_path)
            mixer.music.play()
            listBox.select_clear(0, 'end')
            listBox.activate(next_song)
            listBox.select_set(next_song)

            is_playing = True
            is_paused = False
            current_position = 0

            try:
                import mutagen
                audio_file = mutagen.File(song_path)
                if audio_file:
                    song_length = int(audio_file.info.length)
                else:
                    song_length = 180
            except:
                song_length = 180

            progress_scale.config(to=song_length)

def play_prev():
    global is_playing, is_paused, song_length, current_position
    if listBox.curselection():
        current_index = listBox.curselection()[0]
        if current_index > 0:
            prev_song = current_index - 1
            prev_song_name = listBox.get(prev_song)
            label.config(text=prev_song_name)
            song_path = os.path.join(rootpath, prev_song_name)
            mixer.music.load(song_path)
            mixer.music.play()
            listBox.select_clear(0, 'end')
            listBox.activate(prev_song)
            listBox.select_set(prev_song)

            is_playing = True
            is_paused = False
            current_position = 0

            try:
                import mutagen
                audio_file = mutagen.File(song_path)
                if audio_file:
                    song_length = int(audio_file.info.length)
                else:
                    song_length = 180
            except:
                song_length = 180

            progress_scale.config(to=song_length)

def pause_song():
    global is_playing, is_paused
    if pauseButton["text"] == "Pause":
        mixer.music.pause()
        pauseButton["text"] = "Play"
        is_paused = True
        is_playing = False
    else:
        mixer.music.unpause()
        pauseButton["text"] = "Pause"
        is_paused = False
        is_playing = True

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def update_progress():
    global current_position, is_playing, is_paused, dragging_progress, song_length
    if is_playing and not is_paused and not dragging_progress:
        if mixer.music.get_busy():
            current_position += 1
            if current_position <= song_length:
                position_var.set(current_position)
                current_time = format_time(current_position)
                total_time = format_time(song_length)
                time_label.config(text=f"{current_time} / {total_time}")
            else:
                is_playing = False
                current_position = 0
                position_var.set(0)
                time_label.config(text="00:00 / 00:00")
        else:
            is_playing = False
    canvas.after(1000, update_progress)

def on_progress_drag(event):
    global dragging_progress
    dragging_progress = True

def on_progress_release(event):
    global dragging_progress, current_position
    dragging_progress = False
    new_position = position_var.get()
    current_position = new_position
    current_time = format_time(current_position)
    total_time = format_time(song_length)
    time_label.config(text=f"{current_time} / {total_time}")

def update_clock():
    current_time = time.strftime("%I:%M:%S %p")
    clock_label.config(text=current_time)
    canvas.after(1000, update_clock)

def update_bass(val):
    bass_label.config(text=f"Bass: {val}")

def update_treble(val):
    treble_label.config(text=f"Treble: {val}")

def update_volume(val):
    mixer.music.set_volume(float(val) / 100)
    volume_label.config(text=f"Volume: {val}")

def create_playlist():
    name = simpledialog.askstring("Create Playlist", "Enter playlist name:")
    if name:
        playlists[name] = []
        playlist_combo['values'] = list(playlists.keys())
        messagebox.showinfo("Success", f"Playlist '{name}' created!")

def add_to_playlist():
    if listBox.curselection() and playlist_combo.get():
        selected_song = listBox.get(listBox.curselection())
        playlist_name = playlist_combo.get()
        if playlist_name in playlists:
            if selected_song not in playlists[playlist_name]:
                playlists[playlist_name].append(selected_song)
                messagebox.showinfo("Success", f"Added '{selected_song}' to '{playlist_name}'")
            else:
                messagebox.showwarning("Warning", "Song already in playlist!")

def load_playlist():
    playlist_name = playlist_combo.get()
    if playlist_name in playlists:
        listBox.delete(0, 'end')
        for song in playlists[playlist_name]:
            listBox.insert('end', song)
        messagebox.showinfo("Success", f"Loaded playlist '{playlist_name}'")

def load_all_songs():
    listBox.delete(0, 'end')
    for root, dirs, files in os.walk(rootpath):
        for filename in fnmatch.filter(files, pattern):
            listBox.insert('end', filename)

# Clock
clock_label = tk.Label(canvas, text="", fg='white', font=('ds-digital', 18), bg='black')
clock_label.pack(pady=(10, 10))

# Song list
listBox = tk.Listbox(canvas, fg="cyan", bg="black", width=100, font=('poppins', 14),
                     selectbackground="#444444", selectforeground="cyan",
                     highlightbackground="cyan", highlightcolor="cyan",
                     highlightthickness=2, relief='flat', bd=0)
listBox.pack(padx=20, pady=(5, 20))

# Now playing
label = tk.Label(canvas, text='No song selected', fg='yellow',
                 font=('ds-digital', 16), wraplength=600, bg='black')
label.pack(pady=10)

# Time display
time_label = tk.Label(canvas, text='00:00 / 00:00', fg='cyan',
                      font=('ds-digital', 14), bg='black')
time_label.pack(pady=10)

# Progress bar
progress_frame = tk.Frame(canvas, bg='black')
progress_frame.pack(pady=10, padx=40, fill='x')

progress_scale = tk.Scale(progress_frame, from_=0, to=100, orient='horizontal',
                         variable=position_var, length=720, sliderlength=20,
                         fg='cyan', bg='black', highlightbackground='black',
                         troughcolor='#333333', activebackground='cyan',
                         bd=0, highlightthickness=0, showvalue=0)
progress_scale.pack(fill='x')
progress_scale.bind("<Button-1>", on_progress_drag)
progress_scale.bind("<ButtonRelease-1>", on_progress_release)

# Control buttons
control_frame = tk.Frame(canvas, bg='black')
control_frame.pack(pady=20)

prevButton = tk.Button(control_frame, image=prev_img, bg='black', borderwidth=0,
                       relief='flat', activebackground='#333333', command=play_prev)
prevButton.pack(side='left', padx=10)

stopButton = tk.Button(control_frame, image=stop_img, bg='black', borderwidth=0,
                       relief='flat', activebackground='#333333', command=stop)
stopButton.pack(side='left', padx=10)

playButton = tk.Button(control_frame, image=play_img, bg='black', borderwidth=0,
                       relief='flat', activebackground='#333333', command=select)
playButton.pack(side='left', padx=10)

pauseButton = tk.Button(control_frame, image=pause_img, bg='black', borderwidth=0,
                        relief='flat', activebackground='#333333', command=pause_song)
pauseButton.pack(side='left', padx=10)

nextButton = tk.Button(control_frame, image=next_img, bg='black', borderwidth=0,
                       relief='flat', activebackground='#333333', command=play_next)
nextButton.pack(side='left', padx=10)

# Equalizer (shifted left & spaced out)
eq_title = tk.Label(canvas, text="Equalizer", fg='red', font=('poppins', 12, 'bold'))
eq_title.place(x=20, y=500)

bass_label = tk.Label(canvas, text="Bass: 50", fg='red', font=('poppins', 10))
bass_label.place(x=20, y=530)
bass_scale = tk.Scale(canvas, from_=0, to=100, orient='horizontal', fg='red',
                      highlightbackground='black', command=update_bass,
                      troughcolor='#333333', activebackground='red', length=150,
                      bd=0, highlightthickness=0)
bass_scale.set(50)
bass_scale.place(x=20, y=550)

treble_label = tk.Label(canvas, text="Treble: 50", fg='red', font=('poppins', 10))
treble_label.place(x=220, y=530)
treble_scale = tk.Scale(canvas, from_=0, to=100, orient='horizontal', fg='red',
                        highlightbackground='black', command=update_treble,
                        troughcolor='#333333', activebackground='red', length=150,
                        bd=0, highlightthickness=0)
treble_scale.set(50)
treble_scale.place(x=220, y=550)

volume_label = tk.Label(canvas, text="Volume: 70", fg='red', font=('poppins', 10))
volume_label.place(x=420, y=530)
volume_scale = tk.Scale(canvas, from_=0, to=100, orient='horizontal', fg='red',
                        highlightbackground='black', command=update_volume,
                        troughcolor='#333333', activebackground='red', length=150,
                        bd=0, highlightthickness=0)
volume_scale.set(70)
volume_scale.place(x=420, y=550)

# Playlists (shifted left & spaced down)
playlist_title = tk.Label(canvas, text="Playlists", fg='red', font=('poppins', 12, 'bold'))
playlist_title.place(x=20, y=630)

playlist_controls = tk.Frame(canvas)
playlist_controls.place(x=20, y=660)

playlist_combo = ttk.Combobox(playlist_controls, values=list(playlists.keys()),
                              font=('poppins', 12), width=20)
playlist_combo.pack(side='left', padx=8)

create_btn = tk.Button(playlist_controls, text="Create Playlist", bg='#333333', fg='red',
                       font=('poppins', 12), relief='flat', command=create_playlist,
                       width=12, height=1)
create_btn.pack(side='left', padx=8)

add_btn = tk.Button(playlist_controls, text="Add to Playlist", bg='#333333', fg='red',
                    font=('poppins', 12), relief='flat', command=add_to_playlist,
                    width=12, height=1)
add_btn.pack(side='left', padx=8)

load_btn = tk.Button(playlist_controls, text="Load Playlist", bg='#333333', fg='red',
                     font=('poppins', 12), relief='flat', command=load_playlist,
                     width=12, height=1)
load_btn.pack(side='left', padx=8)

all_songs_btn = tk.Button(playlist_controls, text="All Songs", bg='#333333', fg='red',
                          font=('poppins', 12), relief='flat', command=load_all_songs,
                          width=12, height=1)
all_songs_btn.pack(side='left', padx=8)

# Load all songs initially
for root, dirs, files in os.walk(rootpath):
    for filename in fnmatch.filter(files, pattern):
        listBox.insert('end', filename)

update_clock()
update_progress()

canvas.mainloop()