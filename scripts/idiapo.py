from openai import OpenAI
import json

class IdiapoTranslator:
    """
    Librairie pour réaliser des traductions en Idiapo ou en Français à l'aide de l'API OpenAI.

    :param base_url: L'URL de base de l'API OpenAI.
    :param api_key: La clé API pour accéder au service.
    :param default_model: Le modèle par défaut utilisé (ex: 'r1').
    :param default_temperature: La température par défaut pour la génération de texte.
    :param default_seed: La graine par défaut pour la génération.
    """
    
    def __init__(self, 
                 base_url: str = "http://localhost:1234/v1", 
                 api_key: str = "lm-studio", 
                 default_model: str = "r1",
                 default_temperature: float = 0.7,
                 default_seed: int = 123):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.default_model = default_model
        self.default_temperature = default_temperature
        self.default_seed = default_seed
        try:
            with open('../preprompt/idiapo-0-fr.md', 'r', encoding='utf-8') as f:
                self.preprompt = f.read()
        except FileNotFoundError:
            preprompt = "Préprompt non trouvé. Veuillez vérifier le chemin du fichier."

    def infer(self, system_prompt: str, user_prompt: str, max_tokens: int = 1024, model: str = None) -> str:
        """
        Effectue une inférence en envoyant une séquence de messages au modèle de chat.

        :param system_prompt: Le prompt système (souvent un préambule ou une grammaire).
        :param user_prompt: Le prompt utilisateur (la question ou la commande à traiter).
        :param max_tokens: Nombre maximal de tokens pour la réponse.
        :param model: Le modèle à utiliser (par défaut, le modèle défini lors de l'initialisation).
        :return: La réponse générée par le modèle.
        """
        model = model if model is not None else self.default_model
        completion = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.default_temperature,
            seed=self.default_seed,
            max_tokens=max_tokens
        )
        return completion.choices[0].message.content

    def action(self, act: str, question: str) -> str:
        """
        Exécute une action de traduction selon le code d'action fourni.

        Les codes d'action supportés sont :
          - 'FRID'  : Traduis en Idiapo.
          - 'IDFR'  : Traduis en Français.
          - 'FRIDj' : Traduis en Idiapo et renvoie le résultat sous forme JSON (traduction et explication).
          - 'IDFRj' : Traduis en Français et renvoie le résultat sous forme JSON (traduction et explication).

        :param act: Code de l'action à effectuer.
        :param question: La question ou phrase à traduire.
        :return: La réponse générée par le modèle.
        :raises ValueError: Si le code d'action n'est pas supporté.
        """
        grammaire=self.preprompt
        actions = {
            'FRID': 'Traduis en Idiapo',
            'IDFR': 'Traduis en Français',
            'FRIDj': 'Traduis en Idiapo. Présente la réponse sans commentaire, juste un format JSON avec la traduction, l\'explication',
            'IDFRj': 'Traduis en Français. Présente la réponse sans commentaire, juste un format JSON avec la traduction et l\'explication.'
        }
        
        if act not in actions:
            raise ValueError(f"Action '{act}' non supportée. Choisissez parmi {list(actions.keys())}.")

        prompt = f"{actions[act]}: {question}"
        return self.infer(grammaire, prompt)



class SymbolTranslator:
    def __init__(self, json_file="vocab.json"):
        """
        À l'initialisation, charge le JSON depuis le fichier `vocab.json`
        et construit deux dictionnaires pour la conversion :
          - de la translittération vers le symbole (translit_to_sym_map)
          - du symbole vers la translittération (sym_to_translit_map)
        """
        with open(json_file, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        
        self.translit_to_sym_map = {}
        self.sym_to_translit_map = {}
        for entry in self.data:
            translit = entry["Translittération"]
            sym = entry["Sym"]
            self.translit_to_sym_map[translit] = sym
            self.sym_to_translit_map[sym] = translit

    def translit_to_sym(self, translit_str):
        """
        Convertit une chaîne de mots (translittérations séparées par des espaces)
        en une suite de symboles correspondants.
        Exemple :
          "ein ant pla" --> "𐀁𐀤𐀳"
        """
        words = translit_str.split()
        symbols = [self.translit_to_sym_map.get(word, "?") for word in words]
        return "".join(symbols)

    def sym_to_translit(self, sym_str):
        """
        Convertit une suite de symboles (sans séparateur, ou avec des espaces)
        en une chaîne de translittérations séparées par des espaces.
        Exemple :
          "𐀁𐀤𐀳" --> "ein ant pla"
        """
        translits = [self.sym_to_translit_map.get(ch, "?") for ch in sym_str if not ch.isspace()]
        return " ".join(translits)

