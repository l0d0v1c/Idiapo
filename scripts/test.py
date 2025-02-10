import idiapo


# Initialisation de la classe
translator = idiapo.IdiapoTranslator()

# Exemples d'actions
print("Action FRID:")
print(translator.action('FRID', 'Je suis heureux.'))

print("\nAction IDFR:")
print(translator.action('IDFR', 'idi ego ein agape.'))

print("\nAction FRIDj:")
print(translator.action('FRIDj', 'Je suis heureux.'))