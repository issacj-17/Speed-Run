import requests, json
from pathlib import Path

class AI_Image_Detector():
    def __init__(self, USER, KEY):
        self.USER = USER
        self.KEY = KEY
        self.query = input("Is this an Image URL or Image File?\nImage URL: A\nImage File: B\n").capitalize()
        print(self.url_or_file())
    def url_or_file(self):
        if self.query == "A":
            self.image_data = input("Please key in the image url here: ")
            params = {
                'url': self.image_data,
                'models': 'genai',
                'api_user': self.USER,
                'api_secret': self.KEY
            }
            r = requests.get('https://api.sightengine.com/1.0/check.json', params=params)
        elif self.query == "B":
            self.image_data = input("Please key in the image file path here: ")
            params = {
                'models': 'genai',
                'api_user': self.USER,
                'api_secret': self.KEY
            }
            image_path = Path(str(self.image_data).strip('"'))
            files = {'media': open(image_path, 'rb')}
            r = requests.post('https://api.sightengine.com/1.0/check.json', files=files, data=params)
        else:
            self.url_or_file()
        output = json.loads(r.text)
        percent_ai = output["type"]["ai_generated"]
        message = f"This image is {percent_ai * 100}% AI generated."
        return message

ris = AI_Image_Detector()