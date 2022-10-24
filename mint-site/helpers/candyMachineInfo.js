export const candyMachineAddress = "0x6390bcd78627597e7b431e74b7c0a7ef8a489a20bdd3ea164e10440c6deff97b";
export const collectionName = "Test"; // Case sensitive!
export const collectionCoverUrl = "https://cloudflare-ipfs.com/ipfs/QmeCuKGLvAGrBAPGdaRh2hkTjXsXuk8VEUHNoYRD4cJG51";
export const mode = "test"; // "dev" or "test" or "mainnet"

export let NODE_URL;
export const CONTRACT_ADDRESS = "0x8c77a08888a537c39449b9e2e33cab520f0427acadc373bb569239cb2f22676d";
export const COLLECTION_SIZE = 10
let FAUCET_URL;
if (mode == "dev") {
    NODE_URL = "https://fullnode.devnet.aptoslabs.com/v1";
    FAUCET_URL = "https://faucet.devnet.aptoslabs.com";
} else if (mode === "test") {
    NODE_URL = "https://fullnode.testnet.aptoslabs.com/v1";
    FAUCET_URL = "https://faucet.testnet.aptoslabs.com";
} else {
    NODE_URL = "https://fullnode.mainnet.aptoslabs.com/v1";
    FAUCET_URL = null;
}