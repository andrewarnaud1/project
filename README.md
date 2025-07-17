        html_lower = html_content.lower()
        
        for pattern in patterns:
            matches = re.finditer(pattern, html_lower, re.IGNORECASE)
            for match in matches:
                if match.groups():
                    # Si le pattern capture un code d'erreur
                    code = match.group(1)
                    errors.append(f"Code d'erreur HTTP {code}")
                else:
                    # Si le pattern capture un message complet
                    matched_text = match.group(0)
                    if 'problem' in matched_text or 'error' in matched_text:
                        errors.append("Erreur HTTP détectée dans la page")
                    elif 'server' in matched_text:
                        errors.append("Erreur serveur détectée")
                    elif 'unavailable' in matched_text or 'indisponible' in matched_text:
                        errors.append("Service indisponible")
                
                # Limiter à 3 erreurs maximum
                if len(errors) >= 3:
                    break
        
        return errors
