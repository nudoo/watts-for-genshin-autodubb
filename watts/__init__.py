import multiprocessing
import os

from watts import config, ocr, tts


class WaTTS(object):
    def __init__(self):
        self.tts_queue = multiprocessing.Queue(maxsize=int(config.max_tts_length))
        self.wav_queue = multiprocessing.Queue(maxsize=int(config.max_wav_length))
        self.is_run = True

    def inference(self):
        tts.inference(self.is_run, self.tts_queue, self.wav_queue)

    def ocr(self):
        ocr.start(self)

    def playsound(self):
        tts.play(self.is_run, self.wav_queue)

    def send(self, msg):
        self.tts_queue.put(msg)

    def run(self):
        # ocr文字识别进程
        p1 = multiprocessing.Process(target=self.ocr, args=())
        p1.start()
        # tts 推理进程
        p2 = multiprocessing.Process(target=self.inference, args=())
        p2.start()
        # 音频播放进程
        p3 = multiprocessing.Process(target=self.playsound, args=())
        p3.start()


_bot = None


def init():
    global _bot
    os.makedirs(config.AUDIO_DIR, exist_ok=True)
    _bot = WaTTS()
    return _bot
