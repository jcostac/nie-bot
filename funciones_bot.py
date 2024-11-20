import bs4 as bs
import requests
import data_config as config


class NieBot:
    def __init__(self):
        #base url
        self.base_url = config.base_url

        #provinces dictionary
        self.dct_provincias = config.dct_provincias

        #user data
        self.doc_type = config.doc_type
        self.nombre = config.nombre
        self.doc_id = config.documento_id
        self.ubicacion_usuario = config.ubicacion_usuario

        #session object to store cookies
        self.session = None

        #headers to simulate a browser request
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    @staticmethod
    def check_oficinas(provincia: str, municipalidad: str) -> list:
        """Return a list with the available offices for a given province"""

        try:    
            if municipalidad == "any":
                return str(99)  #return "Cualquier oficina"

            if provincia == "Madrid":
                dct_oficinas = config.dct_oficinas_madrid
                office_keys = list(dct_oficinas.keys()) #get keys from dictionary
            else:
                print(f"No available offices for {provincia}")
                return None

            if municipalidad:
                    # Find all office keys containing the municipality name (case insensitive)
                    matching_office_keys = [
                        office
                        for office in office_keys 
                        if municipalidad.lower() in office.lower()
                    ] #append to list if municipality name is in office key
                    
                    # Create filtered dictionary with matching offices
                    if matching_office_keys:
                        filtered_offices = {
                            key: dct_oficinas[key] 
                            for key in matching_office_keys
                        } 
                    
                    #return matching offices values as a list as strings
                    return list(str(filtered_offices.values()))
               
        
        except Exception as e:
            print(f"Error in extracting codes associated to offices: {e}")
            return None
    
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

    def select_province(self, provincia: str):
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
                return
            else:
                print(f"Error al obtener datos de la URL: {response.status_code}")
                return 

        except Exception as e:
            print(f"Error al obtener datos de la URL: {e}")
            return

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
                'sede': oficina, #cualquier oficina = value 99
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

    def seleccionar_tipo_presentacion(self):
        """Select the type of presentation (sin Cl@ve)"""
        try:
            if not self.session:
                if not self.create_session():
                    return None

            # Endpoint URL
            endpoint = f"{self.base_url}/icpplustiem/acEntrada"

            # Form data
            payload = {
                'cadd9228-55db-4f0e-a246-243388f877bc': '',
                '6ae34d68-b97d-4558-ac35-af1d352d19d7': 'b8872b92-bbcd-482a-978e-9d3977f0bc37',
                'acceso': 'N'  # N presumably means "sin Cl@ve"
            }

            # Additional headers for this specific request
            post_headers = self.headers.copy()
            post_headers.update({
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://icp.administracionelectronica.gob.es',
                'Referer': f'{self.base_url}/icpplustiem/acInfo',  # Previous page URL
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
                print(f"Error selecting tipo presentacion: {response.status_code}")
                return None

        except Exception as e:
            print(f"Error in seleccionar_tipo_presentacion: {e}")
            return None

    def validar_entrada(self, doc_type: str, documento_id: str, nombre: str):
        """Validar entrada de datos del usuario"""
        try: 
            if not self.session:
                if not self.create_session():
                    return None

            # Endpoint URL
            endpoint = f"{self.base_url}/icpplustiem/acValidarEntrada"

            # Payload data
            payload = {
                'cfcbe634-ce1e-41d3-827b-82f23bc96a73': '65732fb4-5d2d-4e86-97f2-4417509eff95',
                'de8f94fc-551d-4835-bf33-0241152d1c2e': '',
                'rdbTipoDoc': self.doc_type[0],  # Can be 'N.I.E.', 'D.N.I.' or 'Pasaporte'
                'txtIdCitado': self.doc_id[0],  # The document number
                'txtDesCitado': self.nombre[0].upper()  # Name in uppercase
            }

            # Additional headers for this specific request
            post_headers = self.headers.copy()
            post_headers.update({
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://icp.administracionelectronica.gob.es',
                'Referer': f'{self.base_url}/icpplustiem/acEntrada',  # Previous page URL
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
                print(f"Error validating entrada: {response.status_code}")
                return None

        except Exception as e:
            print(f"Error in validar_entrada: {e}")
            return None

def main(provincia: str, municipalidad: str):
    bot = NieBot()
    bot.select_province(provincia)
    oficina = bot.check_oficinas(provincia, municipalidad)
    bot.submit_tramite_form(oficina)
    bot.seleccionar_tipo_presentacion()


if __name__ == "__main__":
    main()

    

