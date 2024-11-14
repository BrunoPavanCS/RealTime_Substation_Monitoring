# Electric Current Filtering Software

Final project of the Real-Time Computing Systems discipline, at the Federal University of Uberlândia - UFU.

A real-time electric current monitoring and filtering system with a graphical interface. The application receives current measurements via UDP packets, applies user-defined filters, and displays the results in real-time.

## Features

- Real-time monitoring of electric current measurements from multiple devices
- Custom filter creation with threshold-based rules
- Visual feedback through an interactive GUI
- Support for multiple concurrent device connections
- Real-time status updates via checkboxes
- UDP broadcast communication

## Project Structure

```
electric-current-filter/
├── main.py           # Main application with GUI and filtering logic
├── mockup.py         # UDP packet simulator for testing
├── requirements.txt  # Project dependencies
└── README.md         # This file
```

## Prerequisites

- Python 3.8+
- Virtual environment (recommended)
- Required packages listed in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd electric-current-filter
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the main application:
```bash
python main.py
```

2. In a separate terminal (with venv activated), run the mockup script:
```bash
python mockup.py
```

3. The GUI will appear, allowing you to:
   - Add new filters using the format: `Ix <operator> value`
     - Where `x` is a letter from a to h
     - `operator` is >, <, or =
     - `value` is a positive integer
   - Example: `Ia > 5`
   - Monitor filter states through checkboxes
   - Remove filters using the "-" button

## Filter Rules

- Devices are grouped in pairs:
  - Ia, Ib (Device ID 1)
  - Ic, Id (Device ID 2)
  - Ie, If (Device ID 3)
  - Ig, Ih (Device ID 4)
- Each filter consists of:
  - A device identifier (Ia through Ih)
  - An operator (>, <, or =)
  - A threshold value

## Network Configuration

- The application uses UDP for communication:
  - Receive Port: 5005
  - Send Port: 5006
- Broadcasts are used to allow multiple instances on the same network

## Dependencies

- customtkinter==5.2.2
- darkdetect==0.7.1
- packaging==23.2
- typing_extensions==4.9.0

## Error Handling

- Invalid filter formats trigger a warning window
- Network errors are logged to stderr
- GUI elements are protected against race conditions

## Performance

- Processing times for packet handling are logged in milliseconds
- Multithreaded design ensures responsive GUI
- Efficient state management for filter updates
