from PyQt5.QtWidgets import QWidget, QFrame, QApplication
from PyQt5.QtCore import Qt, QPoint, QRect, QRectF
from PyQt5.QtGui import QPainter, QPolygon, QColor, QPen, QFont, QBrush, QPainterPath, QFontMetrics
import sys
import math

# visual settings similar to the provided code
COLORS = {
    "DEFAULT_STATE_BG": "#f0f0f0",
    "DEFAULT_BORDER": "#666666",
    "CURRENT_STATE": "#a0d2eb",
    "ARROW_COLOR": "#3366cc",
    "ACCEPT_STATE_BG": "#c8e6c9",
    "ACCEPT_STATE_BORDER": "#2e7d32",
    "REJECT_STATE_BG": "#ffcdd2",
    "REJECT_STATE_BORDER": "#c62828"
}

SIZES = {
    "STATE_NODE_SIZE": 90,
    "STATE_RADIUS": 40,
    "INNER_RADIUS": 30,
    "ARROW_WIDTH": 12,
    "LABEL_PADDING": 6,
    "CURVE_OFFSET": 50
}

FONTS = {
    "STATE_FONT": {"SIZE": 8},
    "LABEL_FONT": {"SIZE": 8},
    "LEGEND_FONT": {"SIZE": 8}
}

