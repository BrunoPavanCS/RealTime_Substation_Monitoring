import customtkinter as ctk
import json
import re
import socket
import time
from threading import Thread
from typing import Dict, List
import sys

# Configurações de tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Configurações de IP e Porta para receber e enviar pacotes UDP
RECEIVE_PORT = 5005
SEND_PORT = 5006

# Configuração do socket para enviar e receber dados
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # permite reutilizar o endereço

# Para ouvir pacotes broadcast, o cliente deve escutar no IP broadcast ou em todos os IPs locais ('')
sock.bind(('', RECEIVE_PORT))


class FilterApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Electric Current Filtering Mechanism")
        self.geometry("800x600")
        self.resizable(False, False)
        self.configure(bg="#1a1a1a")

        # Estrutura de dados para armazenar os filtros por dispositivo
        self.filters: Dict[int, List[Dict[str, str | bool]]] = {
            1: [],  # Ia, Ib
            2: [],  # Ic, Id
            3: [],  # Ie, If
            4: []   # Ig, Ih
        }

        # Configuração da interface
        self.setup_interface()

        # Thread para escutar pacotes UDP
        self.listener_thread = Thread(target=self.listen_for_packets)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def setup_interface(self):
        # Project Title
        title_label = ctk.CTkLabel(
            self,
            text="Electric Current Filtering Mechanism",
            font=("JetBrains Mono", 20)
        )
        title_label.pack(pady=20)

        # Filter input box
        self.filter_input = ctk.CTkEntry(
            self,
            placeholder_text="Enter a Filter Rule",
            width=400,
            font=("JetBrains Mono", 15),
            justify="center"
        )
        self.filter_input.pack(pady=(10, 5))  # Positioned above Add Filter button

        # Add Filter Button
        add_button = ctk.CTkButton(
            self,
            text="Add Filter",
            font=("JetBrains Mono", 15),
            command=self.verify_and_add_filter,
            fg_color="#024bbf",
            hover_color="#0073e6"
        )
        add_button.pack(pady=10)

        # Frame principal
        self.filters_frame = ctk.CTkFrame(self, corner_radius=15)
        self.filters_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Canvas e Scrollbar
        self.canvas = ctk.CTkCanvas(
            self.filters_frame, 
            highlightthickness=0, 
            bg="#1a1a1a",
            borderwidth=20
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

    def verify_and_add_filter(self):
        filter_rule = self.filter_input.get().strip()
        if self.is_valid_filter_rule(filter_rule):
            device_type = filter_rule.split()[0]
            device_id = self.get_device_id(device_type)
            if device_id in self.filters:
                self.filters[device_id].append({"filter": filter_rule, "state": False})
                # Passa `device_id` ao adicionar o filtro
                self.add_filter(filter_rule, device_id)
            self.filter_input.delete(0, 'end')
        else:
            self.show_warning()


    def remove_filter(self, filter_frame: ctk.CTkFrame, device_id: int, filter_index: int) -> None:
        # Remove o filtro da interface e da estrutura de dados
        filter_frame.destroy()
        del self.filters[device_id][filter_index]

    def listen_for_packets(self):
        while True:
            try:
                # Recebe pacotes UDP do mockup
                data, _ = sock.recvfrom(1024)
                packet = json.loads(data)
                start_time = time.time()
                self.process_packet(packet, start_time)
            except Exception as e:
                print(f"Erro ao ouvir pacotes: {e}", file=sys.stderr)

    def process_packet(self, packet: Dict[str, int | str], start_time: float):
        device_id = packet["id"]
        measurement = packet["measurement[A]"]

        # Verifica filtros associados ao dispositivo
        if device_id in self.filters:
            for i, filter_info in enumerate(self.filters[device_id]):
                filter_rule = filter_info["filter"]
                threshold_achieved = self.evaluate_filter(filter_rule, measurement)
                
                # Comportamento toggle
                if threshold_achieved != filter_info["state"]:
                    filter_info["state"] = threshold_achieved
                    self.send_filtered_packet(device_id, filter_rule, threshold_achieved, start_time)

    def evaluate_filter(self, filter_rule: str, measurement: int) -> bool:
        # Realiza parsing do filtro e verifica se a medição cumpre a condição
        device, operator, value = re.match(r"(I[a-z])\s*(>|=|<)\s*(\d+)", filter_rule).groups()
        value = int(value)

        if operator == ">":
            return measurement > value
        elif operator == "<":
            return measurement < value
        elif operator == "=":
            return measurement == value
        return False

    def send_filtered_packet(self, device_id: int, filter_rule: str, threshold_achieved: bool, start_time: float):
        try:
            # Cria e envia pacote JSON UDP com o filtro atingido
            filtered_packet = {
                "id": device_id,
                "filter": filter_rule,
                "threshold_achieved": threshold_achieved
            }
            message = json.dumps(filtered_packet).encode('utf-8')
            sock.sendto(message, ('<broadcast>', SEND_PORT))
            # Calcula e exibe o tempo de processamento em milissegundos
            end_time = time.time()
            processing_time = (end_time - start_time) * 1000
            print(f"Processing time: {processing_time:.6f} ms")
        except Exception as e:
            print(f"Erro ao enviar pacote: {e}", file=sys.stderr)

    def get_device_id(self, device: str) -> int:
        # Mapeia dispositivo para ID
        device_map = {
            "Ia": 1, "Ib": 1,
            "Ic": 2, "Id": 2,
            "Ie": 3, "If": 3,
            "Ig": 4, "Ih": 4
        }
        return device_map.get(device, 0)

    # ... outras funções (show_warning, is_valid_filter_rule, etc.)
    def on_frame_configure(self, event=None):
        # Atualiza a largura da janela do canvas quando o frame pai é redimensionado
        self.canvas.itemconfig("win", width=event.width)

    def is_valid_filter_rule(self, rule: str) -> bool:
        pattern = r"^I[a-z]\s*(>|=|<)\s*\d+$"
        return bool(re.match(pattern, rule))
    
    def show_warning(self):
        # Janela de aviso
        warning_window = ctk.CTkToplevel(self)
        warning_window.geometry("600x220")
        warning_window.title("Invalid Filter Rule")
        warning_window.configure(bg="#1a1a1a")

        # Associa a janela de aviso à janela principal para que fique sempre à frente
        warning_window.transient(self)
        warning_window.lift()  # Garante que a janela esteja na frente
        warning_window.focus_set()  # Coloca o foco na janela de aviso

        # Mensagem de aviso
        warning_message = ctk.CTkLabel(
            warning_window,
            text="Invalid rule format.\nUse: I[letter] [operator] [number]\nWhere: [letter] is a lower case letter,\n[operator] is <, > or = and\n[number] is a positive integer.\nExample: Ia > 5",
            font=("JetBrains Mono", 13),
            wraplength=500,
        )
        warning_message.pack(pady=20, padx=20)

        # Botão para fechar a janela
        close_button = ctk.CTkButton(
            warning_window,
            text="Close",
            font=("JetBrains Mono", 12),
            fg_color="#024bbf",
            hover_color="#0073e6",
            command=warning_window.destroy
        )
        close_button.pack(pady=10)



    def add_filter(self, rule: str, device_id: int) -> None:
        # Frame para a linha do filtro
        filter_row = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        filter_row.pack(fill="x", pady=5)

        # Frame central que contém os elementos do filtro
        filter_container = ctk.CTkFrame(filter_row, fg_color="transparent")
        filter_container.pack(expand=True)

        # Label para exibir a regra do filtro
        filter_label = ctk.CTkLabel(
            filter_container,
            text=rule,
            font=("JetBrains Mono", 15),
            justify="center"
        )
        filter_label.pack(side="left", padx=(0, 10))

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

        # Define o índice do filtro baseado na posição na lista
        filter_index = len(self.filters[device_id]) - 1

        # Botão de remover
        remove_button = ctk.CTkButton(
            filter_container,
            text="-",
            width=30,
            height=30,
            font=("JetBrains Mono", 15),
            fg_color="#024bbf",
            hover_color="#0073e6",
            command=lambda: self.remove_filter(filter_row, device_id, filter_index)
        )
        remove_button.pack(side="left", padx=(10, 0))

        # Adiciona às listas
        self.filter_entries.append(filter_label)
        self.filter_checkboxes.append(filter_checkbox)

    
    def set_filter_active(self, index: int, active: bool) -> None:
        if active:
            self.filter_checkboxes[index].select()
        else:
            self.filter_checkboxes[index].deselect()

if __name__ == "__main__":
    app = FilterApp()
    app.mainloop()
