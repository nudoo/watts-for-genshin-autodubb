# WaTTS:原神支线AI配音机器人

使用ocr和tts实现的原神支线AI配音机器人

## 如何开始使用

1. 打开一个合适的文件夹，点击资源管理器左上角的 `文件 -> 打开Windows Powershell`

2. 输入以下命令克隆本仓库并安装依赖

    ```powershell
    git clone https://github.com/nudoo/watts-for-genshin-autodubb.git
    cd watts-for-genshin-autodubb
    python -m pip install -r requirements.txt
    ```

3. 进入watts目录下，右键使用Notepad++打开config.py，填写您的访问令牌：
   ```python
   access_token = "your_token"
   ```

   若您还没有[在线语音合成](https://infer.acgnai.top)的访问令牌，可以参考[这里](https://www.bilibili.com/read/cv26659988/?spm_id_from=333.1007.0.0)获取。

4. 回到powershell，输入以下命令，启动 WaTTS

    ```powershell
    python run.py
    ```
	
## 注意事项

如果你在使用过程中遇到任何问题或有改进建议，请随时联系我们，我们会尽快回复并解决问题。

感谢使用WaTTS，祝你游戏愉快！

## 开源协议及免责声明

本项目遵守GPL-3.0协议开源，请在协议允许的条件及范围内使用本项目。本项目的开发者不会强制向您索要任何费用，同时也不会提供任何质保，一切因本项目引起的法律、利益纠纷与本项目的开发者无关。

最终解释权归HoshinoBot开发组所有。
