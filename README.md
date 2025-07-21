Parfait ! Voici comment faire de la reconnaissance d’image avec Playwright Python pour automatiser des actions dans une VM via Guacamole :

## 1. Installation des dépendances

```bash
pip install playwright opencv-python pillow pytesseract numpy
playwright install
```

## 2. Classe helper pour l’automation Guacamole

```python
import asyncio
import cv2
import numpy as np
from PIL import Image
import pytesseract
from playwright.async_api import async_playwright, Page
import os
import time

class GuacamoleAutomation:
    def __init__(self, page: Page):
        self.page = page
        self.canvas = None
        
    async def initialize(self, guacamole_url: str, username: str, password: str):
        """Initialise la connexion Guacamole"""
        await self.page.goto(guacamole_url)
        
        # Connexion (adaptez selon votre interface)
        await self.page.fill('#username', username)
        await self.page.fill('#password', password)
        await self.page.click('#login-button')
        
        # Attendre et sélectionner la VM
        await self.page.wait_for_selector('canvas')
        self.canvas = self.page.locator('canvas')
        
    async def take_screenshot(self, path: str = 'temp_screen.png'):
        """Prend une capture d'écran du canvas"""
        await self.canvas.screenshot(path=path)
        return path
        
    async def find_image(self, template_path: str, threshold: float = 0.8):
        """Trouve une image template dans le canvas"""
        # Prendre une capture d'écran
        screenshot_path = await self.take_screenshot()
        
        # Charger les images
        screenshot = cv2.imread(screenshot_path)
        template = cv2.imread(template_path)
        
        if screenshot is None or template is None:
            return {'found': False, 'error': 'Could not load images'}
        
        # Conversion en niveaux de gris pour améliorer la détection
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        # Reconnaissance de motif
        result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            # Calculer le centre de l'image trouvée
            h, w = template_gray.shape
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            
            return {
                'found': True,
                'x': center_x,
                'y': center_y,
                'confidence': max_val,
                'top_left': max_loc,
                'bottom_right': (max_loc[0] + w, max_loc[1] + h)
            }
        
        return {'found': False, 'confidence': max_val}
    
    async def wait_for_image(self, template_path: str, timeout: int = 30, threshold: float = 0.8):
        """Attend qu'une image apparaisse"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = await self.find_image(template_path, threshold)
            if result['found']:
                return result
            await asyncio.sleep(1)
        
        raise TimeoutError(f"Image {template_path} not found within {timeout} seconds")
    
    async def click_image(self, template_path: str, threshold: float = 0.8):
        """Clique sur une image trouvée"""
        result = await self.wait_for_image(template_path, threshold=threshold)
        await self.canvas.click(position={'x': result['x'], 'y': result['y']})
        await asyncio.sleep(0.5)  # Attendre que l'action soit traitée
        
    async def find_text(self, search_text: str, confidence_threshold: int = 60):
        """Trouve du texte via OCR"""
        screenshot_path = await self.take_screenshot()
        
        # Utiliser pytesseract pour l'OCR
        try:
            data = pytesseract.image_to_data(Image.open(screenshot_path), output_type=pytesseract.Output.DICT)
            
            for i, text in enumerate(data['text']):
                if (search_text.lower() in text.lower() and 
                    int(data['conf'][i]) > confidence_threshold):
                    
                    # Calculer le centre du texte
                    x = data['left'][i] + data['width'][i] // 2
                    y = data['top'][i] + data['height'][i] // 2
                    
                    return {
                        'found': True,
                        'x': x,
                        'y': y,
                        'confidence': data['conf'][i],
                        'text': text
                    }
            
            return {'found': False}
            
        except Exception as e:
            return {'found': False, 'error': str(e)}
    
    async def wait_for_text(self, search_text: str, timeout: int = 30):
        """Attend qu'un texte apparaisse"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = await self.find_text(search_text)
            if result['found']:
                return result
            await asyncio.sleep(1)
        
        raise TimeoutError(f"Text '{search_text}' not found within {timeout} seconds")
    
    async def click_text(self, search_text: str):
        """Clique sur un texte trouvé"""
        result = await self.wait_for_text(search_text)
        await self.canvas.click(position={'x': result['x'], 'y': result['y']})
        await asyncio.sleep(0.5)
        
    async def type_text(self, text: str):
        """Tape du texte"""
        await self.page.keyboard.type(text)
        
    async def send_key(self, key: str):
        """Envoie une touche spécifique"""
        await self.page.keyboard.press(key)
        
    async def double_click_image(self, template_path: str, threshold: float = 0.8):
        """Double-clique sur une image"""
        result = await self.wait_for_image(template_path, threshold=threshold)
        await self.canvas.dblclick(position={'x': result['x'], 'y': result['y']})
        await asyncio.sleep(0.5)
        
    async def right_click_image(self, template_path: str, threshold: float = 0.8):
        """Clic droit sur une image"""
        result = await self.wait_for_image(template_path, threshold=threshold)
        await self.canvas.click(position={'x': result['x'], 'y': result['y']}, button='right')
        await asyncio.sleep(0.5)
```

