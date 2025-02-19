
import json
import time
import hashlib
import hmac
import requests

API_CONFIG_FILE_PATH = "./config/api-config.json"
SETTINGS_FILE_PATH = "./config/settings.json"

class Translate_Handler():
    def __init__(self):
        # load config
        with open(SETTINGS_FILE_PATH,"r+") as f:
            settings = json.load(f)
        self.api_type = settings['translate_api_type']
        self.source_lang = settings['translate_source_lang']
        self.target_lang = settings['translate_target_lang']
        with open(API_CONFIG_FILE_PATH,"r+") as f:
            api_config = json.load(f)
        self.config = api_config['translate_config']
        
        api_call_dict = {
            "tx_api": tx_translate,
        }
        self.api_selected = api_call_dict[self.api_type]
    
    def translate(self, text):
        return tx_translate(text, self.config, self.source_lang, self.target_lang)

# tx api 文本翻译：
def tx_translate(text, translate_config, source_lang='jp', target_lang='zh'):
    
    SECRET_ID = translate_config['tx_api']['SecretId']
    SECRET_KEY = translate_config['tx_api']['SecretKey']
    PROJECT_ID = translate_config['tx_api']['ProjectId']
    REGION = translate_config['tx_api']['Region']
    ENDPOINT = translate_config['tx_api']['EndPoint']
    SERVICE = 'tmt'
    VERSION = translate_config['tx_api']['Version']
    ACTION = translate_config['tx_api']['Action']
    
    # 保密协议
    def sign_request(secret_id, secret_key, method, endpoint, uri, params):
        timestamp = int(time.time())
        date = time.strftime('%Y-%m-%d', time.gmtime(timestamp))
        
        # 1. Build Canonical Request String
        http_request_method = method
        canonical_uri = uri
        canonical_querystring = ''
        canonical_headers = f'content-type:application/json\nhost:{endpoint}\n'
        signed_headers = 'content-type;host'
        payload_hash = hashlib.sha256(json.dumps(params).encode('utf-8')).hexdigest()
        canonical_request = (http_request_method + '\n' + 
                            canonical_uri + '\n' + 
                            canonical_querystring + '\n' + 
                            canonical_headers + '\n' + 
                            signed_headers + '\n' + 
                            payload_hash)
        
        # 2. Build String to Sign
        algorithm = 'TC3-HMAC-SHA256'
        credential_scope = f"{date}/{SERVICE}/tc3_request"
        string_to_sign = (algorithm + '\n' + 
                        str(timestamp) + '\n' + 
                        credential_scope + '\n' + 
                        hashlib.sha256(canonical_request.encode('utf-8')).hexdigest())
        
        # 3. Sign String
        def sign(key, msg):
            return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
        
        secret_date = sign(('TC3' + secret_key).encode('utf-8'), date)
        secret_service = sign(secret_date, SERVICE)
        secret_signing = sign(secret_service, 'tc3_request')
        signature = hmac.new(secret_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        
        # 4. Build Authorization Header
        authorization = (f"{algorithm} "
                        f"Credential={secret_id}/{credential_scope}, "
                        f"SignedHeaders={signed_headers}, "
                        f"Signature={signature}")
        
        return authorization, timestamp
    
    params = {
        "SourceText": text,
        "Source": source_lang,
        "Target": target_lang,
        "ProjectId": int(PROJECT_ID)
    }
 
    method = 'POST'
    uri = '/'
    authorization, timestamp = sign_request(SECRET_ID, SECRET_KEY, method, ENDPOINT, uri, params)
 
    headers = {
        'Content-Type': 'application/json',
        'Host': ENDPOINT,
        'X-TC-Action': ACTION,
        'X-TC-Timestamp': str(timestamp),
        'X-TC-Version': VERSION,
        'X-TC-Region': REGION,
        'Authorization': authorization
    }
 
    response = requests.post(f'https://{ENDPOINT}{uri}', headers=headers, data=json.dumps(params))
    result = response.json()
    
    if 'Response' in result and 'TargetText' in result['Response']:
        return result['Response']['TargetText']
    else:
        print(f"翻译API响应错误: {result}")
        return text  # 如果翻译失败，返回原文
    