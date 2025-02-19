
import json
import os
from aip import AipOcr
from PyQt5.QtCore import QThread, pyqtSignal

API_CONFIG_FILE_PATH = "./config/api-config.json"
SETTINGS_FILE_PATH = "./config/settings.json"

class AipOcr_Handler():
    def __init__(self, config):
        bd_config = config['bd_api']
        self.app_id = bd_config['AppID']
        self.api_key = bd_config['APIKey']
        self.secret_key = bd_config['SecretKey']
        self.ocr = AipOcr(self.app_id,self.api_key,self.secret_key)
        
    def recognize(self, image, language):
        result_json = self.ocr.basicGeneral(image, {"language_type":language})
        if not (result_json["words_result_num"]):# 没有结果
            return '[未识别到文字]'
        if result_json.get("words_result"): #能获取结果
            # 文本处理
            result_text = ''
            for i in result_json["words_result"]:
                result_text += i['words']+"\n"
            return result_text
        elif result_json.get('error_code') == 14: #证书失效,检查用户信息
            return "[错误: 请检查APPID,APIKEY,以及SECRET_KEY]"
        elif result_json.get('error_code') == 17: #今天超额
            return "[错误: 今日次数超额]"
        else:
            return f"[错误: 未知错误({result_json})]"

class Ocr_Handler(QThread):
    signal_started = pyqtSignal()
    signal_finished = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        # load config
        with open(SETTINGS_FILE_PATH,"r+") as f:
            settings = json.load(f)
        self.api_type = settings['ocr_api_type']
        self.language = settings['ocr_language']
        with open(API_CONFIG_FILE_PATH,"r+") as f:
            api_config = json.load(f)
        self.config = api_config['ocr_config']
        # API初始化
        api_call_dict = {
            'bd_normal': AipOcr_Handler,
        }
        self.api_selected = api_call_dict[self.api_type](self.config)
        
    def select_image(self, image):
        self.image = image
    
    def run(self):
        self.signal_started.emit()
        text = self.api_selected.recognize(self.image, self.language)
        self.signal_finished.emit(text)