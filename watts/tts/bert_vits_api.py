import requests, sys
from NsparkleLog import LogManager


access_token = r"6cb54f0ef2fe3fa1df97d2ecdd8652d5"


class BertVits2:
    def __init__(self) -> None:
        self.logger = LogManager.GetLogger(self.__class__.__name__)
        self.baseapi = f"https://infer.acgnai.top"
        self.token = access_token
        self.getsp = f"{self.baseapi}/infer/spks"
        self.gen = f"{self.baseapi}/infer/gen"
        self.parm: dict[str, str] = {
            "type": "tts",
            "brand": "bert-vits2",
            "name": "sr"
        }
        self.gen_body = {
            "access_token": access_token,
            "type": "tts",
            "brand": "bert-vits2",
            "name": "sr",
            "prarm": {
                "speaker": "花火【中】",
                "text": "你好你好，我是花火，请问你是？。",
                "sdp_ratio": 0.2,
                "noise_scale": 0.6,
                "noise_scale_w": 0.9,
                "length_scale": 1.0,
                "language": "ZH",
                "cut_by_sent": True,
                "interval_between_sent": 0.2,
                "interval_between_para": 1.0,
                "style_text": "我很开心！！！",
                "style_weight": 0.4
            }
        }

    def getSpeakers(self, name: str = "sr") -> list[str]:
        filename = "default"
        try:
            self.parm["name"] = name
            if name == "sr":
                filename = "star-rail-spklist"
                self.logger.trace("获取所有星穹铁道的说话人")
            self.logger.info("开始获取所有可用的说话人")
            response = requests.get(self.getsp, json=self.parm)
            if response.status_code == 200:
                self.logger.info("响应成功")
                self.logger.trace("提取spklist字段")
                spklist: list[str] = response.json()["spklist"]
                if not spklist:
                    self.logger.warning("提取到spklist为空")
                else:
                    self.logger.trace("提取成功")
                self.logger.info("写入文件")
                with open(f"{filename}.txt", "w", encoding="utf-8") as f:
                    s_spklist = '\n'.join(spklist)
                    f.write(f"{s_spklist}")  # type: ignore
                return spklist
            else:
                self.logger.error(f"获取失败,状态码:{response.status_code}")
                self.logger.error(f"获取失败, 返回信息:{response.text}")
        except Exception as e:
            self.logger.exception(e)
            return []

    def moreSettings(self,
                     sdp_ratio: float,
                     noise_scale: float,
                     noise_scale_w: float,
                     length_scale: float,
                     style_weight: float,
                     cut_by_sent: bool,
                     interval_between_sent: float,
                     interval_between_para: float,
                     style_text: str
                     ) -> None:
        self.logger.info("开始设置")
        self.gen_body["prarm"]["sdp_ratio"] = sdp_ratio
        self.gen_body["prarm"]["noise_scale"] = noise_scale
        self.gen_body["prarm"]["noise_scale_w"] = noise_scale_w
        self.gen_body["prarm"]["length_scale"] = length_scale
        self.gen_body["prarm"]["style_weight"] = style_weight
        self.gen_body["prarm"]["cut_by_sent"] = cut_by_sent
        self.gen_body["prarm"]["interval_between_sent"] = interval_between_sent
        self.gen_body["prarm"]["interval_between_para"] = interval_between_para
        self.gen_body["prarm"]["style_text"] = style_text
        self.logger.info("设置完成")

    def gengrateToVolce(self, filename: str, speaker: str, text: str, text_language: str = "ZH") -> dict:
        try:
            self.gen_body["prarm"]["speaker"] = speaker
            self.gen_body["prarm"]["text"] = text
            self.gen_body["prarm"]["language"] = text_language
            self.logger.trace(f"设置说话人为:{speaker}")
            self.logger.info("开始生成语音")
            if not self.token or self.token == "":
                self.logger.warning("token未设置")
            response = requests.post(self.gen, json=self.gen_body)
            if response.status_code == 200:
                # 提取audio字段
                self.logger.info("响应成功,提取字段...")
                audio = response.json()["audio"]
                if not audio:
                    self.logger.warning("提取到audio地址为空")
                self.logger.trace(f"提取到的audio地址:{audio}")
                # 获取audio字节流数据
                audio_bytes = requests.get(audio).content
                self.logger.trace(f"转换字节流成功")
                # 写入文件
                with open(f"{filename}.wav", "wb") as f:
                    f.write(audio_bytes)
                self.logger.info(f"文件 {filename} 写入成功!")
                return response.json()
            else:
                self.logger.error(f"生成失败, 状态码:{response.status_code}")
                self.logger.error(f"生成失败, 返回信息:{response.text}")
        except Exception as e:
            self.logger.exception(e)
            return {}


if __name__ == "__main__":
    bert = BertVits2()
    bert.moreSettings(0.2, 0.6, 0.9, 1.0, 0.4, True, 0.2, 1.0, "我很开心！！！")
    bert.gengrateToVolce("test", "花火【中】", "你好你好，我是花火。不能再商量商量吗?")
