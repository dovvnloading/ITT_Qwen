import base64
import ollama
from PySide6.QtCore import QThread, Signal

class ModelThread(QThread):
    finished = Signal(str)
    error = Signal(str)
    progress = Signal(int)
    
    def __init__(self, message_history, image_path=None):
        super().__init__()
        self.message_history = message_history
        self.image_path = image_path
        self._is_cancelled = False
    
    def cancel(self):
        self._is_cancelled = True
    
    def image_to_base64(self, image_path):
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to process image: {str(e)}")
    
    def run(self):
        try:
            if self._is_cancelled:
                return

            system_prompt = """You are Insight AI, a specialized visual assistant. Your goal is to provide clear, accurate, and well-structured information.

**Core Instructions:**
1.  **Image Analysis:** When an image is provided, your primary function is to meticulously analyze it and answer questions based *only* on the visual information present.
2.  **General Conversation:** If no image is provided, act as a helpful, general-purpose assistant.
3.  **Honesty:** If you cannot determine an answer from the image, explicitly state that the information is not available in the provided visual. Do not speculate or invent details.

**Formatting Rules:**
- You MUST format all your responses using GitHub Flavored Markdown.
- Use headings, lists, and bold text to structure your answers for maximum readability.
- For any code snippets, use fenced code blocks with appropriate language identifiers (e.g., ```python)."""
            
            ollama_messages = [{
                'role': 'system',
                'content': system_prompt
            }]

            for msg in self.message_history:
                if self._is_cancelled:
                    return
                    
                message = {
                    'role': 'user' if msg['is_user'] else 'assistant',
                    'content': msg['text']
                }
                if msg['is_user'] and msg == self.message_history[-1] and self.image_path:
                    try:
                        message['images'] = [self.image_to_base64(self.image_path)]
                    except Exception as e:
                        self.error.emit(f"Image processing failed: {str(e)}")
                        return
                ollama_messages.append(message)
            
            try:
                res = ollama.chat(
                    model='qwen2.5vl:7b',
                    messages=ollama_messages
                )
                if not self._is_cancelled:
                    self.finished.emit(res['message']['content'])
            except Exception as e:
                if not self._is_cancelled:
                    self.error.emit(f"Model processing failed: {str(e)}")
        except Exception as e:
            if not self._is_cancelled:
                self.error.emit(f"Unexpected error: {str(e)}")