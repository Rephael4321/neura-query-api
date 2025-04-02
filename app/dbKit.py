class DBKit():
    def __init__(self):
        self.provider: str = ""
        self.metadata: list[str] = []

    def setProvider(self, provider: str):
        self.provider = provider
    
    def getProvider(self) -> str:
        return self.provider
    
    def setMetadata(self, metadata: list[str]):
        self.metadata = metadata

    def getMetadata(self) -> list[str]:
        return self.metadata

class DBKitManager():
    def __init__(self):
        self.objects: dict[str, DBKit] = dict()
    
    def setKit(self, username: str) -> None:
        self.objects[username] = DBKit()
    
    def getKit(self, username: str) -> DBKit:
        return self.objects[username]
