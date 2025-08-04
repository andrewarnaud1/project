'''
Ensemble des méthodes qui permettent de récupérer un agent fictif
'''
import logging
import base64
from Crypto.Cipher import AES
from src.utils.utils import contexte_actuel

LOGGER = logging.getLogger(__name__)


def decryptage_utilisateur(valeur) -> str:
    '''
    Décryptage des valeur à décrypter
    '''
    methode_name = contexte_actuel()
    LOGGER.debug('[%s] ---- DEBUT ----', methode_name)

    try:
        tag_length = 16

        key_aes = base64.b64decode(valeur['key_aes'])
        iv_base64 = base64.b64decode(valeur['iv_base64'])
        data = base64.b64decode(valeur['data_base64'])

        if len(data) < tag_length:
            raise ValueError("Les données sont trop courtes pour contenir un tag valide.")
        
        ciphertext = data[:-tag_length]

        tag = data[-tag_length:]

        cipher = AES.new(key_aes, AES.MODE_GCM, nonce=iv_base64)

        plaintext_bytes = cipher.decrypt_and_verify(ciphertext, tag)

        return plaintext_bytes.decode('utf-8')
    
    except (ValueError, UnicodeDecodeError) as e:
        print("Erreur lors du déchiffrement ou décodage :", e)


    LOGGER.debug('[%s] ----  FIN  ----', methode_name)


