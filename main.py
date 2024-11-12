import customtkinter as ctk

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

        # Frame principal
        self.filters_frame = ctk.CTkFrame(self, corner_radius=15)
        self.filters_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Canvas e Scrollbar
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
            width=self.filters_frame.winfo_width()  # Define largura igual ao frame pai
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind para atualizar a largura da janela do canvas quando o frame pai for redimensionado
        self.filters_frame.bind("<Configure>", self.on_frame_configure)

        # Listas para referências
        self.filter_entries = []
        self.filter_checkboxes = []

        # Adiciona filtro inicial
        self.add_filter()

        # Botão de adicionar
        add_button = ctk.CTkButton(
            self,
            text="Add Filter",
            font=("JetBrains Mono", 15),
            command=self.add_filter,
            fg_color="#024bbf",
            hover_color="#0073e6"
        )
        add_button.pack(pady=10)

    def on_frame_configure(self, event=None):
        # Atualiza a largura da janela do canvas quando o frame pai é redimensionado
        self.canvas.itemconfig("win", width=event.width)

    def add_filter(self) -> None:
        # Frame para a linha do filtro
        filter_row = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        filter_row.pack(fill="x", pady=5)

        # Frame central que contém os elementos do filtro
        filter_container = ctk.CTkFrame(filter_row, fg_color="transparent")
        filter_container.pack(expand=True)

        # Entry para o filtro
        filter_entry = ctk.CTkEntry(
            filter_container,
            placeholder_text="Enter a filter rule",
            width=250,
            font=("JetBrains Mono", 15),
            justify="center"
        )
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

        # Botão de remover
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

        # Adiciona às listas
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