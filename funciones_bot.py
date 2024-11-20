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
                new_url = f"{self.base_url}/citar?p={provincia_id}&locale=es"
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
        

def main():
    bot = NieBot()
    bot.select_province("Madrid")

if __name__ == "__main__":
    main()