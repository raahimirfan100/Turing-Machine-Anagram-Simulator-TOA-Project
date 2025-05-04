from PyQt5.QtWidgets import QWidget, QFrame
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPainter, QPolygon, QColor, QPen, QFont, QBrush, QPainterPath, QFontMetrics

from visual_settings import COLORS, SIZES, FONTS

class StateNode(QWidget):
    """a single node in our state diagram"""
    def __init__(self, name, position, is_current=False, is_terminal=False, is_accept=False, parent=None):
        super().__init__(parent)
        self.name = name
        self.position = position
        self.is_current = is_current
        self.is_terminal = is_terminal
        self.is_accept = is_accept
        self.setFixedSize(SIZES["STATE_NODE_SIZE"], SIZES["STATE_NODE_SIZE"])
        self.move(position.x() - SIZES["STATE_NODE_SIZE"]//2, position.y() - SIZES["STATE_NODE_SIZE"]//2)
        
        # tooltip to explain what the state does
        descriptions = {
            'scan_to_separator': "Searching for the # separator",
            'find_first_char': "Finding next unprocessed character in first string",
            'find_match': "Looking for matching character in second string",
            'check_second_string': "Checking if all characters in second string are matched",
            'accept': "Strings are anagrams - all characters matched",
            'reject': "Strings are NOT anagrams - found unmatched characters"
        }
        self.setToolTip(descriptions.get(name, name))
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # pick colors based on state type
        if self.is_accept:
            bg_color = QColor(COLORS["ACCEPT_STATE_BG"])
            border_color = QColor(COLORS["ACCEPT_STATE_BORDER"])
        elif self.is_terminal and not self.is_accept:
            bg_color = QColor(COLORS["REJECT_STATE_BG"])
            border_color = QColor(COLORS["REJECT_STATE_BORDER"])
        elif self.is_current:
            bg_color = QColor(COLORS["CURRENT_STATE"])
            border_color = QColor(COLORS["ARROW_COLOR"])
        else:
            bg_color = QColor(COLORS["DEFAULT_STATE_BG"])
            border_color = QColor(COLORS["DEFAULT_BORDER"])
            
        # draw the circle for this state
        painter.setBrush(QBrush(bg_color))
        
        # make terminal states have double circles
        pen_width = 2 if not self.is_current else 3
        painter.setPen(QPen(border_color, pen_width))
        
        # main circle
        radius = SIZES["STATE_RADIUS"]
        painter.drawEllipse(SIZES["STATE_NODE_SIZE"]//2 - radius, SIZES["STATE_NODE_SIZE"]//2 - radius, radius * 2, radius * 2)
        
        # second circle for terminal states
        if self.is_terminal:
            inner_radius = SIZES["INNER_RADIUS"]
            painter.drawEllipse(SIZES["STATE_NODE_SIZE"]//2 - inner_radius, SIZES["STATE_NODE_SIZE"]//2 - inner_radius, inner_radius * 2, inner_radius * 2)
            
        # show the state name
        painter.setPen(Qt.black)
        font = QFont()
        font.setPointSize(FONTS["STATE_FONT"]["SIZE"])
        font.setBold(self.is_current)
        painter.setFont(font)
        
        # split multi-word state names to fit better
        display_name = self.name.replace('_', '\n')
        
        # draw text with multi-line support
        metrics = QFontMetrics(font)
        lines = display_name.split('\n')
        line_height = metrics.height()
        
        # figure out vertical positioning
        total_height = line_height * len(lines)
        start_y = (self.height() - total_height) // 2 + line_height
        
        for i, line in enumerate(lines):
            text_rect = QRect(0, start_y + i * line_height - line_height, self.width(), line_height)
            painter.drawText(text_rect, Qt.AlignCenter, line)


class StateTransition:
    """the arrows between states showing how the machine transitions"""
    def __init__(self, from_state, to_state, label="", curved=False, curve_direction=1):
        self.from_state = from_state
        self.to_state = to_state
        self.label = label
        self.curved = curved
        self.curve_direction = curve_direction  # 1 for up, -1 for down


class StateDiagram(QWidget):
    """shows all the states and transitions in our turing machine"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(750, 400)  # big enough to fit everything
        self.current_state = "scan_to_separator"
        
        # where to put each state on the diagram
        self.state_positions = {
            "scan_to_separator": QPoint(120, 180),
            "find_first_char": QPoint(300, 100),
            "find_match": QPoint(500, 100),
            "check_second_string": QPoint(300, 280),
            "accept": QPoint(650, 100),
            "reject": QPoint(650, 280)
        }
        
        # create all the state nodes
        self.nodes = {}
        for state, pos in self.state_positions.items():
            is_terminal = state in ["accept", "reject"]
            is_accept = state == "accept"
            self.nodes[state] = StateNode(
                state, pos, 
                is_current=(state == self.current_state),
                is_terminal=is_terminal,
                is_accept=is_accept, 
                parent=self
            )
            
        # set up all the transitions between states
        self.transitions = [
            StateTransition("scan_to_separator", "find_first_char", "Found separator"),
            StateTransition("find_first_char", "find_match", "Process char"),
            StateTransition("find_match", "find_first_char", "Found match", curved=True, curve_direction=1),
            StateTransition("find_first_char", "check_second_string", "First string done"),
            StateTransition("check_second_string", "accept", "All matched"),
            StateTransition("check_second_string", "reject", "Unmatched char"),
            StateTransition("find_match", "reject", "No match found"),
        ]
        
        # where to put labels on arrows (above or below)
        self.label_positions = {
            "scan_to_separator_find_first_char": "above",
            "find_first_char_find_match": "below",
            "find_match_find_first_char": "above",
            "find_first_char_check_second_string": "below",
            "check_second_string_accept": "above",
            "check_second_string_reject": "below",
            "find_match_reject": "below",
        }
        
    def set_state(self, state):
        """updates which state is currently active"""
        if state == self.current_state:
            return
            
        # update all nodes
        for node_state, node in self.nodes.items():
            node.is_current = (node_state == state)
            node.update()
            
        self.current_state = state
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # draw transitions first so they're behind the nodes
        for trans in self.transitions:
            from_pos = self.state_positions[trans.from_state]
            to_pos = self.state_positions[trans.to_state]
            self._draw_transition(painter, trans, from_pos, to_pos)
            
        # draw the legend to explain the colors
        self._draw_legend(painter)
        
    def _draw_transition(self, painter, trans, from_pos, to_pos):
        """draws an arrow between states"""
        # figure out the direction
        dx = to_pos.x() - from_pos.x()
        dy = to_pos.y() - from_pos.y()
        length = (dx*dx + dy*dy) ** 0.5
        
        if length < 0.1:
            return  # skip self-loops for now
            
        # normalize direction
        dx, dy = dx/length, dy/length
        
        # calculate where to start and end the arrow (at edge of circles)
        node_radius = SIZES["STATE_RADIUS"]
        start_x = from_pos.x() + dx * node_radius
        start_y = from_pos.y() + dy * node_radius
        end_x = to_pos.x() - dx * node_radius
        end_y = to_pos.y() - dy * node_radius
        
        # figure out if label goes above or below
        transition_key = f"{trans.from_state}_{trans.to_state}"
        label_position = self.label_positions.get(transition_key, "above")
        position_multiplier = -1 if label_position == "above" else 1  # -1 = up, 1 = down
        
        # create the path for drawing
        path = QPainterPath()
        path.moveTo(start_x, start_y)
        
        if trans.curved:
            # make a curved arrow
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            
            # offset to make a nice curve
            offset = SIZES["CURVE_OFFSET"] * trans.curve_direction
            perp_x = -dy * offset
            perp_y = dx * offset
            
            ctrl_x = mid_x + perp_x
            ctrl_y = mid_y + perp_y
            
            # draw curved path
            path.quadTo(ctrl_x, ctrl_y, end_x, end_y)
            
            # figure out where to put the label
            t = 0.5  # middle of curve
            label_x = (1-t)*(1-t)*start_x + 2*(1-t)*t*ctrl_x + t*t*end_x
            label_y = (1-t)*(1-t)*start_y + 2*(1-t)*t*ctrl_y + t*t*end_y
            
            # tweak label position a bit
            fine_tune_offset = position_multiplier * 10
            label_y += fine_tune_offset
        else:
            # straight line
            path.lineTo(end_x, end_y)
            
            # put label in middle of line
            label_x = (start_x + end_x) / 2
            label_y = (start_y + end_y) / 2
            
            # offset label a bit
            offset = position_multiplier * 15
            label_y += offset
        
        # draw the path
        painter.setPen(QPen(QColor(COLORS["ARROW_COLOR"]), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawPath(path)
        
        # draw arrowhead
        angle = 3.14159 / 6  # 30 degrees
        if trans.curved:
            # for curves, calculate tangent at endpoint
            dx = end_x - ctrl_x
            dy = end_y - ctrl_y
            length = (dx*dx + dy*dy) ** 0.5
            dx, dy = dx/length, dy/length
            
        a1_x = end_x - SIZES["ARROW_WIDTH"] * (dx * 0.866 + dy * 0.5)
        a1_y = end_y - SIZES["ARROW_WIDTH"] * (dy * 0.866 - dx * 0.5)
        a2_x = end_x - SIZES["ARROW_WIDTH"] * (dx * 0.866 - dy * 0.5)
        a2_y = end_y - SIZES["ARROW_WIDTH"] * (dy * 0.866 + dx * 0.5)
        
        # make the arrowhead
        arrow = QPolygon()
        arrow.append(QPoint(int(end_x), int(end_y)))
        arrow.append(QPoint(int(a1_x), int(a1_y)))
        arrow.append(QPoint(int(a2_x), int(a2_y)))
        
        painter.setBrush(QBrush(QColor(COLORS["ARROW_COLOR"])))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(arrow)
        
        # add the label
        if trans.label:
            font = QFont()
            font.setPointSize(FONTS["LABEL_FONT"]["SIZE"])
            painter.setFont(font)
            
            # figure out how big the text is
            metrics = QFontMetrics(font)
            text_width = metrics.horizontalAdvance(trans.label)
            text_height = metrics.height()
            
            # bit of padding around text
            padding = SIZES["LABEL_PADDING"] - 1
            
            # make a semi-transparent background
            bg_color = QColor(255, 255, 255)
            bg_color.setAlpha(230)
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(QColor(COLORS["DEFAULT_BORDER"]), 1))
            
            # create a box for the label
            label_rect = QRect(
                int(label_x - text_width/2 - padding), 
                int(label_y - text_height/2 - padding/2), 
                text_width + padding*2, 
                text_height + padding
            )
            
            # draw rounded rectangle for label
            painter.drawRoundedRect(label_rect, 5, 5)
            
            # add the text
            painter.setPen(Qt.black)
            painter.drawText(
                int(label_x - text_width/2), 
                int(label_y + text_height/3), 
                trans.label
            )
                           
    def _draw_legend(self, painter):
        """draws a little box explaining what the different state colors mean"""
        # make a background for the legend
        painter.setBrush(QBrush(QColor(255, 255, 255, 230)))
        painter.setPen(QPen(Qt.lightGray, 1))
        legend_rect = QRect(10, 10, 140, 85)
        painter.drawRoundedRect(legend_rect, 5, 5)
        
        painter.setPen(QPen(Qt.black, 1))
        font = QFont()
        font.setPointSize(FONTS["LEGEND_FONT"]["SIZE"])
        painter.setFont(font)
        
        # legend title
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(20, 25, "state types")
        font.setBold(False)
        painter.setFont(font)
        
        y_pos = 40
        spacing = 22
        
        # current state
        painter.setBrush(QBrush(QColor(COLORS["CURRENT_STATE"])))
        painter.setPen(QPen(QColor(COLORS["ARROW_COLOR"]), 2))
        painter.drawEllipse(20, y_pos - 8, 16, 16)
        painter.setPen(Qt.black)
        painter.drawText(45, y_pos + 4, "current state")
        
        # accept state
        y_pos += spacing
        painter.setBrush(QBrush(QColor(COLORS["ACCEPT_STATE_BG"])))
        painter.setPen(QPen(QColor(COLORS["ACCEPT_STATE_BORDER"]), 1))
        painter.drawEllipse(20, y_pos - 8, 16, 16)
        painter.drawEllipse(22, y_pos - 6, 12, 12)
        painter.setPen(Qt.black)
        painter.drawText(45, y_pos + 4, "accept state")
        
        # reject state
        y_pos += spacing
        painter.setBrush(QBrush(QColor(COLORS["REJECT_STATE_BG"])))
        painter.setPen(QPen(QColor(COLORS["REJECT_STATE_BORDER"]), 1))
        painter.drawEllipse(20, y_pos - 8, 16, 16)
        painter.drawEllipse(22, y_pos - 6, 12, 12)
        painter.setPen(Qt.black)
        painter.drawText(45, y_pos + 4, "reject state")