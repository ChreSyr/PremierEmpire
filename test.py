
import googletrans
from googletrans import Translator

# for id, language in googletrans.LANGUAGES.items():
#     print(id, ":", language)

translator = Translator()

result = translator.translate("Au tour de {}", src="fr", dest="en")
print(result.src)
print(result.dest)
print(result.origin)
print(result.text)
print(result.pronunciation)
