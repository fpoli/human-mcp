from mcp.server.fastmcp import FastMCP
from pathlib import Path
from loguru import logger
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QTextEdit, QPushButton, QFrame
from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import Qt
import markdown

# Go up one level from the package directory to get to the project root
project_root = Path(__file__).parent.parent
logger.add(project_root / "server.log", retention="30 days", level="DEBUG")

mcp = FastMCP("oracle")

application_name = "Human Oracle MCP"

class OracleWindow(QMainWindow):
    """A Qt window to display a question and get an answer from the user."""
    def __init__(self, question):
        super().__init__()
        self.answer = ""
        self.setWindowTitle(application_name)

        central_widget = QFrame()
        central_widget.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        html = markdown.markdown(question)
        self.question_label = QLabel(html)
        self.question_label.setTextFormat(Qt.RichText)
        self.question_label.setWordWrap(True)
        self.layout.addWidget(self.question_label)

        self.text_area = QTextEdit()
        self.layout.addWidget(self.text_area)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.on_submit)
        self.layout.addWidget(self.submit_button)

    def on_submit(self):
        """Saves the user's answer and closes the application."""
        self.answer = self.text_area.toPlainText().strip()
        self.close()
        QCoreApplication.quit()


@mcp.tool()
def ask(question: str) -> str:
    """Ask a question to an expert, but expensive, oracle.

    The question must be fully self-contained but concise. It should not waste the precious oracle's time, yet it should be detailed enough to maximize the value of the answer.

    The question and the answer can either be formatted in plain text or markdown.
    """
    logger.debug(f"Asked oracle: {question}")
    
    # Get the current QApplication instance, or create one if it doesn't exist.
    # This is necessary because there can only be one QApplication instance per process.
    app = QApplication.instance()
    if app is None:
        # Set the application name for better desktop integration (e.g., taskbar grouping).
        QCoreApplication.setApplicationName(application_name)
        app = QApplication(sys.argv)

    # Create and show the oracle window, then start the event loop.
    # The application will block here until the user submits an answer or closes the window.
    window = OracleWindow(question)
    window.show()
    app.exec()

    answer = window.answer
    logger.debug(f"Oracle answered: {answer}")
    return answer


def run_server():
    mcp.run()
