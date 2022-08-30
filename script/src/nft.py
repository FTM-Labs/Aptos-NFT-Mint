class NFT:
    """represents an NFT"""
    def __init__(self, name, uri, description, propertyKey, propertyValue, propertyType):
        self.name = name
        self.uri = uri
        self.description = description
        self.propertyKey = propertyKey
        self.propertyValue = propertyValue
        self.propertyType = propertyType