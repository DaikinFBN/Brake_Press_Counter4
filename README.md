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

2. **Install the Required Python Packages:**
   ```bash
   pip install Pillow RPi.GPIO

3. **Prepare the Configuration File:**
   Create a `settings.json` file in the project directory with the required settings. Refer to the Configuration section for details.

## Usage
1. **Automatic Startup:**
   The brake press counter application is configured to start automatically when the Raspberry Pi boots up. No manual action is required to start the application.
2. **User Interface:**
   - The application window will display the current bend count, goals, shift goals, and efficiency.
   - Use the following keyboard shortcuts to interact with the application:
     - `Ctrl+W`: Close the application.
     - `Ctrl+U`: Update the window.
     - `Return` (Enter): Interact with the widget in focus.
     - `b`: Manually increase the bend count (for testing).
     - `g`: Manually increase the goal count (for testing).
     - `o`: Open settings.
3. **Settings:**
   - To open the settings window, press `o`.
   - Adjust shift and break times as needed.
   - Save the settings and close the settings window when done.
4. **Automatic Reset:**
   - The bend count and shift goals will reset automatically based on the times specified in the settings.
5. **SD Card Imaging:**
   - If you need to re-image the Raspberry Pi SD card, follow these steps:
     1. **Download the Raspberry Pi Image:**
        - Download the image file from the repository or a provided link.
     2. **Use Imaging Software:**
        - Use software like [Raspberry Pi Imager](https://www.raspberrypi.com/software/) or [Balena Etcher](https://www.balena.io/etcher/) to write the image to the SD card.
     3. **Insert the SD Card:**
        - Insert the imaged SD card into the Raspberry Pi and power it on.
6. **Updating the Application:**
   - To update the application, pull the latest changes from the repository:
     ```bash
     git pull origin main
     ```
   - Restart the application to apply the updates.
7. **Raspberry Pi Kiosk Mode Setup:**
   - The Raspberry Pi is set up to automatically start the application in kiosk mode. No additional setup is required for normal usage.

## Configuration
1. **Configuration Overview:**
   - The brake press counter application allows you to configure shift times, break times, and various settings through the settings interface.
2. **Accessing Settings:**
   - To open the settings window, press `o` while the application is running.
3. **Shift Times:**
   - Configure the start and end times for each shift.
   - If your operation includes multiple shifts, enable the second shift and set the corresponding times.
4. **Break Times:**
   - Set the start times and durations for breaks and lunch periods within each shift.
5. **Saving Changes:**
   - After making changes to the shift and break times, click the 'Save' button to apply the new settings.
6. **Automatic Reset Times:**
   - The bend count and shift goals will automatically reset at the configured times.
7. **File Locations:**
   - The configuration is stored in a JSON file located in the application directory (`/home/daikinfbn/Brake_Press_Counter4/settings.json`).
8. **Manual Configuration:**
   - If needed, you can manually edit the `settings.json` file to configure the application settings. Make sure the file is formatted correctly to avoid errors.
9. **Configuration Parameters:**
   - The `settings.json` file includes parameters such as `shift_times`, `break_times`, `count_pin`, `auto_reset_times`, and `epe_number`.
