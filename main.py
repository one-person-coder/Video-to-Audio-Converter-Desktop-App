import time
import os
import threading
from tkinter.filedialog import askopenfilenames
import tkinter.messagebox as msg
from customtkinter import *
import webbrowser
import sys

# --- Import Error Handling ---
try:
  from moviepy import VideoFileClip
except ImportError:
  msg.showerror("Import Error", "MoviePy library not found. Please run 'pip install moviepy'.")
  sys.exit(1)

try:
  from plyer import notification
  PLYER_AVAILABLE = True
except ImportError:
  # print("Plyer library not found. Notifications will not work.")
  PLYER_AVAILABLE = False
  notification = None


class VideoConverter(CTk):
  """
  Professional Video to Audio Converter with modern minimalist design.
  """

  OUTPUT_FOLDER_NAME = "Converted Audio"

  # Updated Sophisticated Color Palette
  COLORS = {
      "bg_primary": "#f5f7fa",        # Soft light gray background
      "bg_secondary": "#ffffff",      # White for sections/cards
      "bg_card": "#ffffff",           # White cards with subtle shadows
      "accent": "#3b82f6",            # Modern vibrant blue
      "accent_hover": "#2563eb",      # Slightly darker blue on hover
      "accent_light": "#93c5fd",      # Light blue for highlights
      "success": "#16a34a",           # Fresh green
      "success_hover": "#15803d",
      "warning": "#f59e0b",           # Amber/yellow
      "error": "#dc2626",             # Bright red
      "text_primary": "#111827",      # Dark gray/almost black
      "text_secondary": "#6b7280",    # Medium gray
      "text_light": "#9ca3af",        # Light gray
      "border": "#e5e7eb",            # Soft border gray
      "border_light": "#f3f4f6",      # Very subtle border
      "shadow": "rgba(0, 0, 0, 0.08)",  # Soft shadow
      "hover": "#f3f4f6",             # Light hover background
      "progress": "#3b82f6",          # Matches accent
      "disabled": "#d1d5db",          # Gray for disabled elements
      "button_text": "#ffffff"        # White button text
  }

  def __init__(self):
    super().__init__()

    # Configure window
    self.title("Video to Audio Converter")
    self.geometry("1050x850")
    self.configure(fg_color=self.COLORS["bg_primary"])
    self.resizable(True, True)
    self.minsize(1024, 758)
    self.wm_iconbitmap("assets/images/logo.ico")

    # Center window on screen
    self.update_idletasks()
    width = 1050
    height = 850
    x = (self.winfo_screenwidth() // 2) - (width // 2)
    y = (self.winfo_screenheight() // 2) - (height // 2)
    self.geometry(f'{width}x{height}+{x}+{y}')

    # Apply modern theme
    set_appearance_mode("light")
    set_default_color_theme("blue")

    # Initializing instance variables
    self.output_path = ""
    self.selected_videos = []
    self.total_videos_count = 0
    self.converted_count = 0
    self.failed_count = 0
    self.is_converting = False
    self.conversion_thread = None
    self.file_status_labels = []
    self.empty_state_frame = None  # To manage the empty state visibility

    # Dictionary to store UI components
    self.widgets = {}

    # GUI Setup
    self._setup_gui()

    # Bind window close event
    self.protocol("WM_DELETE_WINDOW", self._on_closing)

  def _setup_gui(self):
    """Sets up all the main components of the GUI."""
    # Main container with padding
    main_container = CTkFrame(master=self,
                              fg_color=self.COLORS["bg_primary"],
                              corner_radius=0)
    main_container.pack(fill=BOTH, expand=True, padx=0, pady=0)

    self._create_header(main_container)
    self._create_main_content(main_container)
    self._create_progress_section(main_container)
    self._create_action_buttons(main_container)
    self._create_footer(main_container)

  def _create_header(self, parent):
    """Creates the minimalist header and CENTERS the content."""
    header_frame = CTkFrame(master=parent,
                            fg_color=self.COLORS["bg_primary"],
                            height=90,
                            corner_radius=0,
                            border_width=0)
    header_frame.pack(fill=X, pady=0)
    header_frame.pack_propagate(False)

    # Main title container with fixed width to center properly
    # Using grid for simple centering
    header_frame.grid_columnconfigure(0, weight=1)

    # Center the main title container
    title_container = CTkFrame(master=header_frame,
                               fg_color="transparent")
    title_container.grid(row=0, column=0, pady=25, sticky="n")  # Centered vertically and horizontally

    # Icon and title with better spacing
    icon_title_frame = CTkFrame(master=title_container,
                                fg_color="transparent")
    icon_title_frame.pack(side=LEFT)

    CTkLabel(master=icon_title_frame,
             text="🎼",
             font=("Segoe UI", 26),
             text_color=self.COLORS["accent"]).pack(side=LEFT, padx=(0, 15))

    # Main title
    title_frame = CTkFrame(master=icon_title_frame,
                           fg_color="transparent")
    title_frame.pack(side=LEFT)

    CTkLabel(master=title_frame,
             text="Video to Audio Converter",
             font=("Segoe UI Semibold", 24),
             text_color=self.COLORS["text_primary"]).pack(anchor="w")

    # Subtitle (FIXED: Added wraplength to prevent cutting)
    CTkLabel(master=title_frame,
             text="Convert videos to high-quality MP3 format quickly",
             font=("Segoe UI", 13),
             text_color=self.COLORS["text_secondary"],
             wraplength=350).pack(anchor="w", pady=(4, 0))  # Wraplength added here

  def _create_main_content(self, parent):
    """Creates the main content area."""
    main_frame = CTkFrame(master=parent,
                          fg_color=self.COLORS["bg_primary"])
    main_frame.pack(fill=BOTH, expand=True, padx=50, pady=(10, 20))

    # Two column layout with proper spacing
    columns_frame = CTkFrame(master=main_frame,
                             fg_color="transparent")
    columns_frame.pack(fill=BOTH, expand=True)

    # Left column - File selection (fixed width)
    left_column = CTkFrame(master=columns_frame,
                           fg_color="transparent",
                           width=380)
    left_column.pack(side=LEFT, fill=Y)
    left_column.pack_propagate(False)

    self._create_file_selection_panel(left_column)

    # Vertical separator with better styling
    separator = CTkFrame(master=columns_frame,
                         fg_color=self.COLORS["border"],
                         width=1)
    separator.pack(side=LEFT, fill=Y, padx=40)

    # Right column - File list (takes remaining space)
    right_column = CTkFrame(master=columns_frame,
                            fg_color="transparent")
    right_column.pack(side=RIGHT, fill=BOTH, expand=True)

    self._create_file_list_panel(right_column)

  def _create_file_selection_panel(self, parent):
    """Creates the file selection panel with better padding and output button."""
    CTkLabel(master=parent,
             text="File Selection",
             font=("Segoe UI Semibold", 18),
             text_color=self.COLORS["text_primary"]).pack(anchor="w", pady=(0, 25))

    browse_btn = CTkButton(master=parent,
                           text="📁 Select Video Files",
                           font=("Segoe UI", 14, "bold"),
                           fg_color=self.COLORS["accent"],
                           hover_color=self.COLORS["accent_hover"],
                           text_color=self.COLORS["button_text"],
                           height=52,
                           corner_radius=8,
                           border_width=0,
                           command=self._select_videos)
    browse_btn.pack(fill=X, pady=(0, 30))

    # Supported formats card
    formats_card = CTkFrame(master=parent,
                            fg_color=self.COLORS["bg_secondary"],
                            corner_radius=10,
                            border_width=1,
                            border_color=self.COLORS["border"])
    formats_card.pack(fill=X, pady=(0, 30))

    # Card header
    CTkLabel(master=formats_card,
             text="Supported Formats",
             font=("Segoe UI Semibold", 13),
             text_color=self.COLORS["text_primary"]).pack(anchor="w", padx=20, pady=(18, 10))

    # FIX: Making the format list scrollable
    scrollable_formats_frame = CTkScrollableFrame(master=formats_card,
                                                  fg_color="transparent",
                                                  height=150,  # Fixed height for the scrollable area
                                                  corner_radius=0)
    scrollable_formats_frame.pack(fill=X, padx=0, pady=0)

    # Format list
    formats = [
        ("MP4", ".mp4 files"), ("MKV", ".mkv files"), ("AVI", ".avi files"),
        ("MOV", ".mov files"), ("WMV", ".wmv files"), ("FLV", ".flv files"),
        ("WebM", ".webm files"), ("OGG", ".ogg files"), ("3GP", ".3gp files"),
        ("TS", ".ts files"), ("VOB", ".vob files")  # Added more for scrolling demo
    ]

    for fmt_name, fmt_desc in formats:
      fmt_frame = CTkFrame(master=scrollable_formats_frame, fg_color="transparent")
      fmt_frame.pack(fill=X, padx=20, pady=2)
      CTkLabel(master=fmt_frame, text=f"• {fmt_name}", font=("Segoe UI", 12),
               text_color=self.COLORS["text_primary"]).pack(side=LEFT)
      CTkLabel(master=fmt_frame, text=fmt_desc, font=("Segoe UI", 11),
               text_color=self.COLORS["text_secondary"]).pack(side=RIGHT)

    # Output format
    output_frame = CTkFrame(master=formats_card,
                            fg_color=self.COLORS["accent"],
                            corner_radius=6)
    output_frame.pack(fill=X, padx=20, pady=(15, 18))

    CTkLabel(master=output_frame,
             text="Output: MP3 (High Quality Audio)",
             font=("Segoe UI", 12, "bold"),
             text_color="white").pack(pady=10)

    # Stats section
    stats_frame = CTkFrame(master=parent, fg_color="transparent")
    stats_frame.pack(fill=X, pady=(10, 0))

    # Files count card
    count_card = CTkFrame(master=stats_frame, fg_color=self.COLORS["bg_secondary"],
                          corner_radius=10, height=100, border_width=1,
                          border_color=self.COLORS["border"])
    count_card.pack(fill=X, pady=(0, 15))
    count_card.pack_propagate(False)

    CTkLabel(master=count_card, text="Selected Files", font=("Segoe UI", 12),
             text_color=self.COLORS["text_secondary"]).pack(anchor="w", padx=25, pady=(22, 5))

    self.widgets['file_count_label'] = CTkLabel(master=count_card, text="0",
                                                font=("Segoe UI Semibold", 28),
                                                text_color=self.COLORS["accent"])
    self.widgets['file_count_label'].pack(anchor="w", padx=25, pady=(0, 22))

    # Output location card
    output_card = CTkFrame(master=stats_frame, fg_color=self.COLORS["bg_secondary"],
                           corner_radius=10, height=120, border_width=1,
                           border_color=self.COLORS["border"])
    output_card.pack(fill=X)
    output_card.pack_propagate(False)

    output_card_top = CTkFrame(master=output_card, fg_color="transparent")
    output_card_top.pack(fill=X, padx=25, pady=(22, 8))

    CTkLabel(master=output_card_top, text="Output Location", font=("Segoe UI", 12),
             text_color=self.COLORS["text_secondary"]).pack(side=LEFT)

    # Open Folder Button
    self.widgets['open_folder_button'] = CTkButton(master=output_card_top,
                                                   text="📂 Open Folder",
                                                   font=("Segoe UI", 10),
                                                   fg_color=self.COLORS["accent_light"],
                                                   hover_color=self.COLORS["accent"],
                                                   text_color="white",
                                                   width=110,
                                                   height=28,
                                                   corner_radius=6,
                                                   command=self._open_output_folder,
                                                   state=DISABLED)
    self.widgets['open_folder_button'].pack(side=RIGHT)

    # Output path label
    self.widgets['output_path_label'] = CTkLabel(master=output_card,
                                                 text="No folder selected",
                                                 font=("Segoe UI", 11),
                                                 text_color=self.COLORS["text_secondary"],
                                                 wraplength=320,
                                                 justify="left")
    self.widgets['output_path_label'].pack(anchor="w", padx=25, pady=(0, 22), fill=X)

  def _create_file_list_panel(self, parent):
    """Creates the file list panel with better styling."""
    # Panel header with actions
    header_frame = CTkFrame(master=parent,
                            fg_color="transparent")
    header_frame.pack(fill=X, pady=(0, 20))

    CTkLabel(master=header_frame,
             text="Conversion Queue",
             font=("Segoe UI Semibold", 18),
             text_color=self.COLORS["text_primary"]).pack(side=LEFT)

    # Clear button with better styling
    clear_btn = CTkButton(master=header_frame,
                          text="🗑️ Clear All",
                          font=("Segoe UI", 12),
                          fg_color=self.COLORS["bg_secondary"],
                          hover_color=self.COLORS["hover"],
                          text_color=self.COLORS["text_secondary"],
                          border_color=self.COLORS["border"],
                          border_width=1,
                          width=110,
                          height=36,
                          corner_radius=6,
                          command=self._clear_list)
    clear_btn.pack(side=RIGHT)

    # File list container with shadow effect
    list_container = CTkFrame(master=parent,
                              fg_color=self.COLORS["bg_secondary"],
                              corner_radius=12,
                              border_width=1,
                              border_color=self.COLORS["border"])
    list_container.pack(fill=BOTH, expand=True)

    # Scrollable list frame
    self.widgets['list_frame'] = CTkScrollableFrame(master=list_container,
                                                    fg_color="transparent",  # Changed to transparent for better look
                                                    corner_radius=12)
    self.widgets['list_frame'].pack(fill=BOTH, expand=True, padx=2, pady=2)

    # Empty state
    self._show_empty_state()

  def _show_empty_state(self):
    """Shows empty state in file list, if not already shown."""
    # Only show if not already present or if children exist (shouldn't happen)
    if not self.widgets['list_frame'].winfo_children():
      self.empty_state_frame = CTkFrame(master=self.widgets['list_frame'],
                                        fg_color="transparent")
      self.empty_state_frame.pack(expand=True, pady=120)

      CTkLabel(master=self.empty_state_frame,
               text="📂",
               font=("Segoe UI", 56),
               text_color=self.COLORS["text_light"]).pack()

      CTkLabel(master=self.empty_state_frame,
               text="No files selected",
               font=("Segoe UI Semibold", 16),
               text_color=self.COLORS["text_secondary"]).pack(pady=15)

      CTkLabel(master=self.empty_state_frame,
               text="Select video files to begin conversion",
               font=("Segoe UI", 13),
               text_color=self.COLORS["text_light"]).pack()

  def _hide_empty_state(self):
    """Hides the empty state frame."""
    if self.empty_state_frame:
      self.empty_state_frame.destroy()
      self.empty_state_frame = None

  def _create_progress_section(self, parent):
    """Creates the progress section with better layout."""
    progress_frame = CTkFrame(master=parent,
                              fg_color=self.COLORS["bg_secondary"],
                              corner_radius=12,
                              height=200,
                              border_width=1,
                              border_color=self.COLORS["border"])
    progress_frame.pack(fill=X, padx=50, pady=(0, 25))
    progress_frame.pack_propagate(False)

    # Status section
    status_section = CTkFrame(master=progress_frame,
                              fg_color="transparent")
    status_section.pack(fill=X, padx=30, pady=(28, 20))

    # Status label
    CTkLabel(master=status_section,
             text="Status",
             font=("Segoe UI Semibold", 15),
             text_color=self.COLORS["text_primary"]).pack(side=LEFT)

    self.widgets['status_label'] = CTkLabel(master=status_section,
                                            text="Ready",
                                            font=("Segoe UI", 13, "bold"),
                                            text_color=self.COLORS["success"])
    self.widgets['status_label'].pack(side=RIGHT)

    # Current file display
    current_file_container = CTkFrame(master=progress_frame,
                                      fg_color=self.COLORS["bg_primary"],
                                      corner_radius=8,
                                      border_width=1,
                                      border_color=self.COLORS["border"])
    current_file_container.pack(fill=X, padx=30, pady=(0, 25))

    CTkLabel(master=current_file_container,
             text="Current file:",
             font=("Segoe UI", 12),
             text_color=self.COLORS["text_secondary"]).pack(anchor="w", padx=18, pady=(14, 5))

    self.widgets['current_file_label'] = CTkLabel(master=current_file_container,
                                                  text="No file selected",
                                                  font=("Segoe UI", 13),
                                                  text_color=self.COLORS["text_primary"],
                                                  wraplength=700)
    self.widgets['current_file_label'].pack(anchor="w", padx=18, pady=(0, 14))

    # Progress bar section
    progress_section = CTkFrame(master=progress_frame,
                                fg_color="transparent")
    progress_section.pack(fill=X, padx=30, pady=(0, 30))

    # Progress info row
    progress_info = CTkFrame(master=progress_section,
                             fg_color="transparent")
    progress_info.pack(fill=X, pady=(0, 12))

    CTkLabel(master=progress_info,
             text="Overall Progress",
             font=("Segoe UI", 13),
             text_color=self.COLORS["text_secondary"]).pack(side=LEFT)

    self.widgets['progress_percentage'] = CTkLabel(master=progress_info,
                                                   text="0/0 (0%)",
                                                   font=("Segoe UI Semibold", 14),
                                                   text_color=self.COLORS["accent"])
    self.widgets['progress_percentage'].pack(side=RIGHT)

    # Progress bar
    self.widgets['progress_bar'] = CTkProgressBar(master=progress_section,
                                                  fg_color=self.COLORS["border"],
                                                  progress_color=self.COLORS["progress"],
                                                  height=8,
                                                  corner_radius=4)
    self.widgets['progress_bar'].pack(fill=X)
    self.widgets['progress_bar'].set(0)

  def _create_action_buttons(self, parent):
    """Creates the action buttons with better styling."""
    button_frame = CTkFrame(master=parent,
                            fg_color="transparent")
    button_frame.pack(fill=X, padx=50, pady=(0, 30))

    # Start button - Primary action button
    self.widgets['start_button'] = CTkButton(master=button_frame,
                                             text="▶️ Start Conversion",
                                             font=("Segoe UI Semibold", 15),
                                             fg_color=self.COLORS["success"],
                                             hover_color=self.COLORS["success_hover"],
                                             text_color="white",
                                             height=56,
                                             corner_radius=8,
                                             border_width=0,
                                             command=self._start_conversion_thread,
                                             state=DISABLED)
    self.widgets['start_button'].pack(side=LEFT, fill=X, expand=True, padx=(0, 12))

    # Stop button - Secondary action button
    self.widgets['stop_button'] = CTkButton(master=button_frame,
                                            text="⏹ Stop Conversion",
                                            font=("Segoe UI", 14),
                                            fg_color=self.COLORS["bg_secondary"],
                                            hover_color=self.COLORS["hover"],
                                            text_color=self.COLORS["text_secondary"],
                                            height=56,
                                            corner_radius=8,
                                            border_width=1,
                                            border_color=self.COLORS["border"],
                                            command=self._stop_conversion,
                                            state=DISABLED)
    self.widgets['stop_button'].pack(side=RIGHT, fill=X, expand=True, padx=(12, 0))

  def _create_footer(self, parent):
    """Creates the footer with better portfolio button visibility."""
    footer_frame = CTkFrame(master=parent,
                            fg_color=self.COLORS["bg_primary"],
                            height=70,
                            corner_radius=0,
                            border_width=1,
                            border_color=self.COLORS["border_light"])
    footer_frame.pack(fill=X, side=BOTTOM)
    footer_frame.pack_propagate(False)

    footer_content = CTkFrame(master=footer_frame,
                              fg_color="transparent")
    footer_content.pack(expand=True, fill=BOTH, padx=50)

    # Left section - Copyright
    left_section = CTkFrame(master=footer_content,
                            fg_color="transparent")
    left_section.pack(side=LEFT, fill=Y, pady=20)

    CTkLabel(master=left_section,
             text="Developed by",
             font=("Segoe UI", 12),
             text_color=self.COLORS["text_secondary"]).pack(side=LEFT)

    # Separator
    CTkLabel(master=left_section,
             text="•",
             font=("Segoe UI", 12),
             text_color=self.COLORS["text_light"],
             padx=8).pack(side=LEFT)

    CTkLabel(master=left_section,
             text="HussainCoder",
             font=("Segoe UI", 12),
             text_color=self.COLORS["text_primary"]).pack(side=LEFT)

    # Right section - Portfolio button (MORE VISIBLE)
    right_section = CTkFrame(master=footer_content,
                             fg_color="transparent")
    right_section.pack(side=RIGHT, fill=Y, pady=20)

    # Portfolio button with better visibility
    portfolio_btn = CTkButton(master=right_section,
                              text="👨‍💻 Portfolio",
                              font=("Segoe UI Semibold", 13),
                              fg_color=self.COLORS["accent"],
                              hover_color=self.COLORS["accent_hover"],
                              text_color="white",
                              height=40,
                              width=140,
                              corner_radius=20,
                              border_width=0,
                              command=self._open_portfolio)
    portfolio_btn.pack(side=RIGHT)

    # Version info next to portfolio button
    CTkLabel(master=right_section,
             text="v1.3 (Optimized)",  # Updated version number
             font=("Segoe UI", 11),
             text_color=self.COLORS["text_light"],
             padx=15).pack(side=RIGHT, pady=10)

  # --- Core Logic and Utility Functions ---

  def _open_portfolio(self):
    """Opens the portfolio website."""
    try:
      webbrowser.open("https://hussaincoder.dev")
      self.widgets['status_label'].configure(
          text="Portfolio opened",
          text_color=self.COLORS["accent"])
    except Exception as e:
      msg.showerror("Error", f"Could not open portfolio: {e}")

  def _open_output_folder(self):
    """Opens the output folder in the system file explorer."""
    if not self.output_path:
      return

    try:
      if os.path.isdir(self.output_path):
        webbrowser.open(self.output_path)
      else:
        msg.showwarning("Warning", "Output folder does not exist yet.")
    except Exception as e:
      msg.showerror("Error", f"Could not open folder: {e}")

  def _on_closing(self):
    """Handles window closing."""
    if self.is_converting:
      if msg.askyesno("Confirm", "Conversion is in progress. Are you sure you want to exit?"):
        self.is_converting = False
        self.destroy()
    else:
      self.destroy()

  def _clear_list(self):
    """Clears the file list and resets UI."""
    if self.is_converting:
      msg.showwarning("Warning", "Please stop conversion first!")
      return

    self.selected_videos = []
    self.total_videos_count = 0
    self.converted_count = 0
    self.failed_count = 0
    self.file_status_labels.clear()

    # Clear list frame
    for widget in self.widgets['list_frame'].winfo_children():
      widget.destroy()

    # Show empty state
    self._show_empty_state()

    # Reset UI
    self.widgets['file_count_label'].configure(text="0")
    self.widgets['output_path_label'].configure(text="No folder selected")
    self.widgets['start_button'].configure(state=DISABLED)
    self.widgets['open_folder_button'].configure(state=DISABLED)
    self.widgets['status_label'].configure(text="Ready", text_color=self.COLORS["success"])
    self.widgets['current_file_label'].configure(text="No file selected")
    self.widgets['progress_bar'].set(0)
    self.widgets['progress_percentage'].configure(text="0/0 (0%)")

  def _select_videos(self):
    """Opens file dialog to select videos and updates the list."""
    files = askopenfilenames(
        title="Select Video Files",
        filetypes=[
            ("Video Files", "*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm *.ogg *.3gp *.ts *.vob"),
            ("All Files", "*.*")
        ]
    )

    if files:
      self.selected_videos = list(files)
      self.total_videos_count = len(files)
      self.converted_count = 0
      self.failed_count = 0

      # Set output path
      first_video_dir = os.path.dirname(self.selected_videos[0])
      self.output_path = os.path.join(first_video_dir, self.OUTPUT_FOLDER_NAME)

      # Create directory if needed
      try:
        os.makedirs(self.output_path, exist_ok=True)
      except Exception as e:
        msg.showerror("Error", f"Failed to create output directory: {e}")
        self.selected_videos = []
        self.output_path = ""
        return

      # Hide empty state and clear list frame
      self._hide_empty_state()
      for widget in self.widgets['list_frame'].winfo_children():
        widget.destroy()

      # Initialize status labels list
      self.file_status_labels.clear()

      # Add files to list
      for i, file_path in enumerate(self.selected_videos, 1):
        self._add_file_to_list(i, file_path)

      # Update UI
      self.widgets['start_button'].configure(state=NORMAL)
      self.widgets['open_folder_button'].configure(state=NORMAL)
      self.widgets['file_count_label'].configure(text=str(self.total_videos_count))
      self.widgets['output_path_label'].configure(
          text=f"{self.output_path}")
      self.widgets['status_label'].configure(
          text="Ready to convert",
          text_color=self.COLORS["success"])

  def _add_file_to_list(self, index, file_path):
    """Adds a file to the list with better styling."""
    file_frame = CTkFrame(master=self.widgets['list_frame'],
                          fg_color=self.COLORS["bg_primary"],
                          corner_radius=8,
                          height=80,
                          border_width=1,
                          border_color=self.COLORS["border"])
    file_frame.pack(fill=X, pady=3, padx=3)
    file_frame.pack_propagate(False)

    # Main content container
    content_frame = CTkFrame(master=file_frame, fg_color="transparent")
    content_frame.pack(fill=BOTH, expand=True, padx=18)

    # Top row - file name and status
    top_row = CTkFrame(master=content_frame, fg_color="transparent")
    top_row.pack(fill=X, pady=(14, 4))

    # File number badge
    number_badge = CTkFrame(master=top_row,
                            fg_color=self.COLORS["accent"],
                            width=26, height=26, corner_radius=13)
    number_badge.pack(side=LEFT)
    number_badge.pack_propagate(False)

    CTkLabel(master=number_badge, text=str(index),
             font=("Segoe UI", 11, "bold"), text_color="white").pack(expand=True)

    # File name
    file_name = os.path.basename(file_path)
    name_label = CTkLabel(master=top_row, text=file_name,
                          font=("Segoe UI", 13),
                          text_color=self.COLORS["text_primary"],
                          anchor="w")
    name_label.pack(side=LEFT, fill=X, expand=True, padx=(12, 0))

    # Status indicator
    status_label = CTkLabel(master=top_row,
                            text="Pending",
                            font=("Segoe UI", 11),
                            text_color=self.COLORS["text_secondary"])
    status_label.pack(side=RIGHT)

    # Store status label for updates
    self.file_status_labels.append(status_label)

    # Bottom row - file size
    bottom_row = CTkFrame(master=content_frame, fg_color="transparent")
    bottom_row.pack(fill=X, pady=(4, 14))

    try:
      size_bytes = os.path.getsize(file_path)
      size_text = f"{size_bytes/(1024*1024):.1f} MB" if size_bytes >= 1024 * 1024 else f"{size_bytes/1024:.1f} KB"
    except:
      size_text = "Size unknown"

    CTkLabel(master=bottom_row, text=f"Size: {size_text}",
             font=("Segoe UI", 11),
             text_color=self.COLORS["text_light"]).pack(side=LEFT)

  def _update_file_status(self, file_index, status_text, color_key):
    """Safely updates a single file status label from the worker thread."""
    if file_index < len(self.file_status_labels):
      label = self.file_status_labels[file_index]
      self.after(10, lambda: label.configure(text=status_text, text_color=self.COLORS[color_key]))

  def _update_ui(self, current_file_name="", conversion_complete=False):
    """Safely updates main UI elements from the worker thread."""

    if conversion_complete:
      status_text = f"Completed ({self.converted_count} success, {self.failed_count} failed)"
      status_color = "success" if self.failed_count == 0 else "warning"
      progress_val = 1.0
      percent_text = f"{self.converted_count}/{self.total_videos_count} (100%)"
      current_file_name = "All conversions finished."

      # Re-enable buttons and set final state
      self.widgets['start_button'].configure(state=NORMAL, text="Restart Conversion")
      self.widgets['stop_button'].configure(state=DISABLED)
      self.is_converting = False

      if PLYER_AVAILABLE:
        notification.notify(
            title='Video Converter',
            message=status_text,
            timeout=10
        )

    else:
      # Update progress during conversion
      progress_val = self.converted_count / self.total_videos_count if self.total_videos_count > 0 else 0
      percent_text = f"{self.converted_count}/{self.total_videos_count} ({int(progress_val*100)}%)"
      status_text = "Converting..."
      status_color = "accent"

    # Scheduled UI updates
    self.widgets['progress_bar'].set(progress_val)
    self.widgets['progress_percentage'].configure(text=percent_text)
    self.widgets['status_label'].configure(text=status_text, text_color=self.COLORS[status_color])
    self.widgets['current_file_label'].configure(text=current_file_name)

  # --- Performance Critical Logic (FIXED) ---

  def _start_converting(self):
    """The core conversion logic run in a separate thread."""

    for i, input_path in enumerate(self.selected_videos):
      if not self.is_converting:
        break

      file_name = os.path.basename(input_path)

      self.after(10, lambda name=file_name: self._update_ui(current_file_name=f"Converting: {name}"))
      self._update_file_status(i, "In Progress...", "accent")

      try:
        base_name = os.path.splitext(file_name)[0]
        output_file = os.path.join(self.output_path, f"{base_name}.mp3")

        clip = VideoFileClip(input_path)

        if clip.audio is None:
          raise ValueError("Video file contains no audio stream.")

        # Fix applied: Removed 'verbose' and 'logger' arguments for compatibility
        clip.audio.write_audiofile(
            output_file,
            codec='mp3',
            bitrate='320k'
        )

        clip.close()

        self.converted_count += 1
        self._update_file_status(i, "Done", "success")

      except Exception as e:
        self.failed_count += 1
        error_msg = str(e).splitlines()[0] if str(e) else "Unknown Error"
        self._update_file_status(i, f"Failed: {error_msg[:20]}...", "error")
        print(f"Conversion failed for {file_name}: {e}")

      self.after(10, lambda: self._update_ui(
          current_file_name=f"Completed {self.converted_count} of {self.total_videos_count}"))

    self.after(10, lambda: self._update_ui(conversion_complete=True))

  def _start_conversion_thread(self):
    """Starts conversion in separate thread."""
    if not self.selected_videos:
      msg.showwarning("Warning", "Please select video files first.")
      return

    self.converted_count = 0
    self.failed_count = 0

    for i in range(len(self.file_status_labels)):
      self._update_file_status(i, "Pending", "text_secondary")

    self.widgets['start_button'].configure(state=DISABLED)
    self.widgets['stop_button'].configure(state=NORMAL)
    self.is_converting = True
    self.widgets['progress_bar'].set(0)
    self.widgets['progress_percentage'].configure(text=f"0/{self.total_videos_count} (0%)")
    self.widgets['status_label'].configure(text="Conversion Started", text_color=self.COLORS["accent"])
    self.widgets['current_file_label'].configure(text="Starting process...")

    self.conversion_thread = threading.Thread(target=self._start_converting)
    self.conversion_thread.daemon = True
    self.conversion_thread.start()

  def _stop_conversion(self):
    """Stops the conversion."""
    if self.is_converting:
      self.is_converting = False
      self.widgets['stop_button'].configure(state=DISABLED)

      def final_stop_update():
        self.widgets['status_label'].configure(
            text=f"Stopped ({self.converted_count} converted)",
            text_color=self.COLORS["warning"])
        self.widgets['start_button'].configure(state=NORMAL)
        self.widgets['current_file_label'].configure(text="Process interrupted by user.")

      self.after(500, final_stop_update)


# --- Main execution block ---
if __name__ == "__main__":
  app = VideoConverter()
  app.mainloop()
