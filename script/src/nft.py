class NFT:
    """represents an NFT"""
    def __init__(self, name, uri, metadataUri, description):
        self.name = name
        self.uri = uri
        self.metadataUri = metadataUri
        self.description = description
