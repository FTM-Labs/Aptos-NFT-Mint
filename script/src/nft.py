class NFT:
    """represents an NFT"""
    def __init__(self, name, uri, metadataUri, description, propertyKey, propertyValue, propertyType):
        self.name = name
        self.uri = uri
        self.metadataUri = metadataUri
        self.description = description
        self.propertyKey = propertyKey
        self.propertyValue = propertyValue
        self.propertyType = propertyType