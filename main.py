from typing import Dict, List, Tuple, Optional, Union, Any
from threading import Thread
import customtkinter as ctk
import socket
import json
import time
import re

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

RECEIVE_PORT = 5005
SEND_PORT = 5006

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(('', RECEIVE_PORT))


class FilterApp(ctk.CTk):
    """
    A GUI application for filtering and monitoring electric current measurements.
    
    This class implements a real-time filtering mechanism for electric current readings
    from multiple devices. It allows users to set threshold-based filters and displays
    their status through a graphical interface.
    
    Attributes
    ----------
    filters : Dict[int, List[Dict[str, Union[str, bool]]]]
        Dictionary storing filter rules for each device.
    filter_checkboxes : Dict[str, ctk.CTkCheckBox]
        Dictionary mapping filter rules to their corresponding checkboxes.
    filter_entries : List
        List storing filter entry widgets.
    """

    def __init__(self) -> None:
        """
        Initialize the FilterApp with GUI components and network listeners.
        """
        super().__init__()

        self.title("Electric Current Filtering Mechanism")
        self.geometry("800x600")
        self.resizable(False, False)
        self.configure(bg="#1a1a1a")

        self.filters: Dict[int, List[Dict[str, Union[str, bool]]]] = {
            1: [],  # Ia, Ib
            2: [],  # Ic, Id
            3: [],  # Ie, If
            4: []   # Ig, Ih
        }

        self.setup_interface()

        for device_id in self.filters:
            thread = Thread(target=self.listen_for_device_packets, args=(device_id,))
            thread.daemon = True
            thread.start()

        self.listener_thread = Thread(target=self.listen_for_device_packets, args=(1,))
        self.listener_thread.daemon = True
        self.listener_thread.start()
        
    def setup_interface(self) -> None:
        """
        Set up the graphical user interface components.
        """
        title_label = ctk.CTkLabel(
            self,
            text="Electric Current Filtering Mechanism",
            font=("JetBrains Mono", 20)
        )
        title_label.pack(pady=20)

        self.filter_input = ctk.CTkEntry(
            self,
            placeholder_text="Enter a Filter Rule",
            width=400,
            font=("JetBrains Mono", 15),
            justify="center"
        )
        self.filter_input.pack(pady=(10, 5))

        add_button = ctk.CTkButton(
            self,
            text="Add Filter",
            font=("JetBrains Mono", 15),
            command=self.verify_and_add_filter,
            fg_color="#024bbf",
            hover_color="#0073e6"
        )
        add_button.pack(pady=10)

        self.filters_frame = ctk.CTkFrame(self, corner_radius=15)
        self.filters_frame.pack(pady=10, padx=20, fill="both", expand=True)

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
            width=self.filters_frame.winfo_width()
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.filters_frame.bind("<Configure>", self.on_frame_configure)

        self.filter_checkboxes: Dict[str, ctk.CTkCheckBox] = {}
        self.filter_entries: List[Any] = []

    def verify_and_add_filter(self) -> None:
        """
        Verify and add a new filter rule based on user input.
        """
        filter_rule = self.filter_input.get().strip()
        if self.is_valid_filter_rule(filter_rule):
            device_type = filter_rule.split()[0]
            device_id = self.get_device_id(device_type)
            if device_id in self.filters:
                self.filters[device_id].append({"filter": filter_rule, "state": False})
                self.add_filter(filter_rule, device_id)
            self.filter_input.delete(0, 'end')
        else:
            self.show_warning()

    def remove_filter(self, filter_frame: ctk.CTkFrame, device_id: int, filter_rule: str) -> None:
        """
        Remove a filter from both the data structure and the GUI.

        Parameters
        ----------
        filter_frame : ctk.CTkFrame
            The frame containing the filter elements.
        device_id : int
            The ID of the device associated with the filter.
        filter_rule : str
            The filter rule to be removed.
        """
        self.filters[device_id] = [f for f in self.filters[device_id] if f["filter"] != filter_rule]
        if filter_rule in self.filter_checkboxes:
            del self.filter_checkboxes[filter_rule]
        filter_frame.destroy()

    def listen_for_device_packets(self, device_id: int) -> None:
        """
        Listen for UDP packets from a specific device.

        Parameters
        ----------
        device_id : int
            The ID of the device to monitor.
        """
        while True:
            try:
                data, _ = sock.recvfrom(1024)
                packet = json.loads(data)
                
                if packet.get("id") == device_id:
                    start_time = time.time()
                    self.process_packet(packet, start_time)
            except Exception as e:
                print(f"Error listening for packets from device {device_id}: {e}", file=sys.stderr)

    def process_packet(self, packet: Dict[str, Union[int, str]], start_time: float) -> None:
        """
        Process received packets and update filter states.

        Parameters
        ----------
        packet : Dict[str, Union[int, str]]
            The received packet containing device ID and measurement.
        start_time : float
            The timestamp when packet processing started.
        """
        device_id = packet["id"]
        measurement = packet["measurement[A]"]

        if device_id in self.filters:
            for filter_info in self.filters[device_id]:
                filter_rule = filter_info["filter"]
                threshold_achieved = self.evaluate_filter(filter_rule, measurement)
                
                if threshold_achieved != filter_info["state"]:
                    filter_info["state"] = threshold_achieved
                    self.send_filtered_packet(device_id, filter_rule, threshold_achieved, start_time)
                    
                    if filter_rule in self.filter_checkboxes:
                        self.set_filter_active(filter_rule, threshold_achieved)

    def evaluate_filter(self, filter_rule: str, measurement: int) -> bool:
        """
        Evaluate if a measurement meets the filter criteria.

        Parameters
        ----------
        filter_rule : str
            The filter rule to evaluate.
        measurement : int
            The current measurement value.

        Returns
        -------
        bool
            True if the measurement meets the filter criteria, False otherwise.
        """
        device, operator, value = re.match(r"(I[a-z])\s*(>|=|<)\s*(\d+)", filter_rule).groups()
        value = int(value)

        if operator == ">":
            return measurement > value
        elif operator == "<":
            return measurement < value
        elif operator == "=":
            return measurement == value
        return False

    def send_filtered_packet(self, device_id: int, filter_rule: str, threshold_achieved: bool, start_time: float) -> None:
        """
        Send a filtered packet via UDP broadcast.

        Parameters
        ----------
        device_id : int
            The ID of the device.
        filter_rule : str
            The filter rule that was evaluated.
        threshold_achieved : bool
            Whether the threshold was achieved.
        start_time : float
            The timestamp when packet processing started.
        """
        try:
            filtered_packet = {
                "id": device_id,
                "filter": filter_rule,
                "threshold_achieved": threshold_achieved
            }
            message = json.dumps(filtered_packet).encode('utf-8')
            sock.sendto(message, ('<broadcast>', SEND_PORT))
            end_time = time.time()
            processing_time = (end_time - start_time) * 1000
            print(f"Processing time: {processing_time:.6f} ms")
        except Exception as e:
            print(f"Error sending packet: {e}", file=sys.stderr)

    def get_device_id(self, device: str) -> int:
        """
        Map device identifier to device ID.

        Parameters
        ----------
        device : str
            The device identifier (e.g., 'Ia', 'Ib').

        Returns
        -------
        int
            The corresponding device ID.
        """
        device_map = {
            "Ia": 1, "Ib": 1,
            "Ic": 2, "Id": 2,
            "Ie": 3, "If": 3,
            "Ig": 4, "Ih": 4
        }
        return device_map.get(device, 0)

    def on_frame_configure(self, event: Optional[Any] = None) -> None:
        """
        Update canvas window width when parent frame is resized.

        Parameters
        ----------
        event : Optional[Any]
            The configure event object.
        """
        self.canvas.itemconfig("win", width=event.width)

    def is_valid_filter_rule(self, rule: str) -> bool:
        """
        Check if a filter rule matches the required format.

        Parameters
        ----------
        rule : str
            The filter rule to validate.

        Returns
        -------
        bool
            True if the rule is valid, False otherwise.
        """
        pattern = r"^I[a-z]\s*(>|=|<)\s*\d+$"
        return bool(re.match(pattern, rule))
    
    def show_warning(self) -> None:
        """
        Display a warning window for invalid filter rules.
        """
        warning_window = ctk.CTkToplevel(self)
        warning_window.geometry("600x220")
        warning_window.title("Invalid Filter Rule")
        warning_window.configure(bg="#1a1a1a")

        warning_window.transient(self)
        warning_window.lift()
        warning_window.focus_set()

        warning_message = ctk.CTkLabel(
            warning_window,
            text="Invalid rule format.\nUse: I[letter] [operator] [number]\nWhere: [letter] is a lower case letter,\n[operator] is <, > or = and\n[number] is a positive integer.\nExample: Ia > 5",
            font=("JetBrains Mono", 13),
            wraplength=500,
        )
        warning_message.pack(pady=20, padx=20)

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
        """
        Add a new filter to the GUI.

        Parameters
        ----------
        rule : str
            The filter rule to add.
        device_id : int
            The ID of the device associated with the filter.
        """
        filter_row = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        filter_row.pack(fill="x", pady=5)

        filter_container = ctk.CTkFrame(filter_row, fg_color="transparent")
        filter_container.pack(expand=True)

        filter_label = ctk.CTkLabel(
            filter_container,
            text=f"{rule}[A]",
            font=("JetBrains Mono", 15),
            justify="center"
        )
        filter_label.pack(side="left", padx=(0, 10))

        filter_checkbox = ctk.CTkCheckBox(
            filter_container,
            text="Active - Threshold Achieved",
            font=("JetBrains Mono", 14),
            fg_color="#024bbf",
            hover_color="#0073e6",
            state="disabled"
        )
        filter_checkbox.pack(side="left", padx=10)

        self.filter_checkboxes[rule] = filter_checkbox

        remove_button = ctk.CTkButton(
            filter_container,
            text="-",
            width=30,
            height=30,
            font=("JetBrains Mono", 15),
            fg_color="#024bbf",
            hover_color="#0073e6",
            command=lambda f=filter_row, d=device_id, fr=rule: self.remove_filter(f, d, fr)
        )
        remove_button.pack(side="left")

    def set_filter_active(self, filter_rule: str, threshold_achieved: bool) -> None:
        """
        Update the checkbox state for a filter.

        Parameters
        ----------
        filter_rule : str
            The filter rule to update.
        threshold_achieved : bool
            Whether the threshold was achieved.
        """
        try:
            filter_checkbox = self.filter_checkboxes.get(filter_rule)
            if filter_checkbox and filter_checkbox.winfo_exists():
                filter_checkbox.select() if threshold_achieved else filter_checkbox.deselect()
        except Exception as e:
            print(f"Error updating checkbox for filter {filter_rule}: {e}")


if __name__ == "__main__":
    app = FilterApp()
    app.mainloop()