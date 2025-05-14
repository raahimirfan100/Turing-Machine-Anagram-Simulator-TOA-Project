from PyQt5.QtWidgets import (QTextEdit, QWidget, QHBoxLayout, QLabel, QVBoxLayout, 
                         QPushButton, QSlider, QGridLayout, QLineEdit, 
                         QGroupBox, QFrame, QSplitter,
                         QMainWindow)
from PyQt5.QtCore import Qt, QPoint, QTimer, QRect
from PyQt5.QtGui import QPainter, QPolygon, QColor, QPen, QFont, QBrush

from turing_machine import TuringMachine
from state_diagram import StateDiagram
from visual_settings import COLORS, SIZES

# common fonts
def get_cell_font():
    font = QFont()
    font.setPointSize(SIZES["CELL_FONT_SIZE"])
    font.setBold(True)
    return font


class TapeCell(QFrame):
    """each individual cell on our turing machine tape"""
    def __init__(self, symbol='_', is_head=False, parent=None):
        super().__init__(parent)
        self.symbol = symbol
        self.is_head = is_head
        self.setFixedSize(SIZES["CELL_SIZE"], SIZES["CELL_SIZE"])
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Plain)
        self.update_style()
        
        # tooltip to explain what's in the cell
        self.setToolTip(self.get_tooltip())
        
    def get_tooltip(self):
        """makes a helpful tooltip based on what's in the cell"""
        tooltips = {
            '_': "Blank cell (empty)",
            '*': "Processed character from first string",
            'X': "Matched character in second string",
            '$': "Separator between strings (originally '#')"
        }
        return tooltips.get(self.symbol, f"character: {self.symbol}")
        
    def update_style(self):
        """updates how the cell looks based on what it contains"""
        base_style = "QFrame { font-size: 18px; font-weight: bold; border: 2px solid black; }"
        
        if self.is_head:
            self.setStyleSheet(base_style + f"background-color: {COLORS['CURRENT_STATE']}; border: 3px solid {COLORS['HEAD_POINTER']};")
            return
            
        # color coding for different symbols
        color = COLORS["DEFAULT_STATE_BG"]  # default white
        
        if self.symbol == '_':
            color = COLORS["BLANK_CELL"]  # light gray for blank cells
        elif self.symbol == '*':
            color = COLORS["PROCESSED_CHAR"]  # light red for processed chars in first string
        elif self.symbol == 'X':
            color = COLORS["MATCHED_CHAR"]  # light green for matched chars in second string
        elif self.symbol == '$':
            color = COLORS["SEPARATOR"]  # light blue for separator
            
        self.setStyleSheet(f"{base_style} background-color: {color};")
    
    def set_symbol(self, symbol):
        self.symbol = symbol
        self.update_style()
        self.setToolTip(self.get_tooltip())
        self.update()
    
    def set_head(self, is_head):
        self.is_head = is_head
        self.update_style()
        self.update()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # draw the symbol in the middle of the cell
        painter.setPen(Qt.black)
        painter.setFont(get_cell_font())
        
        painter.drawText(self.rect(), Qt.AlignCenter, self.symbol)
        
        # add a box if this cell is where the head is
        if self.is_head:
            painter.setPen(QPen(QColor(COLORS["HEAD_POINTER"]), 2))
            rect = QRect(2, 2, self.width()-4, self.height()-4)
            painter.drawRect(rect)


