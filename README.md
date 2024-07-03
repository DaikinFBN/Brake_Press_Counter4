# Brake Press Counter

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [SD Card Imaging](#sd-card-imaging)
- [Contributing](#contributing)
- [License](#license)

## Overview
The Brake Press Counter is a system designed to monitor and display the efficiency and count of a brake press machine in real-time. This system uses a Raspberry Pi for GPIO input handling and a Tkinter GUI for display purposes. The project includes settings management through a JSON file, making it flexible and easy to configure.

## Features
- Real-time monitoring of brake press counts
- Display of efficiency and goals
- Configurable shift and break times
- JSON-based settings management
- Fullscreen Tkinter GUI for clear visibility
- GPIO input handling for counting operations

## Requirements
- Python 3.x
- Raspberry Pi with GPIO pins
- Required Python packages:
  - `tkinter`
  - `Pillow`
  - `RPi.GPIO`
- A JSON file for configuration (`settings.json`)

## Installation
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/YourUsername/Brake_Press_Counter.git
   cd Brake_Press_Counter
