import customtkinter as ctk
import re
from tkinter import messagebox

# Theme configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FilterApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Electric Current Filtering Mechanism")
        self.geometry("1000x600")
        self.resizable(False, False)
        self.configure(bg="#1a1a1a")

        # Project Title
        title_label = ctk.CTkLabel(
            self,
            text="Electric Current Filtering Mechanism",
            font=("JetBrains Mono", 20)
        )
        title_label.pack(pady=20)

        # Text box for filter input
        self.filter_input = ctk.CTkEntry(
            self,
            placeholder_text="Enter filter rule (e.g., Ia >= 5)",
            font=("JetBrains Mono", 15),
            justify="center"
        )
        self.filter_input.pack(pady=10)

        # Main frame
        self.filters_frame = ctk.CTkFrame(self, corner_radius=15)
        self.filters_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Canvas and Scrollbar
        self.canvas = ctk.CTkCanvas(
            self.filters_frame,
            highlightthickness=0,
            bg="#1a1a1a"
        )
        self.scrollbar = ctk.CTkScrollbar(
            self.filters_frame,
            orientation="vertical",
            command=self.canvas.yview
        )
        self.scrollable_frame = ctk.CTkFrame(
            self.canvas,
            fg_color="#1a1a1a"
        )

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw",
            width=self.filters_frame.winfo_width()
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind to update canvas width when parent frame is resized
        self.filters_frame.bind("<Configure>", self.on_frame_configure)

        # Lists for references
        self.filter_entries = []
        self.filter_checkboxes = []

        # Add initial filter
        self.add_filter()

        # Button to add filter
        add_button = ctk.CTkButton(
            self,
            text="Add Filter",
            font=("JetBrains Mono", 15),
            command=self.add_filter_with_validation,
            fg_color="#024bbf",
            hover_color="#0073e6"
        )
        add_button.pack(pady=10)

    def on_frame_configure(self, event=None):
        # Update canvas window width when parent frame is resized
        self.canvas.itemconfig("win", width=event.width)

    def add_filter_with_validation(self) -> None:
        # Validate filter rule input before adding
        rule = self.filter_input.get()
        if self.is_valid_filter_rule(rule):
            self.add_filter(rule)
            self.filter_input.delete(0, 'end')  # Clear input after adding
        else:
            self.show_error_message("Invalid filter format.\nUse format: 'In >= N' where:\n - 'I' is a prefix\n - 'n' is a lowercase letter\n - '>=', '<=', '=', '<', or '>'\n - 'N' is a positive integer.")

    def is_valid_filter_rule(self, rule: str) -> bool:
        # Regular expression for pattern: In >= N
        pattern = r"^I[a-z]\s*(>=|<=|=|>|<)\s*\d+$"
        return bool(re.match(pattern, rule))

    def show_error_message(self, message: str) -> None:
        # Display error message in a popup window
        messagebox.showerror("Invalid Filter Rule", message)

    def add_filter(self, rule_text: str = "") -> None:
        # Frame for filter row
        filter_row = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        filter_row.pack(fill="x", pady=5)

        # Frame that holds filter elements
        filter_container = ctk.CTkFrame(filter_row, fg_color="transparent")
        filter_container.pack(expand=True)

        # Entry for filter (disabled to prevent modification)
        filter_entry = ctk.CTkEntry(
            filter_container,
            font=("JetBrains Mono", 15),
            width=250,
            justify="center"
        )
        filter_entry.insert(0, rule_text)
        filter_entry.configure(state="disabled")  # Prevent user input
        filter_entry.pack(side="left", padx=(0, 10))

        # Checkbox
        filter_checkbox = ctk.CTkCheckBox(
            filter_container,
            text="Active - Threshold Achieved",
            font=("JetBrains Mono", 14),
            fg_color="#024bbf",
            hover_color="#0073e6",
            state="disabled"
        )
        filter_checkbox.pack(side="left", padx=10)

        # Remove button
        remove_button = ctk.CTkButton(
            filter_container,
            text="-",
            width=30,
            height=30,
            font=("JetBrains Mono", 15),
            fg_color="#024bbf",
            hover_color="#0073e6",
            command=lambda: self.remove_filter(filter_row)
        )
        remove_button.pack(side="left", padx=(10, 0))

        # Add to lists
        self.filter_entries.append(filter_entry)
        self.filter_checkboxes.append(filter_checkbox)

    def remove_filter(self, filter_frame: ctk.CTkFrame) -> None:
        filter_frame.destroy()

    def set_filter_active(self, index: int, active: bool) -> None:
        if active:
            self.filter_checkboxes[index].select()
        else:
            self.filter_checkboxes[index].deselect()

    def toggle_filter_status(self, checkbox: ctk.CTkCheckBox) -> None:
        if checkbox.get():
            print("Filter is active")
        else:
            print("Filter is not active")

if __name__ == "__main__":
    app = FilterApp()
    app.mainloop()
