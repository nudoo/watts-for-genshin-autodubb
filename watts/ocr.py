"""
识别屏幕上的文字
"""
import asyncio
import time
import random
import easyocr
from easyocr import Reader
import numpy as np
from PIL import ImageGrab
from PIL import Image
from difflib import SequenceMatcher
from watts.OperationAPI.CharacterOperation import CharacterOperation
from watts.log import new_logger
from watts import config


player = CharacterOperation("主角")
logger = new_logger("ocr")


def get_screenshot():
    # 抓取屏幕截图，并转换为 NumPy 数组
    screenshot = ImageGrab.grab()
    width, height = screenshot.size
    img = screenshot.convert('RGB')
    # 裁剪
    # bounding_box = (250, 1000, 2300, 1350)
    # cropped_img = img.crop(bounding_box)
    # 将 PIL.Image 对象转换为 NumPy 数组
    img_array = np.array(img)
    return img_array


# 比较两个字符串的相似度
def compare_strings(str1, str2):
    # 创建SequenceMatcher对象
    seq_matcher = SequenceMatcher(None, str1, str2)

    # 计算相似度
    similarity = seq_matcher.ratio()

    # 返回相似度值
    return similarity > 0.8


def make_up_msg(charactor: str, dialogue: str, emotion: str = "default", text_language: str = "多语种混合",
                batch_size: int = 1, speed: float = 1.0, stream: str = "False", save_temp: str = "False") -> dict:
    """
    :rtype: dict
    """
    return dict(character=charactor,
                text=dialogue,
                emotion=emotion,
                text_language=text_language,
                batch_size=batch_size,
                speed=speed,
                stream=stream,
                save_temp=save_temp)


def get_ocr_result(img: Image, box: tuple, reader: Reader) -> list[tuple]:
    """传入图像，识别框，ocr Reader，返回ocr文字识别结果"""
    cropped_img = img.crop(box)
    cropped_array = np.array(cropped_img)
    ocr_result = reader.readtext(cropped_array)
    return ocr_result


def get_result_text(results: list[tuple]):
    """从ocr识别结果中，提取其中的文字"""
    # length = len(results)
    text = ""
    for res in results:
        text += res[1]
    return text


def deal_dial_result(results: list[tuple]):
    """从识别结果中，判断文字是否居中，以及box的高度，筛选出角色以及台词"""
    height_list = []
    text_list = []

    """
    默认第一个识别结果为说话人，即 
    speaker = results[0][1]
    如果识别出的说话人姓名长度为1，则认为是ocr识别错误，删除该识别结果
    """
    length = len(results[0][1])
    while length <= 1:
        results.pop(0)
        length = len(results[0][1])

    for res in results:
        box = res[0]
        p_x1, p_y1, p_x2, p_y2 = get_box_position(box)

        width = p_x2 - p_x1
        height = p_y2 - p_y1

        # 相对位置偏移量，越小说明越居中
        # relative = abs(p_x1 + p_x2 - config.width)
        # 居中的内容，判定为说话人姓名，（身份），台词
        # !!!因识别时台词被拆分成多段，不再居中，故不能使用居中来判断
        height_list.append(height)
        text_list.append(res[1])

    print("==============")
    print(text_list)
    length = len(height_list)
    print(f"heights={height_list}")
    if length > 1:
        # 通过高度差判断第二列是否是身份信息
        avg = sum(height_list) / length
        per = height_list[1] / avg
        print(f"avg={avg},per={per}")
        if per < 0.9:
            text_list.pop(1)

    charactor = text_list[0]
    dialogue = ''.join(text_list[1:])
    print(dialogue)
    return charactor, dialogue


def deal_opt_result(results: list[tuple]):
    """处理选项识别结果"""
    # _choice = results[0]
    print("玩家选项：", results)
    _choice = random.choice(results)
    print("选择结果：", _choice)
    p_x1, p_y1, p_x2, p_y2 = get_box_position(_choice[0])
    click_x = random.randint(p_x1, p_x2) + config.opt_box[0]
    click_y = random.randint(p_y1, p_y2) + config.opt_box[1]
    opt_position = (click_x, click_y)

    # 选项的文字
    _text = _choice[1]

    return dict(position=opt_position, text=_text)


def get_box_position(box:tuple):
    # 从单个文字识别结果中，提取box的坐标信息（左上，右下）
    p_x1 = box[0][0]
    p_y1 = box[0][1]
    p_x2 = box[2][0]
    p_y2 = box[2][1]
    return p_x1, p_y1, p_x2, p_y2


def start(bot):
    cnt = 0
    last_text = ""                              # 记录上一次的文字识别结果
    send_flag = False                           # 判断文本是否以发送给tts
    reader = easyocr.Reader(['ch_sim', 'en'])   # this needs to run only once to load the model into memory
    while True:  # 使用一个无限循环
        time.sleep(1)
        # 抓取屏幕截图，并转换为 NumPy 数组
        screenshot = ImageGrab.grab()
        img = screenshot.convert('RGB')

        dial_ocr_result = get_ocr_result(img, config.dia_box, reader)
        """
        从识别结果中选取出说话人和台词，判断台词有无变化，没有变化说明台词显示完全了
        发送
        判断识别结果中有无选项，若有，则随机选取|选择第一条，
        发送，点击选项
        点击任意位置继续（不开自动）
        """
        length = len(dial_ocr_result)
        # 文字识别结果为空|只有1个结果，判断不是对话台词：结束本次循环
        if length < 2:
            continue

        # 识别出2个以上结果
        text = get_result_text(dial_ocr_result)
        logger.info(f"文字识别 cnt = {cnt}，last_text={last_text}, text={text}")
        # 判断文字是否变化
        if not compare_strings(text, last_text):
            # 不一致，判断为对话还没显示完
            last_text = text
            send_flag = False
            continue
        # 判断文本是否以发送至tts
        if send_flag:
            # 该台词已经发送至tts合成
            # pyautogui.click()
            player.MouseLeftClick()
            continue
        logger.info("屏幕截图文字未变化。准备合成语音")
        charactor, dialogue = deal_dial_result(dial_ocr_result)

        msg = make_up_msg(charactor, dialogue)
        bot.send(msg)
        send_flag = True

        cnt += 1
        logger.info(f"对话台词识别结果:\n {dial_ocr_result} \n")
        logger.info(f"对话台词识别结果，{charactor}： {dialogue}")
        logger.info(f"文字识别,已发送 cnt = {cnt}，text={text}")

        # 识别玩家选项
        opt_ocr_result = get_ocr_result(img, config.opt_box, reader)
        if not opt_ocr_result:
            # 无识别结果
            # pyautogui.click()
            player.MouseLeftClick()
            continue

        # 处理选项文字识别结果
        opt_result_dict = deal_opt_result(opt_ocr_result)
        opt_position = opt_result_dict.get("position")          # 点击位置
        my_text = opt_result_dict.get("text")                   # 选择的文本
        logger.info(f"玩家选项。opt_position={opt_position}, text={my_text}")
        # 将鼠标平滑移动到选项位置，持续时间设置为0.5秒
        # pyautogui.moveTo(opt_position, duration=0.5)
        # pyautogui.click()
        player.MoveMouseToPosition(opt_position[0], opt_position[1])
        player.MouseLeftClick()

        msg = make_up_msg("旅行者", my_text)

        bot.send(msg)


