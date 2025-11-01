import json
import tempfile

print(tempfile.gettempdir())


languages = '["en"]'
print(json.loads(languages))