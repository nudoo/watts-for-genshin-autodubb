"""
识别屏幕上的文字
"""
import time
import random
import easyocr
from easyocr import Reader
from typing import List, Tuple
import numpy as np
from PIL import ImageGrab
from PIL import Image
from difflib import SequenceMatcher
from watts.log import new_logger
from watts import config


logger = new_logger("ocr")


# 比较两个字符串的相似度
def compare_strings(last_str, curr_str) -> bool:
    # 创建SequenceMatcher对象
    seq_matcher = SequenceMatcher(None, last_str, curr_str)
    # 计算相似度
    similarity = seq_matcher.ratio()
    # 返回相似度值
    return similarity > 0.8


def make_up_msg(charactor: str, dialogue: str, emotion: str = "default", text_language: str = "多语种混合",
                batch_size: int = 1, speed: float = 1.0, stream: str = "False", save_temp: str = "False") -> dict:
    """
    :rtype: dict
    兼容本地tts（GSVI）接口格式
    """
    return dict(character=charactor,
                text=dialogue,
                emotion=emotion,
                text_language=text_language,
                batch_size=batch_size,
                speed=speed,
                stream=stream,
                save_temp=save_temp)


def get_ocr_result(img: Image, box: Tuple, reader: Reader) -> list[tuple]:
    """传入图像，识别框，ocr Reader，返回ocr文字识别结果"""
    cropped_img = img.crop(box)
    cropped_array = np.array(cropped_img)
    ocr_results = reader.readtext(cropped_array)
    return ocr_results


def get_result_text(results: List[Tuple]) -> str:
    """
    从OCR识别结果中提取并连接所有识别到的文字。

    :param results: 包含OCR识别结果的元组列表，其中每个元组的第一个元素是4个坐标组成的列表，
                    第二个元素是识别到的文字。
    :return: 连接后的所有文字。
    """
    return ''.join(text for _, text, _ in results)


def deal_dial_result(results: List[Tuple]) -> Tuple:
    """处理识别结果，筛选出角色以及台词
    默认第一个识别结果为说话人|角色，如果识别出的说话人姓名长度为1，则认为是ocr识别错误，删除该识别结果.
    默认第二个识别结果为职业，通过相对高度判断是否是职业，若是则忽略.
    将剩下的识别结果拼接为台词.
    """
    height_list = []
    text_list = []

    # 获取第一个识别结果长度
    length = len(results[0][1])
    # 移除长度小于1的元素
    while length <= 1 and results:
        results.pop(0)
        if results:  # 检查列表是否为空
            length = len(results[0][1])

    for res in results:
        box = res[0]
        p_x1, p_y1, p_x2, p_y2 = get_box_position(box)

        # width = p_x2 - p_x1
        height = p_y2 - p_y1

        height_list.append(height)
        text_list.append(res[1])

    count = len(height_list)
    if count > 2:
        # 通过相对高度判断第二行是否是职业信息
        avg = sum(height_list) / count
        per = height_list[1] / avg
        if per < 0.9:
            text_list.pop(1)

    charactor = text_list[0]
    dialogue = ''.join(text_list[1:])
    return charactor, dialogue


def deal_opt_result(results: List[Tuple]) -> dict:
    """处理玩家选项部分识别结果
    坐标本来是控制鼠标点击用的，现在没用了
    """
    _choice = random.choice(results)
    p_x1, p_y1, p_x2, p_y2 = get_box_position(_choice[0])
    click_x = random.randint(p_x1, p_x2) + config.opt_box[0]
    click_y = random.randint(p_y1, p_y2) + config.opt_box[1]
    opt_position = (click_x, click_y)

    return dict(position=opt_position, text=_choice[1])


def get_box_position(box: Tuple) -> Tuple:
    # 从单个文字识别结果中，提取box的坐标信息（左上，右下）
    p_x1 = box[0][0]
    p_y1 = box[0][1]
    p_x2 = box[2][0]
    p_y2 = box[2][1]
    return p_x1, p_y1, p_x2, p_y2


def start(bot):
    last_text = ""                              # 记录上一次的文字识别结果
    send_flag = False                           # 判断文本是否已发送给tts
    reader = easyocr.Reader(['ch_sim', 'en'])   # this needs to run only once to load the model into memory
    while True:                                 # 使用一个无限循环，可以用bot.is_run来着
        time.sleep(1)
        # 抓取屏幕截图，并转换为 NumPy 数组
        screenshot = ImageGrab.grab()
        img = screenshot.convert('RGB')

        dial_ocr_result = get_ocr_result(img, config.dia_box, reader)
        """
        从识别结果中选取出说话人和台词，判断台词有无变化，
        若两次识别结果一样，认为台词播放完了，发送至tts合成语音。     
        判断识别结果中有无玩家选项，若有，则随机选取一条，发送至tts合成语音。（没有自动点击，可能合成的台词和玩家选择的不一样）
        """
        length = len(dial_ocr_result)
        if length < 2:
            # 文字识别结果为空|只有1个结果，判断不是对话台词：结束本次循环
            continue

        # 识别出2个以上结果
        text = get_result_text(dial_ocr_result)
        logger.trace(f"文字识别：last_text={last_text}, text={text}")
        # 判断文字是否变化
        if not compare_strings(text, last_text):
            # 不一致，判断为对话还没显示完
            last_text = text
            send_flag = False
            continue
        # 识别结果无变化，判断文本是否已发送至tts
        if send_flag:
            # 该台词已经发送至tts合成
            # pyautogui.click()
            continue
        logger.trace("识别到屏幕文字未变化。准备合成语音...")
        charactor, dialogue = deal_dial_result(dial_ocr_result)

        msg = make_up_msg(charactor, dialogue)
        bot.send(msg)
        send_flag = True
        logger.trace(f"对话台词识别结果，{charactor}： {dialogue}")

        # 识别玩家选项
        opt_ocr_result = get_ocr_result(img, config.opt_box, reader)
        if not opt_ocr_result:
            # 无识别结果
            # pyautogui.click()
            continue

        # 处理选项文字识别结果
        opt_result_dict = deal_opt_result(opt_ocr_result)
        opt_position = opt_result_dict.get("position")              # 点击位置
        player_text = opt_result_dict.get("text")                   # 选择的文本
        logger.trace(f"玩家选项。opt_position={opt_position}, text={player_text}")
        # 将鼠标移动到选项位置，持续时间设置为0.5秒
        # pyautogui.moveTo(opt_position, duration=0.5)
        # pyautogui.click()

        msg = make_up_msg("旅行者", player_text)
        bot.send(msg)
