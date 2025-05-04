"""
all the styling stuff for our turing machine simulator
put it all here so it's easier to change things later
"""

# colors we use throughout the app
COLORS = {
    # UI element colors
    "CURRENT_STATE": "#FFEB3B",      # yellow 
    "ACCEPT_STATE_BG": "#C8E6C9",    # light green 
    "ACCEPT_STATE_BORDER": "#388E3C", # dark green
    "REJECT_STATE_BG": "#FFCDD2",    # light red
    "REJECT_STATE_BORDER": "#D32F2F", # dark red
    "DEFAULT_STATE_BG": "#FFFFFF",   # white
    "DEFAULT_BORDER": "#000000",     # black
    "HEAD_POINTER": "#FF0000",       # red
    "LABEL_BG": "#FFFDE7",           # pale yellow
    "ARROW_COLOR": "#2196F3",        # blue
    
    # tape cell colors
    "BLANK_CELL": "#F5F5F5",         # light gray
    "UNPROCESSED_CHAR": "#FFFFFF",   # white
    "PROCESSED_CHAR": "#FFCDD2",     # light red
    "MATCHED_CHAR": "#C8E6C9",       # light green
    "SEPARATOR": "#BBDEFB",          # light blue
    
    # text colors
    "SUCCESS_TEXT": "#4CAF50",       # green
    "ERROR_TEXT": "#F44336",         # red
}

# sizes for different parts of the UI
SIZES = {
    # tape stuff
    "CELL_SIZE": 50,                 # how big each tape cell is
    "CELL_FONT_SIZE": 16,            # how big the text in cells is
    
    # state diagram stuff
    "STATE_NODE_SIZE": 90,           # how big the state bubbles are
    "STATE_RADIUS": 40,              # radius of the circles
    "INNER_RADIUS": 34,              # inner circle for terminal states
    "ARROW_WIDTH": 10,               # how wide the arrowheads are
    "LABEL_PADDING": 5,              # space around the labels
    "CURVE_OFFSET": 60,              # how curved the arrows are
    
    # other UI elements
    "BUTTON_HEIGHT": 40,             # how tall the buttons are
    "ARROW_POINTER_WIDTH": 15,       # width of the head pointer arrow
}

# font settings
FONTS = {
    "CELL_FONT": {
        "SIZE": 16,
        "WEIGHT": "bold",
    },
    "STATE_FONT": {
        "SIZE": 9,
        "WEIGHT": "normal",
    },
    "LABEL_FONT": {
        "SIZE": 9,
        "WEIGHT": "normal",
    },
    "LEGEND_FONT": {
        "SIZE": 9,
        "WEIGHT": "normal",
    },
}