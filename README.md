        # Patterns pour détecter les erreurs HTTP dans le HTML
        patterns = [
            # Error code: 500, 404, etc.
            r'error\s*code\s*:\s*([45]\d{2})',
            r'code\s*erreur\s*:\s*([45]\d{2})',
            
            # data-l10n-args avec responsestatus
            r'data-l10n-args="[^"]*responsestatus[^"]*:([45]\d{2})',
            r'responsestatus[^"]*:([45]\d{2})',
            
            # Messages d'erreur classiques
            r'internal\s*server\s*error',
            r'not\s*found.*404',
            r'service\s*unavailable',
            r'bad\s*gateway',
            r'gateway\s*timeout',
            
            # Messages français
            r'erreur\s*du\s*serveur',
            r'page\s*introuvable',
            r'service\s*indisponible',
            r'erreur\s*interne',
            
            # Titres d'erreur
            r'<title[^>]*>.*problem.*loading.*page.*</title>',
            r'<title[^>]*>.*erreur.*</title>',
            r'<title[^>]*>.*error.*</title>',
            
            # Classes CSS d'erreur
            r'class="[^"]*error[^"]*"',
            r'class="[^"]*neterror[^"]*"',
            
            # IDs d'erreur
            r'id="[^"]*error[^"]*"',
            
            # Texte "looks like there's a problem"
            r'looks\s*like.*problem.*site',
            r'problème.*site',
        ]