class HeadPointer(QWidget):
    """the little arrow that shows where the head is"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # draw the arrow pointing up
        width = self.width()
        arrow = QPolygon()
        arrow.append(QPoint(width // 2, 5))  # tip of arrow
        arrow.append(QPoint(width // 2 - SIZES["ARROW_WIDTH"], 30))  # bottom left
        arrow.append(QPoint(width // 2 + SIZES["ARROW_WIDTH"], 30))  # bottom right
        
        painter.setBrush(QBrush(QColor(COLORS["HEAD_POINTER"])))  # use color from constants
        painter.setPen(QPen(Qt.black, 2))
        painter.drawPolygon(arrow)



class TuringMachineSimulator(QMainWindow):
    def __init__(self, tape_string):
        super().__init__()
        self.machine = TuringMachine(tape_string)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.auto_step)
        self.auto_speed = 1000  # default 1 second per step
        
        # central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.initUI()
        self.showMaximized()
        
    def initUI(self):
        self.setWindowTitle("Turing Machine Anagram Simulator")
        self.setMinimumSize(900, 700)
        
        # main layout
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        #-------------------------
        # input & header section
        #-------------------------
        header_layout = QHBoxLayout()
        
        # input controls
        input_group = QGroupBox("Input Strings")
        input_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
                
            }
        """)

        input_layout = QGridLayout()
        input_group.setLayout(input_layout)
        
        input_layout.addWidget(QLabel("String 1:"), 0, 0)
        self.string1_input = QLineEdit()
        self.string1_input.setMinimumWidth(150)
        self.string1_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS["BLANK_CELL"]};
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: #333;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS["SUCCESS_TEXT"]};
                background-color: {COLORS["DEFAULT_STATE_BG"]};
            }}
        """)

        input_layout.addWidget(self.string1_input, 0, 1)
        
        input_layout.addWidget(QLabel("String 2:"), 1, 0)
        self.string2_input = QLineEdit()
        self.string2_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS["BLANK_CELL"]};
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: #333;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS["SUCCESS_TEXT"]};
                background-color: {COLORS["DEFAULT_STATE_BG"]};
            }}
        """)
        input_layout.addWidget(self.string2_input, 1, 1)
        
        self.load_button = QPushButton("Load Strings")
        self.load_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["SUCCESS_TEXT"]};
                color: white;
                border: 2px solid {COLORS["SUCCESS_TEXT"]};
                border-radius: 4px;
                padding: 8px 16px;
                height: 60px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: white;
                color: {COLORS["SUCCESS_TEXT"]};
            }}
        """)

        self.load_button.clicked.connect(self.load_strings)
        input_layout.addWidget(self.load_button, 0, 2, 2, 1)
        
        # try to get the strings from what's already on the tape
        if '#' in ''.join(self.machine.tape):
            tape_str = ''.join(self.machine.tape).strip('_')
            parts = tape_str.split('$' if '$' in tape_str else '#')
            if len(parts) >= 2:
                self.string1_input.setText(parts[0].strip('_'))
                self.string2_input.setText(parts[1].strip('_'))
        
        header_layout.addWidget(input_group)
        
        # current state display
        state_box = QGroupBox("Current State")
        state_layout = QVBoxLayout()
        state_box.setFixedWidth(280)  # or whatever width you want
        state_box.setLayout(state_layout)
        
        self.state_label = QLabel(f"<b>{self.machine.state.replace('_', ' ').title()}</b>")
        self.state_label.setAlignment(Qt.AlignCenter)
        self.state_label.setStyleSheet("font-size: 16px; text-transform: uppercase; letter-spacing: 1px;")
        state_layout.addWidget(self.state_label)
        
        header_layout.addWidget(state_box)
        
        main_layout.addLayout(header_layout)
        #-------------------------
        # tape section
        #-------------------------
        tape_section = QGroupBox("Turing Machine Tape")
        tape_layout = QVBoxLayout()
        tape_section.setLayout(tape_layout)

        # tape visualization (no scroll)
        tape_container = QWidget()
        self.tape_layout = QHBoxLayout(tape_container)
        self.tape_layout.setAlignment(Qt.AlignCenter)
        self.tape_layout.setContentsMargins(0, 0, 0, 0)  # no extra margins
        self.tape_layout.setSpacing(0)  # no spacing between cells

        # add the tape container to the layout
        tape_layout.addWidget(tape_container)

        # create cells
        self.cells = []  # clear cells before refreshing
        self.refresh_tape()

        # head pointer below tape
        head_layout = QHBoxLayout()
        head_layout.setAlignment(Qt.AlignCenter)
        head_layout.setContentsMargins(0, 0, 0, 0)  # no margins
        head_layout.setSpacing(0)  # no spacing
        self.head_pointer = HeadPointer()
        self.head_pointer.setFixedWidth(50)
        self.head_pointer.setFixedHeight(25)  # shorter arrow looks better
        head_layout.addWidget(self.head_pointer)

        # add head pointer layout below the tape
        tape_layout.addLayout(head_layout)

        # add the tape section to the main layout
        main_layout.addWidget(tape_section)

        #-------------------------
        # controls section
        #-------------------------
        controls_group = QGroupBox("Controls")
        controls_layout = QGridLayout()
        controls_group.setLayout(controls_layout)
        
        # control buttons
        self.step_button = QPushButton("Next Step")
        self.step_button.setMinimumHeight(SIZES["BUTTON_HEIGHT"])
        self.step_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #4A90E2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #357ABD;
            }}
            QPushButton:pressed {{
                background-color: #2C5AA0;
            }}
        """)
        self.step_button.clicked.connect(self.do_step)
        controls_layout.addWidget(self.step_button, 0, 0)
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.setMinimumHeight(SIZES["BUTTON_HEIGHT"])
        self.reset_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["ERROR_TEXT"]};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #C0392B;
            }}
            QPushButton:pressed {{
                background-color: #A93226;
            }}
        """)

        self.reset_button.clicked.connect(self.reset_machine)
        controls_layout.addWidget(self.reset_button, 0, 1)
        
        self.auto_button = QPushButton("Auto Run")
        self.auto_button.setMinimumHeight(SIZES["BUTTON_HEIGHT"])
        self.auto_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["SUCCESS_TEXT"]};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #229954;
            }}
            QPushButton:pressed {{
                background-color: #1E8449;
            }}
        """)

        self.auto_button.setCheckable(True)
        self.auto_button.clicked.connect(self.toggle_auto)
        controls_layout.addWidget(self.auto_button, 0, 2)
        
        # speed control
        controls_layout.addWidget(QLabel("Speed:"), 1, 0)
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 20)  # 1 = slow, 20 = fast
        self.speed_slider.setValue(5)
        self.speed_slider.valueChanged.connect(self.update_speed)
        controls_layout.addWidget(self.speed_slider, 1, 1, 1, 2)
        
        main_layout.addWidget(controls_group)
        
        #-------------------------
        # bottom section (state diagram & explanation)
        #-------------------------
        bottom_splitter = QSplitter(Qt.Horizontal)
        bottom_splitter.setHandleWidth(10)
        
        # state diagram
        state_group = QGroupBox("State Diagram")
        state_layout = QVBoxLayout()
        state_group.setLayout(state_layout)
        
        self.state_diagram = StateDiagram(self.machine)
        state_layout.addWidget(self.state_diagram)
        
        bottom_splitter.addWidget(state_group)
        
        # explanation and logging panel
        log_group = QGroupBox("Execution Log & Explanation")
        log_layout = QVBoxLayout()
        log_group.setLayout(log_layout)
        
        self.explanation = QTextEdit()
        self.explanation.setReadOnly(True)
        self.explanation.setMinimumHeight(150)
        self.explanation.setStyleSheet("font-size: 14px;")
        log_layout.addWidget(self.explanation)
        
        bottom_splitter.addWidget(log_group)
        
        # adjust splitter sizes
        bottom_splitter.setSizes([500, 400])
        main_layout.addWidget(bottom_splitter)
        
        # initial explanation
        self.update_explanation("The Turing Machine is ready to check if the two strings are anagrams.\n\n" +
                               "Initially, the machine is in 'scan_to_separator' state and will move right " +
                               "until it finds the # separator. It will then mark the separator as $ and " +
                               "start processing characters from the first string.")
        
        # initial state visualization
        self.state_diagram.set_state(self.machine.state)
        
    def refresh_tape(self):
        """recreates all the cells on the tape"""
        # clear existing cells
        for cell in self.cells:
            self.tape_layout.removeWidget(cell)
            cell.deleteLater()
        self.cells.clear()
        
        # create new cells for the tape
        for i, char in enumerate(self.machine.tape):
            cell = TapeCell(char, i == self.machine.head_position)
            self.tape_layout.addWidget(cell)
            self.cells.append(cell)
        
        # make sure we can see the head
        self._scroll_to_head()
    
    def update_cells(self):
        """updates the cells without recreating them all"""
        for i, (cell, char) in enumerate(zip(self.cells, self.machine.tape)):
            cell.set_symbol(char)
            cell.set_head(i == self.machine.head_position)
        
        # update the head pointer position
        if self.machine.head_position < len(self.cells):
            # figure out where the cell is
            cell_width = SIZES["CELL_SIZE"]
            
            # position the arrow under the current cell
            container_widget = self.tape_layout.parentWidget()
            if container_widget:
                # get the global position of the head cell
                head_cell = self.cells[self.machine.head_position]
                head_pos = head_cell.mapTo(head_cell.window(), QPoint(0, 0))
                
                # position the head pointer centered under the current head cell
                parent_pos = self.head_pointer.parentWidget().mapFrom(head_cell.window(), head_pos)
                self.head_pointer.move(
                    parent_pos.x() + (cell_width - self.head_pointer.width()) // 2,  # center the arrow 
                    self.head_pointer.y()
                )
        
        # make sure we can see the head
        self._scroll_to_head()
            
    def _scroll_to_head(self):
        """makes sure the head is visible by scrolling to it"""
        if self.machine.head_position < len(self.cells):
            cell_width = SIZES["CELL_SIZE"]  # width of each cell
            parent = self.tape_layout.parent().parent()  # get the scroll area
            if hasattr(parent, 'horizontalScrollBar'):
                scroll_pos = max(0, (self.machine.head_position - 4) * cell_width)
                parent.horizontalScrollBar().setValue(scroll_pos)
    
    def do_step(self):
        """runs one step of the turing machine"""
        original_state = self.machine.state.replace('_', ' ').title()
        original_position = self.machine.head_position
        original_symbol = self.machine.read()
        
        # do one step
        self.machine.step()
        
        # update ui
        new_state = self.machine.state.replace('_', ' ').title()
        new_position = self.machine.head_position
        new_symbol = self.machine.read()
        
        # update the visualization
        self.update_cells()
        self.state_diagram.set_state(new_state)
        self.state_label.setText(f"<b>{new_state}</b>")
        
        # explain what happened
        explanation_parts = []
        
        if new_state != original_state:
            explanation_parts.append(f"<b>State transition:</b> {original_state} → {new_state}")
        else:
            explanation_parts.append(f"<b>Remaining in state:</b> {new_state}")
            
        if new_position > original_position:
            explanation_parts.append("<b>Head moved:</b> RIGHT")
        elif new_position < original_position:
            explanation_parts.append("<b>Head moved:</b> LEFT")
        else:
            explanation_parts.append("<b>Head position:</b> unchanged")
            
        if self.machine.tape[original_position] != original_symbol:
            explanation_parts.append(f"<b>Write:</b> Changed '{original_symbol}' to '{self.machine.tape[original_position]}'")
            explanation_parts.append(f"<b>Current symbol:</b> '{new_symbol}'")
        if new_state == 'accept':
            explanation_parts.append("\n<span style='color:green; font-weight:bold;'>✅ SUCCESS! The strings are anagrams.</span>")
            # stop auto-run immediately if active
            if self.timer.isActive():
                self.timer.stop()
                self.auto_button.setChecked(False)
                self.toggle_auto()
        elif new_state == 'reject':
            explanation_parts.append("\n<span style='color:red; font-weight:bold;'>❌ REJECTED! The strings are not anagrams.</span>")
            # stop auto-run immediately if active
            if self.timer.isActive():
                self.timer.stop()
                self.auto_button.setChecked(False)
                self.toggle_auto()
            
        self.update_explanation("<br>".join(explanation_parts))
        return new_state not in ['accept', 'reject']
        
    def auto_step(self):
        """runs a step in auto mode"""
        # check if we're already in a terminating state before doing another step
        if self.machine.state in ['accept', 'reject']:
            self.timer.stop()
            self.auto_button.setChecked(False)
            self.toggle_auto()
            return
            
        # run a step and check if we should continue
        if not self.do_step():
            self.auto_button.setChecked(False)
            self.toggle_auto()
    
    def toggle_auto(self):
        """turns auto mode on/off"""
        if self.auto_button.isChecked():
            self.timer.start(self.auto_speed)
            self.auto_button.setText("Stop")
            self.step_button.setEnabled(False)
            self.reset_button.setEnabled(False)
            self.load_button.setEnabled(False)
        else:
            self.timer.stop()
            self.auto_button.setText("Auto Run")
            self.step_button.setEnabled(True)
            self.reset_button.setEnabled(True)
            self.load_button.setEnabled(True)
    
    def update_speed(self):
        """changes how fast the auto-step goes"""
        # convert slider value (1-20) to milliseconds (2000-100)
        speed_value = self.speed_slider.value()
        self.auto_speed = int(2100 - speed_value * 100)

        self.timer.setInterval(self.auto_speed)
    
    def load_strings(self):
        """loads new strings into the machine"""
        string1 = self.string1_input.text()
        string2 = self.string2_input.text()
        if string1 and string2:
            new_input = f"{string1}#{string2}"
            self.reset_machine(new_input)
    
    def reset_machine(self, new_input=None):
        """resets everything back to the starting state"""
        # stop auto if it's running
        if self.timer.isActive():
            self.auto_button.setChecked(False)
            self.toggle_auto()
            
        # make a new machine with either the current strings or new input
        if new_input:
            self.machine = TuringMachine(new_input)
        else:
            current_input = f"{self.string1_input.text()}#{self.string2_input.text()}"
            self.machine = TuringMachine(current_input)
            
        # reset ui
        self.refresh_tape()
        self.state_diagram.tm = self.machine
        self.state_diagram.set_state(self.machine.state)
        self.state_label.setText(f"<b>{self.machine.state}</b>")
        
        # initial explanation
        self.update_explanation(
            "Machine reset. Ready to check if the two strings are anagrams.<br><br>" +
            "Initially, the machine is in <b>scan_to_separator</b> state and will move right " +
            "until it finds the # separator. It will then mark the separator as $ and " +
            "start processing characters from the first string.<br><br>" +
            "<b>Algorithm explanation:</b><br>" +
            "1. Find and mark the separator between the two strings<br>" +
            "2. For each character in the first string:<br>" +
            "&nbsp;&nbsp;- Mark it as processed (*)<br>" +
            "&nbsp;&nbsp;- Find a matching character in the second string<br>" +
            "&nbsp;&nbsp;- Mark the match as processed (X)<br>" +
            "3. Check that all characters in the second string are matched<br>" +
            "4. If all characters are matched, the strings are anagrams"
        )
    
    def update_explanation(self, text):
        """updates the explanation text"""
        self.explanation.setHtml(text)