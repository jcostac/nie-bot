from playwright.sync_api import sync_playwright, Page, Browser
import bs4 as bs
import data_config as config
import random
import time

class NieBotPlaywright:
    def __init__(self):
        # Configuration
        self.base_url = config.base_url
        self.dct_provincias = config.dct_provincias
        self.doc_type = config.doc_type
        self.nombre = config.nombre
        self.doc_id = config.documento_id
        self.ubicacion_usuario = config.ubicacion_usuario
        
        # Initialize Playwright
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False,  # Set to False to see the browser in action
            args=['--no-sandbox']
        )
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        self.page = self.context.new_page()
        self.page.set_default_timeout(30000)  # 30 seconds timeout

    @staticmethod
    def check_oficinas(provincia: str, municipalidad: str) -> list:
        """Return a list with the available offices for a given province"""
        try:    
            if municipalidad == "any":
                return str(99)  # return "Cualquier oficina"

            if provincia == "Madrid":
                dct_oficinas = config.dct_oficinas_madrid
                office_keys = list(dct_oficinas.keys())
            else:
                print(f"No available offices for {provincia}")
                return None

            if municipalidad:
                matching_office_keys = [
                    office
                    for office in office_keys 
                    if municipalidad.lower() in office.lower()
                ]
                
                if matching_office_keys:
                    filtered_offices = {
                        key: dct_oficinas[key] 
                        for key in matching_office_keys
                    } 
                
                return list(str(filtered_offices.values()))
               
        except Exception as e:
            print(f"Error in extracting codes associated to offices: {e}")
            return None

    @staticmethod
    def check_id_validity(doc_id: str, doc_type: str) -> bool:
        """Check if the document ID is valid"""
        if doc_type == "N.I.E.":
            return len(doc_id) == 9 and doc_id[0].isalpha() and doc_id[1:-1].isdigit() and doc_id[-1].isalpha()
        elif doc_type == "D.N.I.":
            return len(doc_id) == 9 and doc_id[:-1].isdigit() and doc_id[-1].isalpha()
        else:  # for pasaporte no need to check anything
            return True

    def create_session(self):
        """Initialize session using Playwright"""
        try:
            time.sleep(random.uniform(1, 3))
            response = self.page.goto(self.base_url)
            return response.ok
        except Exception as e:
            print(f"Error creating session: {e}")
            return False

    def check_session_expired(self, html_content):
        """Check if session has expired"""
        soup = bs.BeautifulSoup(html_content, 'html.parser')
        error_div = soup.find('div', class_='mf-msg__error')
        info_div = soup.find('div', id="mensajeinfo")
        
        if (error_div and "sesión ha caducado" in error_div.text) or \
           (info_div and "sesión ha caducado" in info_div.text):
            print("Session expired")
            return True
        return False

    def select_province(self, provincia: str):
        """Select a province using Playwright"""
        try:
            if provincia in self.dct_provincias.keys():
                provincia_id = str(self.dct_provincias[provincia])
                url = f"{self.base_url}/icpplus/citar?p={provincia_id}&locale=es"
                
                response = self.page.goto(url)
                if response.ok:
                    print(f"Success: {self.page.url}")
                    return self.page.content()
                else:
                    raise Exception(f"Error: Status code {response.status}")
                    
        except Exception as e:
            print(e)
            return None

    def submit_tramite_form(self, oficina):
        """Submit the tramite form using Playwright"""
        try:
            # Wait for and fill form fields
            self.page.wait_for_selector('select[name="sede"]')
            self.page.select_option('select[name="sede"]', oficina)
            
            # Find and click submit button
            self.page.click('input[type="submit"]')
            
            # Wait for navigation
            self.page.wait_for_load_state('networkidle')
            
            print(f"Success: {self.page.url}")
            return self.page.content()
            
        except Exception as e:
            print(e)
            return None

    def seleccionar_tipo_presentacion(self):
        """Select tipo presentacion using Playwright"""
        try:
            # Wait for radio button
            self.page.wait_for_selector('input[type="radio"]')
            
            # Click first radio button (usually the correct one)
            self.page.click('input[type="radio"]')
            
            # Submit form
            self.page.click('input[type="submit"]')
            
            # Wait for navigation
            self.page.wait_for_load_state('networkidle')
            
            print(f"Success: {self.page.url}")
            return self.page.content()
            
        except Exception as e:
            print(e)
            return None

    def validar_entrada_datos_usuario(self):
        """Validate user data using Playwright"""
        try:
            # Wait for form elements
            self.page.wait_for_selector('select[name="rdbTipoDoc"]')
            
            # Fill form
            self.page.select_option('select[name="rdbTipoDoc"]', self.doc_type[0])
            self.page.fill('input[name="txtIdCitado"]', self.doc_id[0])
            self.page.fill('input[name="txtDesCitado"]', self.nombre[0].upper())
            
            # Submit form
            self.page.click('input[type="submit"]')
            
            # Wait for response
            self.page.wait_for_load_state('networkidle')
            
            # Check for button
            solicitar_cita_button = self.page.query_selector('input[value="Solicitar cita"]')
            
            if solicitar_cita_button:
                print("Successfully found button")
                return self.page.content()
            else:
                raise Exception("Solicitar cita button not found")
                
        except Exception as e:
            print(e)
            return None

    def __del__(self):
        """Cleanup Playwright resources"""
        try:
            self.context.close()
            self.browser.close()
            self.playwright.stop()
        except:
            pass


def main(provincia: str, municipalidad: str):
    bot = NieBotPlaywright()
    max_retries = 3
    current_try = 0
    
    while current_try < max_retries:
        try:
            if current_try > 0:
                delay = random.uniform(5, 10)
                print(f"Waiting {delay:.2f} seconds before retry...")
                time.sleep(delay)

            print("Selecting province...")
            time.sleep(random.uniform(1, 3))
            response = bot.select_province(provincia)
            if not response:
                raise Exception("Failed to select province")
            if bot.check_session_expired(response):
                bot.create_session()
                continue

            print("Checking oficinas...")
            time.sleep(random.uniform(2, 4))
            oficina = bot.check_oficinas(provincia, municipalidad)
            if not oficina:
                raise Exception("Failed to get oficina")

            print("Submitting tramite form...")
            time.sleep(random.uniform(1.5, 3.5))
            response = bot.submit_tramite_form(oficina)
            if not response:
                raise Exception("Failed to submit tramite form")
            if bot.check_session_expired(response):
                bot.create_session()
                continue

            print("Selecting tipo presentacion...")
            time.sleep(random.uniform(1, 3))
            response = bot.seleccionar_tipo_presentacion()
            if not response:
                raise Exception("Failed to select tipo presentacion")
            if bot.check_session_expired(response):
                bot.create_session()
                continue

            print("Validating user data...")
            time.sleep(random.uniform(2, 5))
            response = bot.validar_entrada_datos_usuario()
            if not response:
                raise Exception("Failed to validate user data")
            if bot.check_session_expired(response):
                bot.create_session()
                continue

            print("Process completed successfully!")
            return True

        except Exception as e:
            print(f"Error in attempt {current_try + 1}: {e}")
            current_try += 1
            
            if current_try < max_retries:
                wait_time = (2 ** current_try) + random.uniform(1, 5)
                print(f"Waiting {wait_time:.2f} seconds before next attempt...")
                time.sleep(wait_time)
            
            bot.create_session()

    print("Maximum retries reached. Please try again later.")
    return False


if __name__ == "__main__":
    main("Madrid", "any") 