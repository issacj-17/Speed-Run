from serpapi import GoogleSearch
import json
from pathlib import Path

class ReverseImageSearch():
    def __init__(self):
        self.query = input("Is this an Image URL or Image File?\nImage URL: A\nImage File: B\n").capitalize()
        self.url_or_file()
        print(self.search_now())
    def url_or_file(self):
        if self.query == "A":
            self.image_data = input("Please key in the image url here: ")
        elif self.query == "B":
            self.image_data = input("Please key in the image file path here: ")
        else:
            self.url_or_file(self.query)

    def search_now(self):
        if self.image_data == "A":
            self.image_data = self.query_2
        elif self.image_data == "B":
            self.image_data = Path(self.query_2)
        params = {
        "engine": "google_reverse_image",
        "image_url": self.image_data,
        "api_key": "d7459bdda259a14757a9335dbf6ddcbbda8093482ae160a3afa79aa0d46abdf8"
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        try: 
            json.dumps(results["image_results"], indent=4, ensure_ascii=False)
        except KeyError:
            if results["error"] == "Google Reverse Image hasn't returned any results for this query.":
                message = "This image is original."
        else:
            message = "This image was stolen."
        return message

ris = ReverseImageSearch()