## 3. Exemple d’utilisation complète

```python
async def main():
    async with async_playwright() as p:
        # Lancer le navigateur
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Initialiser l'automation
        automation = GuacamoleAutomation(page)
        await automation.initialize(
            guacamole_url="http://your-guacamole-server",
            username="your-username",
            password="your-password"
        )
        
        try:
            # Attendre que le bureau soit chargé
            await automation.wait_for_image("desktop_background.png", timeout=60)
            print("Bureau chargé !")
            
            # Ouvrir le menu démarrer (Windows)
            await automation.click_image("start_button.png")
            
            # Ou utiliser OCR pour cliquer sur du texte
            await automation.click_text("Notepad")
            
            # Attendre que Notepad s'ouvre
            await automation.wait_for_image("notepad_window.png")
            
            # Taper du texte
            await automation.type_text("Hello from Playwright Python!")
            
            # Sauvegarder (Ctrl+S)
            await automation.send_key("Control+s")
            
            # Attendre la boîte de dialogue de sauvegarde
            await automation.wait_for_text("Save As")
            
            # Taper le nom du fichier
            await automation.type_text("test_file.txt")
            
            # Cliquer sur Save
            await automation.click_text("Save")
            
            print("Automation terminée avec succès !")
            
        except Exception as e:
            print(f"Erreur: {e}")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## 4. Utilitaires supplémentaires

```python
class ImageUtils:
    @staticmethod
    def create_template_from_screenshot(screenshot_path: str, x: int, y: int, width: int, height: int, output_path: str):
        """Crée un template à partir d'une zone d'une capture d'écran"""
        image = cv2.imread(screenshot_path)
        template = image[y:y+height, x:x+width]
        cv2.imwrite(output_path, template)
        
    @staticmethod
    def enhance_image_for_ocr(image_path: str, output_path: str):
        """Améliore une image pour l'OCR"""
        image = cv2.imread(image_path)
        
        # Conversion en niveaux de gris
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Réduction du bruit
        denoised = cv2.medianBlur(gray, 3)
        
        # Amélioration du contraste
        enhanced = cv2.convertScaleAbs(denoised, alpha=1.5, beta=0)
        
        cv2.imwrite(output_path, enhanced)
        
    @staticmethod
    def find_multiple_images(screenshot_path: str, template_path: str, threshold: float = 0.8):
        """Trouve plusieurs occurrences d'une image"""
        screenshot = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        
        matches = []
        h, w = template.shape
        
        for pt in zip(*locations[::-1]):
            matches.append({
                'x': pt[0] + w // 2,
                'y': pt[1] + h // 2,
                'confidence': result[pt[1], pt[0]]
            })
        
        return matches
```

## 5. Configuration et conseils

```python
# Configuration pour pytesseract (si besoin)
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows

# Pour de meilleures performances OCR
def configure_tesseract_for_gui():
    """Configuration optimisée pour les interfaces graphiques"""
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
    return custom_config

# Utilisation avec configuration personnalisée
async def find_text_optimized(self, search_text: str):
    screenshot_path = await self.take_screenshot()
    custom_config = configure_tesseract_for_gui()
    
    data = pytesseract.image_to_data(
        Image.open(screenshot_path), 
        config=custom_config,
        output_type=pytesseract.Output.DICT
    )
    # ... reste du code
```

## Conseils pour de meilleurs résultats

1. **Qualité des templates** : Créez des templates nets et contrastés
1. **Seuils adaptatifs** : Ajustez le threshold selon le contexte (0.7-0.9)
1. **Gestion des résolutions** : Testez sur différentes résolutions d’écran
1. **OCR optimisé** : Utilisez des configurations Tesseract adaptées à votre interface
1. **Gestion d’erreurs** : Implémentez des retry et des timeouts appropriés

Cette approche vous donnera une solution robuste pour automatiser n’importe quelle application dans votre VM via Guacamole !​​​​​​​​​​​​​​​​