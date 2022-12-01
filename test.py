
from googletrans import Translator

# for id, language in googletrans_.LANGUAGES.items():
#     print(id, ":", language)

translator = Translator()


print(translator.translate("français", src='fr', dest='en'))

sentences = ['Bienvenu', 'Comment allez-vous', 'je vais bien']
result = translator.translate(sentences, src='fr', dest='en')

for r in result:
    print(r.__dict__)
print(result)


result = translator.translate(["Au tour de {}", "français"], src="fr", dest="en")
print(result[0].src)
print(result[0].dest)
print(result[0].origin)
print(result[0].text)
print(result[0].pronunciation)
