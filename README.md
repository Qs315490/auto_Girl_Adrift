# 这是什么
一个 《漂流少女》 的自动化脚本。  
由于使用WindowsAPI，此脚本只能在Windows上运行。  
程序默认对 `PRDC` 窗口截图，使用事件机制模拟点击。所以除最小化外的状态都能自动化。

# 目前功能
- [x] 自动战斗
- [x] 自动收邮件
- [x] 自动收补给
- [x] 自动看广告
- [x] 到港口自动出售
- [x] 自动转盘
- [x] 自动炼金
- [ ] 实用yolo进行图像识别以提高识别准确性

# 使用方法
```bash
git clone --depth=1 https://github.com/Qs315490/auto_Girl_Adrift
cd auto_Girl_Adrift
pip install -r requirements.txt
python3 main.py
```