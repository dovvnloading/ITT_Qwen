<img width="856" height="433" alt="ITT-QWEN_Banner_001" src="https://github.com/user-attachments/assets/56318bfb-d8b8-4259-b659-65d4b8040582" />

# ITT-Qwen: Image To Text with Qwen VLM
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Framework](https://img.shields.io/badge/Framework-PySide6-2796EA.svg?logo=qt)
![Backend](https://img.shields.io/badge/Backend-Ollama-lightgrey.svg)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)

> A sleek, modern desktop application for advanced image analysis and chat using the Qwen Vision Language Model, powered by Ollama.

This application provides a fluid, conversational interface for users to upload images and ask detailed questions about them. It features a fully custom-themed UI built with PySide6, real-time Markdown rendering for clear and structured responses, and an advanced region-of-interest selection tool for focused analysis.

 
<img width="1200" height="800" alt="Screenshot 2025-10-01 124256" src="https://github.com/user-attachments/assets/adada672-b880-4dcd-bc01-a7cdc68d4610" />
<img width="1200" height="800" alt="Screenshot 2025-10-01 124447" src="https://github.com/user-attachments/assets/99cb867e-bef5-4574-b52f-c9fdc2f889fe" />
<img width="1200" height="800" alt="Screenshot 2025-10-01 124554" src="https://github.com/user-attachments/assets/60976aec-f2fa-4ae4-8ca6-5e7341daed47" />
<img width="1200" height="800" alt="Screenshot 2025-10-01 124625" src="https://github.com/user-attachments/assets/5c607bbe-7fb1-4b81-9b53-311626914a17" />


---

## Features

*   **Conversational AI Analysis:** Engage in a natural chat conversation about your images. The backend is powered by the **Qwen Vision Language Model** running locally via **Ollama**.
*   **Flexible Image Loading:**
    *   Drag and drop images directly into the application.
    *   Use a traditional file dialog to select images.
*   **Focused Analysis with Box Selection:**
    *   Activate "Select Area" mode to draw a bounding box around a specific region of an image.
    *   Subsequent questions will focus the AI's analysis exclusively on the content within the selected region.
*   **Full Markdown Rendering:**
    *   AI responses are beautifully rendered with support for headings, lists, bold/italic text, and more.
    *   Includes full syntax highlighting for code blocks, making technical discussions clear and readable.
*   **Modern, Custom User Interface:**
    *   A completely custom, frameless window with a dark theme built from the ground up.
    *   Polished UI elements, including custom-drawn chat bubbles with tails and drop shadows.
    *   Interactive, themed scrollbars and buttons.
*   **Robust Threading:** AI processing is handled on a separate thread, keeping the UI responsive at all times, with the ability to cancel long-running requests.

## Tech Stack

*   **Language:** Python 3.8+
*   **Framework:** PySide6 (The official Python bindings for Qt 6)
*   **AI Backend:** Ollama
*   **Vision Language Model:** Qwen VLM (`qwen2.5vl:7b`)
*   **Markdown Parsing:** `markdown` with `pygments` for syntax highlighting.

## Getting Started

Follow these instructions to get a local copy up and running.

### Prerequisites

1.  **Python:** Ensure you have Python 3.8 or newer installed.
2.  **Ollama:** You **must** have Ollama installed and running on your system. You can download it from [ollama.com](https://ollama.com/).
3.  **Qwen Model:** After installing Ollama, you need to pull the Qwen VLM. Open your terminal or command prompt and run:
    ```sh
    ollama pull qwen2.5vl:7b
    ```

### Installation

1.  **Clone the Repository:**
    ```sh
    git clone https://github.com/your-username/ITT-Qwen.git
    cd ITT-Qwen
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```sh
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    Install all required Python packages using the `requirements.txt` file.
    ```sh
    pip install -r requirements.txt
    ```
---
## A VS project file is included for quick use. Located in the files repo
---

## Usage

1.  Ensure the Ollama application is running in the background.
2.  Run the application from the root of the project directory:
    ```sh
    python ITT-Qwen.py
    ```
3.  Drag and drop an image or use the "Select Image" button.
4.  Type your question into the input field and press Enter.

## Project Architecture

The project is structured into several modules to maintain a clean separation of concerns:

*   `ITT-Qwen.py`: The main entry point of the application. Initializes the `QApplication` and the main window.
*   `main_application.py`: Contains the `ImageToTextChatApp` class, which is the core of the application, orchestrating the UI and all interactions.
*   `ui_widgets.py`: Defines all specialized UI components, such as the `ChatMessage` bubbles, `ImagePreviewWidget`, and the `SelectionImageLabel`.
*   `custom_window.py`: Implements the custom frameless `QMainWindow` and its `CustomTitleBar`.
*   `model_thread.py`: Defines the `ModelThread` class responsible for communicating with the Ollama backend on a separate thread to prevent UI freezing.
*   `config.py`: Stores static configuration data like color themes and default text.

## Future Enhancements

*   [ ] Stream responses from the model for a more interactive, real-time feel.
*   [ ] Allow selection and management of different Ollama models from within the application.
*   [ ] Implement conversation history saving and loading to a local file.
*   [ ] Support for multiple images in a single conversation.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

---

### `requirements.txt`

For convenience, here is the content of the `requirements.txt` file needed for this project.

```text
PySide6
ollama
markdown
Pygments
```
