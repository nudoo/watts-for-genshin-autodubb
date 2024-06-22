# 队列深度
max_text_length = 10
max_wav_queue = 10

# 音频文件夹
AUDIO_DIR = r".\audio"


# 屏幕分辨率
width, height = 2560, 1440


def calculate_coordinates(screen_width=2560, screen_height=1440):
    """
    Calculate coordinates for boxes based on screen resolution.

    Parameters:
    - screen_width (int): The width of the screen.
    - screen_height (int): The height of the screen.

    Returns:
    - tuple: Coordinates for the diagnostic box.
    - tuple: Coordinates for the optional box.
    """
    # Define coordinates for the diagnostic box
    # x1 = round(screen_width * 0.15)
    x1 = 0
    y1 = round(screen_height * 0.77)
    # x2 = round(screen_width * 0.85)
    x2 = round(screen_width * 0.85)
    y2 = round(screen_height * 0.925)
    diagnostic_box = (x1, y1, x2, y2)

    # Calculate once to avoid repeated computation
    width_65_percent = round(screen_width * 0.65)
    height_50_percent = round(screen_height * 0.5)
    width_full = round(screen_width)
    height_77_percent = round(screen_height * 0.77)

    # Define coordinates for the optional box
    optional_box = (width_65_percent, height_50_percent, width_full, height_77_percent)

    return diagnostic_box, optional_box


# Get the box coordinates
dia_box, opt_box = calculate_coordinates(width, height)
