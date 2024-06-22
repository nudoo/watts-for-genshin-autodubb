import time
import os
from playsound import playsound
from watts import config
from watts.log import new_logger
from .bert_vits_api import BertVits2
from watts import utils

logger = new_logger("tts")
bert = BertVits2()


def generate_speech(text, audio_name, speaker):
    """使用在线接口合成语音
    接口地址：https://infer.acgnai.top
    作者：红血球AE3803 https://www.bilibili.com/read/cv26659988/?from=articleDetail&spm_id_from=333.976.0.0
    """
    # bert.moreSettings(0.2, 0.6, 0.9, 1.0, 0.4, True, 0.2, 1.0, "我很开心！！！")
    bert.gengrateToVolce(audio_name, speaker, text)
    pass


def inference(is_run, tts_que, wav_que):
    logger.info(f'[inference] 运行inference子进程')
    i = 1
    while is_run:
        # 阻塞
        msg = {}
        if tts_que.empty():
            time.sleep(2)
            continue
        else:
            try:
                msg = tts_que.get()
            except Exception as e:
                logger.warning("-----------ErrorStart--------------")
                logger.warning(e)
                logger.warning("gpt获取弹幕异常，当前线程：：")
                logger.warning(msg)
                logger.warning("-----------ErrorEnd--------------")
                time.sleep(2)
                continue

        text = str(msg["text"]).replace("\n", "")
        text = utils.sanitize_filename(text)

        # 如果text为空，跳过
        if not len(text):
            continue

        name = utils.delete_last_punctuation(text)

        audio_name = os.path.join(config.AUDIO_DIR, name)
        """"""
        # speaker = msg.get("character")
        speaker = "花火【中】"
        logger.info(f'[inference] name={name},speaker={speaker},text={text}')
        generate_speech(text, audio_name, speaker)
        wav_que.put(audio_name + "::" + text)


def play(is_run, wav_que):
    logger.info("by moea:运行play子进程")
    # pygame.init()
    while is_run:
        # 阻塞
        if wav_que.empty():
            time.sleep(2)
            continue
        logger.info(f"[play], wav_queue深度：{wav_que.qsize()}")
        text = wav_que.get()

        audio_name = text.split("::")[0]
        txt = text.split("::")[1]

        logger.info(f"开始播放内容::{audio_name}::{txt}")
        play_audio(audio_name)


def play_audio(audio_name):
    try:
        curr_dir = os.getcwd()
        abs_dir = os.path.join(curr_dir, f"{audio_name}.wav")
        # logger.info(f"[play_audio]:绝对路径：{abs_dir}")
        # 判断文件是否存在
        if os.path.exists(abs_dir):
            playsound(abs_dir)
        else:
            time.sleep(2)
            playsound(abs_dir)
        time.sleep(1)
    except Exception as e:
        logger.warning(e)
