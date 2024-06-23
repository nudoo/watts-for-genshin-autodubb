# 队列深度
max_text_length = 10
max_wav_queue = 10

# 音频文件夹
AUDIO_DIR = r".\audio"

# 在线推理接口访问令牌
access_token = ""

"""匹配说话人。
当一个角色没有语音模型（本来就没有或者ocr识别错误），则为其随机选择一个模型。
记录对应关系，以固定音色。（没啥用，每次识别的名字可能都不一样）
可以提前为角色设置语音模型。例如：{"旅行者":"开拓者(女)【中】"}
"""
SPEAKER_MAPPING = {}


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
    x1 = 0
    y1 = round(screen_height * 0.77)
    x2 = round(screen_width * 0.85)
    y2 = round(screen_height * 0.925)
    diagnostic_box = (x1, y1, x2, y2)

    # Calculate once to avoid repeated computation
    width_65_percent = round(screen_width * 0.65)
    height_50_percent = round(screen_height * 0.5)
    width_full = screen_width
    height_77_percent = round(screen_height * 0.77)

    # Define coordinates for the optional box
    optional_box = (width_65_percent, height_50_percent, width_full, height_77_percent)

    return diagnostic_box, optional_box


# Get the box coordinates
dia_box, opt_box = calculate_coordinates(width, height)
