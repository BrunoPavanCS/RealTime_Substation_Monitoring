import customtkinter as ctk

# Theme configuration
ctk.set_appearance_mode("dark")  # Set to dark mode
ctk.set_default_color_theme("blue")  # Set default color theme to blue

class FilterApp(ctk.CTk):
    """Application for adding and removing filtering rules for electric current measurements."""

    def __init__(self) -> None:
        """Initialize the GUI components."""
        super().__init__()

        self.title("Electric Current Filtering Mechanism")
        self.geometry("1000x600")
        self.resizable(False, False)
        self.configure(bg="#1a1a1a")  # Set app background to dark

        # Project Title
        title_label = ctk.CTkLabel(
            self,
            text="Electric Current Filtering Mechanism",
            font=("JetBrains Mono", 20)
        )
        title_label.pack(pady=20)

        # Frame to contain filter input boxes
        self.filters_frame = ctk.CTkFrame(self, corner_radius=15)  # Rounded corners
        self.filters_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Canvas and Scrollbar to enable scrolling if many filters are added
        self.canvas = ctk.CTkCanvas(self.filters_frame, highlightthickness=0, bg="#1a1a1a", borderwidth=20)  # Dark canvas background
        self.scrollbar = ctk.CTkScrollbar(self.filters_frame, orientation="vertical", command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # List to maintain references to filter input boxes
        self.filter_entries: list[ctk.CTkEntry] = []

        # Add the initial filter box
        self.add_filter()

        # Button to add new filters
        add_button = ctk.CTkButton(
            self,
            text="Add Filter",
            font=("JetBrains Mono", 15),
            command=self.add_filter,
            fg_color="#024bbf",  # Updated button color to a softer blue
            hover_color="#0073e6"  # Keeping hover color the same
        )
        add_button.pack(pady=10)

    def add_filter(self) -> None:
        """Add a new filter input box to the scrollable frame."""
        filter_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=10)  # Rounded corners for filter frame
        filter_frame.pack(pady=5, padx=10, fill="x")

        filter_entry = ctk.CTkEntry(
            filter_frame,
            font=("JetBrains Mono", 15),
            placeholder_text="Enter a filter rule",
            width=300  # Increased width for placeholder text to fit
        )
        filter_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        remove_button = ctk.CTkButton(
            filter_frame,
            text="-",
            font=("JetBrains Mono", 15),
            width=30,
            height=30,
            fg_color="#024bbf",  # Updated remove button color to softer blue
            hover_color="#0073e6",  # Keeping hover color the same
            command=lambda: self.remove_filter(filter_frame)
        )
        remove_button.pack(side="right")

        self.filter_entries.append(filter_entry)

    def remove_filter(self, filter_frame: ctk.CTkFrame) -> None:
        """Remove the specified filter frame from the GUI.
        
        Args:
            filter_frame (ctk.CTkFrame): The frame containing the filter input box to be removed.
        """
        filter_frame.destroy()

if __name__ == "__main__":
    app = FilterApp()
    app.mainloop()
