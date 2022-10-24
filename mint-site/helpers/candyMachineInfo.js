export const candyMachineAddress = "0x8095f6c0b7d7b88294ff999e4a18e6d46c2bf02551914102aaf72d37000604e1";
export const collectionName = "Test"; // Case sensitive!
export const collectionCoverUrl = "https://cloudflare-ipfs.com/ipfs/QmeCuKGLvAGrBAPGdaRh2hkTjXsXuk8VEUHNoYRD4cJG51";
export const mode = "test"; // "dev" or "test" or "mainnet"

export let NODE_URL;
export const CONTRACT_ADDRESS = "0xc071ef709539f7f9372f16050bf984fe6f11850594b8394f11bc74d22f48836b";
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