# PyQt5 imports
from PyQt5.QtWidgets import QMessageBox, QTextEdit, QFileDialog, QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCharFormat, QSyntaxHighlighter, QColor

# self-defined modules
from modules.styling import context_menu_stylesheet
from modules.utils import add_spaces_for_context_menu

# python libraries
import pyperclip


class ScriptingTextEdit(QTextEdit):
    def __init__(self, mainTool):
        super().__init__()
        
        self.mainTool = mainTool
        self.highlighter = KeywordHighlighter(self.document())
        self.setFixedHeight(self.mainTool.app_size * 7)

    def export_script(self):
        file_path, _ = QFileDialog.getSaveFileName(parent=self, caption='Export Script',
                                                    directory='code.txt', filter="Text Files (*.txt)")
        with open(file_path, 'w') as file:
            file.write(self.toPlainText())
        self.setFocus()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        text_to_add = add_spaces_for_context_menu('Copy All', 'Ctrl + L')
        action1 = menu.addAction(text_to_add)
        text_to_add = add_spaces_for_context_menu('Paste', 'Ctrl + V')
        action2 = menu.addAction(text_to_add)
        action4 = menu.addAction('Clear')
        menu.addSeparator()
        action6 = menu.addAction('Import Script')
        text_to_add = add_spaces_for_context_menu('Export Script', 'Ctrl + E')
        action5 = menu.addAction(text_to_add)
        action3 = menu.addAction("Help")
        menu.addSeparator()
        actione = menu.addAction("Back")
        context_menu_stylesheet(menu, self.mainTool)

        action = menu.exec_(event.globalPos())
        if action is None: return
        elif action == action2:
            self.insertPlainText(pyperclip.paste())
        elif action == action1:
            pyperclip.copy(self.toPlainText())
        elif action == action4:
            if (self.toPlainText().strip() and QMessageBox.warning(self, "PyAutoMate", 
                "The entire script will be cleared. Continue?", QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No)) == QMessageBox.Yes:
                self.clear()
            self.setFocus()
        elif action == action5 and self.toPlainText().strip():
            self.export_script()
        elif action == action6:
            file_path, _ = QFileDialog.getOpenFileName(parent=self, caption='Select Code File', filter="Text Files (*.txt)")
            with open(file_path, 'r') as file:
                content = file.read()
                self.insertPlainText(content)
            self.setFocus()
        elif action == actione:
            if (self.toPlainText().strip() and QMessageBox.warning(self, "PyAutoMate", 
                "The script will be discarded. Continue?", QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No)) == QMessageBox.Yes or not self.toPlainText().strip():
                self.reject()
            else:
                self.setfocus()

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_L:
                pyperclip.copy(self.toPlainText())
            elif event.key() == Qt.Key_E:
                self.export_script()
        else:
            super().keyPressEvent(event)

""" Keyword Highlighter Class for the scripting textEdit """

class KeywordHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.keywords = ["click", "wait", "open", "show", "keyboard"]
        # Format for keywords
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor(44, 122, 214))

        # Format for arguments after the keyword
        self.argument_format = QTextCharFormat()
        self.argument_format.setForeground(QColor(150, 75, 0))

    def highlightBlock(self, text):
        """Highlight only the first occurrence of a keyword per line."""
        for keyword in self.keywords:
            start = 0
            while start < len(text):
                start = text.find(keyword, start)
                if start == -1:
                    break  # No keyword found, move to next keyword
                # Find the end of the line
                end_of_line = text.find("\n", start)
                if end_of_line == -1:
                    end_of_line = len(text)

                # Apply keyword format to the first occurrence
                self.setFormat(start, len(keyword), self.keyword_format)
                # Apply argument format to the rest of the line after the first keyword
                arg_start = start + len(keyword) + 1
                if arg_start < end_of_line:
                    self.setFormat(arg_start, end_of_line - arg_start, self.argument_format)
                break  # Stop after the first occurrence per line
