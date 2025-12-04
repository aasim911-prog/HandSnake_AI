# Snake Game with Hand Control

This project implements a classic Snake game controlled by hand gestures using a webcam.

## Prerequisites

- **Python 3.8 - 3.11** (MediaPipe does not yet support Python 3.12 or 3.13)
- Webcam

## Installation

1.  **Create a Virtual Environment (Recommended)**
    It is highly recommended to use a Python version compatible with MediaPipe (e.g., Python 3.10).

    ```bash
    # If you have Python 3.10 installed:
    py -3.10 -m venv venv
    .\venv\Scripts\activate
    ```

2.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

## Running the Game

1.  Ensure your webcam is connected.
2.  Run the main script:

    ```bash
    python main.py
    ```

## Controls

- **Hand Movements**:
    - Move your hand (wrist/index finger) relative to the center of the camera frame.
    - **Right Zone**: Turn Right
    - **Left Zone**: Turn Left
    - **Up Zone**: Turn Up
    - **Down Zone**: Turn Down
    - **Center**: Neutral (Keep current direction)
- **Keyboard**:
    - `ESC`: Quit
    - `R`: Restart (when Game Over)

## Troubleshooting

- **ModuleNotFoundError: No module named 'mediapipe'**:
    - This usually means you are running Python 3.12 or newer. MediaPipe currently supports up to Python 3.11. Please install Python 3.11 and use it to run this project.
