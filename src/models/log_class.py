import json

class Log:
    def __init__(self, url: str):
        self.url = url
        self.jcontent = None
        self.pjcontent = None
    
    def set_jcontent(self, http_response):        
        content = http_response.content.decode("utf-8")
        java_data_text = content.split('var _logData = ')[1].split('var logData = _logData;')[0].rsplit(';', 1)[0].strip()
        self.jcontent = json.loads(java_data_text)

    def set_pjcontent(self, http_response):     
        self.pjcontent = http_response.json()