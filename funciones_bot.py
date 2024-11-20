import bs4 as bs
import requests
import data_config as config


class NieBot:
    def __init__(self):
        self.base_url = config.base_url
        self.dct_provincias = config.dct_provincias
        self.nombre = config.nombre
        self.documento_id = config.documento_id
        self.ubicacion_usuario = config.ubicacion_usuario
        self.session = None #session object to store cookies
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    def create_session(self):
        """Initialize session and get necessary cookies"""
        try:
            self.session = requests.Session()
            # Get initial cookies
            response = self.session.get(self.base_url, headers=self.headers)
            if response.status_code == 200:
                return True
            
        except Exception as e:
            print(f"Error creating session: {e}")
            return False

    def select_province(self, provincia):
        """Select a province and get the URL to access the service"""
        try:
            # Ensure we have an active session
            if not self.session: #if no session, create one
                successful_session = self.create_session()
                if not successful_session: #if session creation failed, raise an exception
                    raise Exception("Failed to create session")

            #get province ID from dictionary
            if provincia in self.dct_provincias.keys():
                provincia_id = str(self.dct_provincias[provincia])
                new_url = f"{self.base_url}/icpplus/citar?p={provincia_id}&locale=es"
            else:
                raise Exception("Invalid province")
            
            # Use existing session for the request
            response = self.session.get(new_url, headers=self.headers, allow_redirects=True)

            if response.status_code == 200:
                print(f"Success: {response.url}")   
                return response.url
            else:
                print(f"Error al obtener datos de la URL: {response.status_code}")
                return None

        except Exception as e:
            print(f"Error al obtener datos de la URL: {e}")
            return None
    
    def check_oficinas(self, provincia):
        """Return a dictionary with the available offices for a given province"""
        if provincia == "Madrid":
            dct_oficinas = config.dct_oficinas_madrid
            return dct_oficinas
        else:
            print(f"No available offices for {provincia}")
            return None

    def submit_tramite_form(self, oficina):
        """Submit the tipo de tramite form after selecting province"""
        try:
            if not self.session:
                if not self.create_session():
                    return None

            # Endpoint URL
            endpoint = f"{self.base_url}/icpplustiem/acInfo"

            # Form data to be passed to the endpoint
            payload = {
                'b3610282-7cf2-441c-bd02-cd45817d4cf7': '',
                '92959092-dfe4-470b-8afc-348396cd6050': '93df6ecb-e502-4603-8b56-146b09ccdadc',
                'sede': '99', #cualquier oficina = value 99
                'tramiteGrupo[0]': '4038' #value 4038 = NIE
            }

            # Additional headers needed for this specific request
            post_headers = self.headers.copy()  # Start copy base header
            post_headers.update({
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://icp.administracionelectronica.gob.es',
                'Referer': f'{self.base_url}/icpplustiem/citar?p=28&locale=es',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            })

            # Make the POST request
            response = self.session.post(
                endpoint,
                data=payload,
                headers=post_headers,
                allow_redirects=True
            )

            if response.status_code == 200:
                print(f"Success: {response.url}")
                return response
            else:
                print(f"Error submitting form: {response.status_code}")
                return None

        except Exception as e:
            print(f"Error in submit_form: {e}")
            return None

def main():
    bot = NieBot()
    bot.select_province("Madrid")

if __name__ == "__main__":
    main()