import string
import re


# 去除句尾标点符号
def delete_last_punctuation(s: str):
    # 定义标点符号字符串
    # string.punctuation只包含标准的ASCII标点符号，不包括中文标点符号，需要添加
    cn_punctuation = '，。！？、；：“”‘’（）《》【】'
    punctuation = string.punctuation + cn_punctuation
    return s.rstrip(punctuation)


# 检查文件名是否符合规范，删除特殊字符
def sanitize_filename(filename):
    # 定义Windows不允许的文件名字符
    invalid_chars = r'<>:"/\|?*'

    # 使用正则表达式替换这些字符
    sanitized_filename = re.sub(f'[{re.escape(invalid_chars)}]', '', filename)

    return sanitized_filename