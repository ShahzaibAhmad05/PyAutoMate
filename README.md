# PyAutoMate

**PyAutoMate** is a desktop automation tool that allows users to create, manage, and execute automation scripts through an intuitive GUI. Build custom automation workflows without writing code.

## Features

- **Visual Script Builder**: Create automation scripts through an easy-to-use interface
- **Customizable Buttons**: Drag-and-drop button interface for organizing automation tasks
- **Theme Support**: Choose between light and dark themes
- **Flexible Grid Layout**: Configurable grid system for button placement
- **Script Management**: Save, load, and delete automation scripts
- **Multi-threaded Execution**: Non-blocking script execution using threading
- **Keyboard & Mouse Control**: Full automation capabilities using PyAutoGUI
- **Custom UI Components**: Built with PyQt5 for a polished desktop experience

## Requirements

- Python 3.7+
- See `requirements.txt` for all dependencies

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ShahzaibAhmad05/PyAutoMate.git
cd PyAutoMate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

The application will:
- Create necessary directories (`images/`, `scripts/`)
- Verify all required configuration files and stylesheets
- Launch the main GUI window

## Project Structure

```
PyAutoMate/
├── main.py                 # Application entry point
├── mainTool.py            # Main window and GUI logic
├── Assistant.py           # Text input/output handling
├── modules/               # Core functionality modules
│   ├── getters.py        # Configuration getters
│   ├── setters.py        # Configuration setters
│   ├── utils.py          # Utility functions
│   ├── interpreter.py    # Script interpretation
│   ├── sysUtils.py       # System utilities
│   └── styling.py        # UI styling
├── ui/                    # User interface components
│   ├── scriptingDialog.py # Script creation dialog
│   ├── addButtonWindow.py # Button creation window
│   ├── draggableButton.py # Custom draggable button
│   ├── customTextEdit.py  # Custom text editor
│   ├── scriptOption.py    # Script options
│   ├── settings.py        # Settings dialog
│   └── toggleSwitch.py    # Toggle UI component
├── stylesheets/           # CSS stylesheets for UI themes
├── scripts/               # Saved automation scripts
├── images/                # Button icons
├── settings.json          # Application configuration
└── requirements.txt       # Python dependencies
```

## Configuration

Edit `settings.json` to customize:
- `theme`: Choose between "light" or "dark"
- `size`: Button size (default: 45)
- `grid`: Grid dimensions (default: 5)

Example:
```json
{
    "theme": "light",
    "size": "45",
    "grid": "5"
}
```

## Dependencies

- **PyQt5**: Desktop GUI framework
- **pyautogui**: Mouse and keyboard control
- **keyboard**: Keyboard event handling
- **mouse**: Mouse event handling
- **pyperclip**: Clipboard operations
- **Pillow**: Image processing
- **psutil**: System utilities
- **PyGetWindow**: Window management
- **opencv-python**: Computer vision
- **numpy**: Numerical computing

## License

[Specify your license here]

## Author

Shahzaib Ahmad

---

For more information or issues, please visit the [GitHub repository](https://github.com/ShahzaibAhmad05/PyAutoMate).