class StateNode(QWidget):
    """A node in the state diagram representing a single state"""
    def __init__(self, name, turing_machine, position, is_current=False, is_terminal=False, is_accept=False, parent=None):
        super().__init__(parent)
        self.name = name
        self.tm = turing_machine
        self.position = position
        self.is_current = is_current
        self.is_terminal = is_terminal
        self.is_accept = is_accept
        self.setFixedSize(SIZES["STATE_NODE_SIZE"], SIZES["STATE_NODE_SIZE"])
        self.move(position.x() - SIZES["STATE_NODE_SIZE"]//2, position.y() - SIZES["STATE_NODE_SIZE"]//2)
        
        # tooltip to explain what the state does
        descriptions = {
            'scan_to_separator': "Initial state - Scanning to separator",
            'find_first_char': "Finding first character",
            'found_first_char': "Found first character",
            'scanback_to_separator': "Scanning back to separator",
            'match_char': "Matching character",
            'found_char': "Found matching character",
            'accept': "Accept state - Strings match",
            'reject': "Reject state - Strings don't match"
        }
        self.setToolTip(descriptions.get(name, name))
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        is_current = (self.name == self.tm.getState())
        is_accept = (self.name == "accept")
        is_reject = (self.name == "reject")

        # pick colors based on state type
        if is_accept:
            bg_color = QColor(COLORS["ACCEPT_STATE_BG"])
            border_color = QColor(COLORS["ACCEPT_STATE_BORDER"])
        elif is_reject:
            bg_color = QColor(COLORS["REJECT_STATE_BG"])
            border_color = QColor(COLORS["REJECT_STATE_BORDER"])
        elif is_current:
            bg_color = QColor(COLORS["CURRENT_STATE"])
            border_color = QColor(COLORS["ARROW_COLOR"])
        else:
            bg_color = QColor(COLORS["DEFAULT_STATE_BG"])
            border_color = QColor(COLORS["DEFAULT_BORDER"])    
            # draw the state circle
        painter.setBrush(QBrush(bg_color))
        
        # make terminal states have double circles
        pen_width = 2 if not self.is_current else 3
        painter.setPen(QPen(border_color, pen_width))
        
        # main circle
        radius = SIZES["STATE_RADIUS"]
        painter.drawEllipse(SIZES["STATE_NODE_SIZE"]//2 - radius, SIZES["STATE_NODE_SIZE"]//2 - radius, radius * 2, radius * 2)
        
        # second circle for terminal states
        if self.is_terminal:
            inner_radius = SIZES["INNER_RADIUS"]            # fill the ring between outer and inner circles for current terminal states (accept/reject)
            if self.is_terminal and is_current:
                # save current brush and create a new one for the ring
                old_brush = painter.brush()
                ring_color = QColor(border_color)
                # make the color slightly lighter
                h, s, v, a = ring_color.getHsv()
                v = min(255, int(v * 3))  # increase brightness
                ring_color.setHsv(h, s, v, a)
                
                ring_brush = QBrush(ring_color)
                painter.setBrush(ring_brush)
                ring_path = QPainterPath()
                # outer circle
                ring_path.addEllipse(SIZES["STATE_NODE_SIZE"]//2 - radius, SIZES["STATE_NODE_SIZE"]//2 - radius, radius * 2, radius * 2)
                # subtract inner circle (creates a hole)
                inner_path = QPainterPath()
                inner_path.addEllipse(SIZES["STATE_NODE_SIZE"]//2 - inner_radius, SIZES["STATE_NODE_SIZE"]//2 - inner_radius, inner_radius * 2, inner_radius * 2)
                ring_path = ring_path.subtracted(inner_path)
                
                # fill the ring path
                painter.drawPath(ring_path)
                painter.setBrush(old_brush)
            
            # draw the inner circle
            painter.drawEllipse(SIZES["STATE_NODE_SIZE"]//2 - inner_radius, SIZES["STATE_NODE_SIZE"]//2 - inner_radius, inner_radius * 2, inner_radius * 2)
            
        # display the state name
        painter.setPen(Qt.black if is_current else Qt.black)
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
    """Enhanced visualization of the state machine with 8 states"""
    def __init__(self, turing_machine, parent=None):
        super().__init__(parent)
        self.setMinimumSize(900, 500)  # increased size for better spacing
        self.current_state = "scan_to_separator"
        self.tm = turing_machine
        # State positions arranged in a more logical flow
        self.state_positions = {
            "scan_to_separator": QPoint(100, 150),
            "find_first_char": QPoint(250, 150),
            "found_first_char": QPoint(400, 150),
            "scanback_to_separator": QPoint(550, 150),
            "match_char": QPoint(550, 300),
            "found_char": QPoint(400, 300),
            "accept": QPoint(550, 50),  # Repositioned above found_first_char and scanback_to_separator
            "reject": QPoint(700, 300)
        }
        
        # create all the state nodes
        self.nodes = {}
        for state, pos in self.state_positions.items():
            is_terminal = state in ["accept", "reject"]
            is_accept = state == "accept"
            self.nodes[state] = StateNode(
                state, turing_machine, pos, 
                is_current=(state == self.current_state),
                is_terminal=is_terminal,
                is_accept=is_accept, 
                parent=self
            )
            
        # define transitions
        self.transitions = [
            StateTransition("scan_to_separator", "find_first_char", "(#, _, L)"),
            StateTransition("find_first_char", "find_first_char", "(Σ, _ , L)", curved=True, curve_direction=1),  # loop
            StateTransition("find_first_char", "found_first_char", "(_ | *, _, R)"),
            StateTransition("found_first_char", "accept", "(#, _, R)"),
            StateTransition("found_first_char", "scanback_to_separator", "(Σ, * , R)"),
            StateTransition("scanback_to_separator", "scanback_to_separator", "(Σ, _ , R)", curved=True, curve_direction=1),  # loop
            StateTransition("scanback_to_separator", "match_char", "(#, _, R)"),
            StateTransition("match_char", "match_char", "(¬Σ, _, R)", curved=True, curve_direction=1),  # loop
            StateTransition("match_char", "found_char", "(Σ, *, L)"),
            StateTransition("match_char", "reject", "(_, _, R)"),
            StateTransition("found_char", "found_char", "(X, _, L) U (*, _, L)", curved=True, curve_direction=1),  # loop
            StateTransition("found_char", "find_first_char", "(#, _, L)"),
        ]
        
        # Custom label positions (absolute x, y values)
        self.label_coordinates = {
            "scan_to_separator_find_first_char": (174, 170),
            "find_first_char_find_first_char": (250, 65),
            "find_first_char_found_first_char": (325, 130),
            "found_first_char_accept": (455, 80),
            "found_first_char_scanback_to_separator": (475, 170),
            "scanback_to_separator_scanback_to_separator": (660, 150),
            "scanback_to_separator_match_char": (515, 230),
            "match_char_match_char": (550, 390),
            "match_char_found_char": (477, 283),
            "match_char_reject": (622, 283),
            "found_char_found_char": (260, 300),
            "found_char_find_first_char": (360, 220),
        }

        # Label position (above or below the arrow)
        self.label_positions = {
            "scan_to_separator_find_first_char": "above",
            "find_first_char_find_first_char": "above",
            "find_first_char_found_first_char": "above",
            "found_first_char_accept": "above",
            "found_first_char_scanback_to_separator": "above",
            "scanback_to_separator_scanback_to_separator": "above",
            "scanback_to_separator_match_char": "above",
            "match_char_match_char": "above",
            "match_char_found_char": "below",
            "match_char_reject": "above",
            "found_char_found_char": "below",
            "found_char_find_first_char": "below",
        }
        
    def set_state(self, state):
        """updates which state is currently active"""
        if state == self.current_state:
            return
            
        # update all nodes
        for node_state, node in self.nodes.items():
            node.tm = self.tm
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

        # draw the Sigma (Σ) notation box
        sigma_x = 20  # X position
        sigma_y = 360  # Starting Y position

        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(Qt.black)

        # list of lines to display
        legend_lines = [
            "Σ         -->    [a-zA-Z]",
            "*         -->    visited character",
            "#        -->    separator",
            "_        -->    NULL character",
            "R/L    -->    Right/Left"
        ]

        # draw each line with spacing
        line_spacing = 30  # pixels between lines
        for i, line in enumerate(legend_lines):
            painter.drawText(sigma_x, sigma_y + i * line_spacing, line)

        
    def _draw_transition(self, painter, trans, from_pos, to_pos):
        """Draw a transition arrow between states with improved visuals"""
        # Self-loop handling
        if trans.from_state == trans.to_state:
            self._draw_self_loop(painter, trans, from_pos)
            return
            
        # calculate direction vector
        dx = to_pos.x() - from_pos.x()
        dy = to_pos.y() - from_pos.y()
        length = (dx*dx + dy*dy) ** 0.5
        
        if length < 0.1:
            return  # skip if positions are identical
            
        # normalize direction
        dx, dy = dx/length, dy/length
        
        # calculate start and end points (offset from state circles)
        # Use a small offset to ensure arrows precisely touch the circle edge
        node_radius = SIZES["STATE_RADIUS"]
        circle_adjustment = 1  # Slight adjustment to make arrows touch circles precisely
        start_x = from_pos.x() + dx * (node_radius - circle_adjustment)
        start_y = from_pos.y() + dy * (node_radius - circle_adjustment)
        end_x = to_pos.x() - dx * (node_radius - circle_adjustment)
        end_y = to_pos.y() - dy * (node_radius - circle_adjustment)
        
        # figure out if label goes above or below
        transition_key = f"{trans.from_state}_{trans.to_state}"
        label_position = self.label_positions.get(transition_key, "above")
        position_multiplier = -1 if label_position == "above" else 1  # -1 = up, 1 = down
        
        # create the path for drawing
        path = QPainterPath()
        path.moveTo(start_x, start_y)

        custom_label_pos = self.label_coordinates.get(transition_key)

        
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
        
        # draw the arrowhead
        self._draw_arrowhead(painter, end_x, end_y, dx, dy, trans.curved, ctrl_x if trans.curved else 0, ctrl_y if trans.curved else 0)
        
        # draw the label

        if custom_label_pos:
            label_x, label_y = custom_label_pos
        if trans.label:
            self._draw_label(painter, trans.label, label_x, label_y)
    
    def _draw_self_loop(self, painter, trans, pos):
        """Draw a self-looping transition with customizable direction"""
        # Get the state name
        state_name = trans.from_state
        
        # Base radius for all loops - larger to make loops bigger and more visible
        radius = 24
        
        # Direction-based configuration
        # Format: [direction, offset_multiplier]
        loop_configs = {
            "find_first_char": ["up", 1.2],
            "scanback_to_separator": ["right", 1.2],
            "match_char": ["down", 1.2],
            "found_char": ["left", 1.2]
        }
        
        # Get direction for this state or default to "up"
        config = loop_configs.get(state_name, ["up", 1.2])
        direction = config[0]
        offset_multiplier = config[1]
        
        # Calculate offsets and angles based on direction
        offset = SIZES["STATE_RADIUS"] * offset_multiplier
        
        # Set parameters based on direction
        if direction == "up":
            cx_offset = 0
            cy_offset = -offset
            start_angle = 45
            span_angle = 270
        elif direction == "right":
            cx_offset = offset
            cy_offset = 0
            start_angle = 135
            span_angle = 270
        elif direction == "down":
            cx_offset = 0
            cy_offset = offset
            start_angle = 225
            span_angle = 270
        elif direction == "left":
            cx_offset = -offset
            cy_offset = 0
            start_angle = 315
            span_angle = 270
        
        # Calculate center point
        cx = pos.x() + cx_offset
        cy = pos.y() + cy_offset
        
        # Draw the arc - FIXED: Convert to QRect and use integers for angles
        rect = QRect(int(cx - radius), int(cy - radius), int(radius * 2), int(radius * 2))
        painter.setPen(QPen(QColor(COLORS["ARROW_COLOR"]), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawArc(rect, int(start_angle * 16), int(span_angle * 24))
        
        # Calculate the endpoint for the arrowhead (convert angles to radians)
        end_angle_rad = (start_angle + span_angle + 80) * 3.14159 / 180
        # Calculate point precisely on the circle edge where the arrow should end
        # Add a small adjustment to ensure the arrowhead touches the circle edge
        arrow_touch_adjustment = 1  # Small adjustment to make arrow touch circle precisely
        end_x = cx + (radius + arrow_touch_adjustment) * math.cos(end_angle_rad)
        end_y = cy + (radius + arrow_touch_adjustment) * math.sin(end_angle_rad)
        
        # Direction vector at the endpoint (tangent to the circle)
        dx = -math.sin(end_angle_rad)
        dy = math.cos(end_angle_rad)
        
        # Draw arrowhead
        self._draw_arrowhead(painter, end_x, end_y, dx, dy)

        transition_key = f"{trans.from_state}_{trans.to_state}"
        custom_label_pos = self.label_coordinates.get(transition_key)

        # Draw the label if present
        if trans.label:
            # Position label based on the loop orientation
            label_angle = (start_angle + span_angle/2) * 3.14159 / 180
            if custom_label_pos:
                label_x, label_y = custom_label_pos
        
            self._draw_label(painter, trans.label, label_x, label_y)
    
    def _draw_arrowhead(self, painter, end_x, end_y, dx, dy, is_curved=False, ctrl_x=0, ctrl_y=0):
        """Draw an arrowhead at the end of a transition line"""
        if is_curved:
            # for curved paths, calculate tangent at endpoint
            dx = end_x - ctrl_x
            dy = end_y - ctrl_y
            length = (dx*dx + dy*dy) ** 0.5
            if length > 0.1:
                dx, dy = dx/length, dy/length
        
        # Slightly larger arrowhead for better visibility
        arrow_width = SIZES["ARROW_WIDTH"] * 1.1
        # Adjusted shape parameters for better appearance
        angle_factor = 0.8  # Controls the "pointiness" of the arrow
            
        a1_x = end_x - arrow_width * (dx * angle_factor + dy * 0.5)
        a1_y = end_y - arrow_width * (dy * angle_factor - dx * 0.5)
        a2_x = end_x - arrow_width * (dx * angle_factor - dy * 0.5)
        a2_y = end_y - arrow_width * (dy * angle_factor + dx * 0.5)
        
        # make the arrowhead
        arrow = QPolygon()
        arrow.append(QPoint(int(end_x), int(end_y)))
        arrow.append(QPoint(int(a1_x), int(a1_y)))
        arrow.append(QPoint(int(a2_x), int(a2_y)))
        
        painter.setBrush(QBrush(QColor(COLORS["ARROW_COLOR"])))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(arrow)
    
    def _draw_label(self, painter, label_text, x, y):
        """Draw a label for a transition"""
        font = QFont()
        font.setPointSize(FONTS["LABEL_FONT"]["SIZE"])
        painter.setFont(font)
        
        # calculate text dimensions
        metrics = QFontMetrics(font)
        text_width = metrics.horizontalAdvance(label_text)
        text_height = metrics.height()
        
        # Smaller padding to make labels more compact
        padding = SIZES["LABEL_PADDING"] - 1
        
        # Create semi-transparent white background
        bg_color = QColor(255, 255, 255)
        bg_color.setAlpha(230)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor(COLORS["DEFAULT_BORDER"]), 1))
        
        # Create label rectangle centered on the calculated position
        label_rect = QRect(
            int(x - text_width/2 - padding), 
            int(y - text_height/2 - padding/2), 
            text_width + padding*2, 
            text_height + padding
        )
        
        # rounded rectangle for label
        painter.drawRoundedRect(label_rect, 5, 5)
        
        # draw text
        painter.setPen(Qt.black)
        painter.drawText(
            int(x - text_width/2), 
            int(y + text_height/3), 
            label_text
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
        # painter.setPen(QPen(QColor(COLORS["ACCEPT_STATE_BORDER"]), 1))
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


# For testing the widget
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = StateDiagram()
    widget.show()
    sys.exit(app.exec_())