import time
from moviepy.editor import VideoFileClip
from customtkinter import *
from tkinter.filedialog import askopenfilenames
import tkinter.messagebox as msg
import os
import threading
from plyer import notification

class VideoConverter(CTk):
    def __init__(self):
        super().__init__()
        self.title("Video Converter - By Muhammad Hussain")
        self.geometry("750x520")
        self.configure(fg_color="#301142")
        self.resizable(False, False)
        self.wm_iconbitmap("assets/images/front.ico")

        self.outputPath = ""
        self.isFolder = False;

    def GuiTopTitle(self):
        title_frame = CTkFrame(master=self)
        title_frame.pack(pady=24)

        title_label = CTkLabel(master=title_frame, text="Video To Audio Converter", font=("Arial", 24, "bold"), fg_color="#172736")
        title_label.pack()

    def centerMain(self):
        self.main_frame = CTkFrame(master=self, border_color="violet", border_width=2, fg_color="#172736")
        self.main_frame.pack(fill=X)

        self.main_first_frame = CTkFrame(master=self.main_frame, width=170, fg_color="#172736")
        self.main_first_frame.pack(side=TOP, pady=7, padx=2, expand=True, fill=BOTH)

        self.main_first_frame_label = CTkLabel(master=self.main_first_frame, text="Converted Files", font=("sans serif", 24, "bold"), fg_color="#172736")
        self.main_first_frame_label.pack(side=LEFT, padx=178)

        self.main_second_frame = CTkFrame(master=self.main_frame)
        self.main_second_frame.pack(side=LEFT, pady=4, expand=True, fill=BOTH, padx=4)

        self.main_second_frame_listbox = CTkTextbox(master=self.main_second_frame, font=("Arial", 15, "bold"), fg_color="#1f0212")
        self.main_second_frame_listbox.pack(expand=True, fill=BOTH)


        self.main_third_frame = CTkFrame(master=self.main_frame, border_width=8, border_color="blue")
        self.main_third_frame.pack(pady=4, padx=7, fill=BOTH, expand=True)

        self.main_third_frame_button = CTkButton(master=self.main_third_frame, text="Browse...", fg_color="#190a5c", font=("Arial", 20, "bold"), hover_color="#0f0345", cursor="hand2", command=self.selectVideos)
        self.main_third_frame_button.pack(fill=BOTH, expand=True)

    def selectVideos(self):
        self.selected_videos = askopenfilenames(title="Select a Videos",
                                        filetypes=[("Videos", "*.mp4"), ("Videos", "*.mkv")])
        if self.selected_videos == "":
            pass
        else:
            self.start_button.configure(state=NORMAL)
            self.current_directory = os.path.dirname(self.selected_videos[0])
            for directory in os.listdir(self.current_directory):
                if directory == "Converted Files":
                    self.outputPath = self.current_directory+"/Converted Files"
                    self.isFolder = True
            if self.isFolder is False:
                self.create_directory = os.makedirs(self.current_directory+"/Converted Files")
                self.outputPath = self.current_directory+"/Converted Files"
            self.all_files = self.selected_videos
            self.total_video_label.configure(text=len(self.all_files))


    def lastFrame(self):
        self.last_frame = CTkFrame(master=self, border_color="red", border_width=2)
        self.last_frame.pack(fill=X, pady=4)

        self.last_frame_first_frame = CTkFrame(master=self.last_frame, border_color="orange", border_width=2)
        self.last_frame_first_frame.pack(side=LEFT, pady=4, padx=4)

        self.last_frame_third_frame_label = CTkLabel(master=self.last_frame_first_frame, text="Total Converted", font=("Arial", 19, "bold"), text_color="#ff59ec")
        self.last_frame_third_frame_label.pack(padx=10, pady=5)

        # Todo Later
        self.total_converted_video_label = CTkLabel(master=self.last_frame_first_frame, text="0", font=("Arial", 22, "bold"))
        self.total_converted_video_label.pack(pady=10)



        self.last_frame_second_frame = CTkFrame(master=self.last_frame, border_color="orange", border_width=2)
        self.last_frame_second_frame.pack(side=LEFT, pady=4, padx=4, fill=BOTH, expand=True)

        self.last_frame_second_frame_label = CTkLabel(self.last_frame_second_frame, text="Current Converting Video", font=("Arial", 18, "bold"), text_color="#4ae89e")
        self.last_frame_second_frame_label.pack(pady=2)


        self.last_second_frame_listbox = CTkTextbox(master=self.last_frame_second_frame, font=("Arial", 12, "bold"), height=0, corner_radius=2)
        self.last_second_frame_listbox.pack(fill=X, pady=8, padx=12)

        # Todo
        self.last_second_frame_listbox.configure(state=NORMAL)
        # function()
        self.last_second_frame_listbox.insert(1.0, "")
        self.last_second_frame_listbox.configure(state=DISABLED)

        self.last_frame_third_frame = CTkFrame(master=self.last_frame, border_color="orange", border_width=2)
        self.last_frame_third_frame.pack(side=LEFT, pady=4, padx=4, fill=Y)

        self.last_frame_third_frame_label = CTkLabel(master=self.last_frame_third_frame, text="Total Videos", font=("Arial", 19, "bold"), text_color="#ff59ec")
        self.last_frame_third_frame_label.pack(padx=10, pady=8)

        # Todo Later
        self.total_video_label = CTkLabel(master=self.last_frame_third_frame, text="0", font=("Arial", 22, "bold"))
        self.total_video_label.pack()

    def successNotification(self, total_videos):
        notification.notify(
            title='Video Converter',
            message=f'Your {total_videos} Videos are succesfully converted in mp3',
            app_icon="assets/images/front.ico",
            timeout=10,
        )

    def startButton(self):
        self.start_button_frame = CTkFrame(master=self, fg_color="#301142")
        self.start_button_frame.pack(fill=X, pady=1)

        self.start_button = CTkButton(master=self.start_button_frame, text="Start Converting", fg_color="#300985", font=("Arial", 20, "bold"), hover_color="#0f0345", cursor="hand2", height=65, width=240, corner_radius=10, command=self.threading, state=DISABLED)
        self.start_button.pack(pady=4, padx=8)

    def threading(self):
        conversion_thread = threading.Thread(target=self.startConverting)
        conversion_thread.start()

    def startConverting(self):
        self.total_converted_video_label.configure(text="0")
        # self.total_video_label.configure(text="0")
        self.last_second_frame_listbox.configure(state=NORMAL)
        self.last_second_frame_listbox.delete(1.0, END)
        self.last_second_frame_listbox.configure(state=DISABLED)

        self.main_second_frame_listbox.configure(state=NORMAL)
        self.main_second_frame_listbox.delete(1.0, END)
        self.main_second_frame_listbox.configure(state=DISABLED)

        self.start_button.configure(state=DISABLED)
        for index, videos in enumerate(self.all_files, start=1):
            audio_name = os.path.basename(videos).split(".")[0] + ".mp3"
            self.nameChanging(os.path.basename(videos))
            video_clip = VideoFileClip(videos)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(self.outputPath + "/" + audio_name)
            self.total_converted_video_label.configure(text=index)
            self.lastRunning(os.path.basename(videos))
        self.start_button.configure(state=NORMAL)
        self.last_second_frame_listbox.configure(state=NORMAL)
        self.last_second_frame_listbox.delete(1.0, END)
        self.last_second_frame_listbox.configure(state=DISABLED)
        self.successNotification(len(self.all_files))
    def nameChanging(self, videos):
        self.last_second_frame_listbox.configure(state=NORMAL)
        self.last_second_frame_listbox.delete(1.0, END)
        self.last_second_frame_listbox.insert(1.0, videos)
        self.last_second_frame_listbox.configure(state=DISABLED)

    def lastRunning(self, videos):
        self.main_second_frame_listbox.configure(state=NORMAL)
        self.main_second_frame_listbox.insert(END, f"{videos}\n")
        self.main_second_frame_listbox.configure(state=DISABLED)
        self.main_second_frame_listbox.see(END)

if __name__ == '__main__':
    try:
        window = VideoConverter()
        window.GuiTopTitle()
        window.centerMain()
        window.lastFrame()
        window.startButton()
        window.mainloop()
    except Exception as error:
        msg.showerror("Error", error)

