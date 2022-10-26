export const candyMachineAddress = "0x40d906649750b18ab88a1dfa5c3217fa9b40b0d5a5ec8ed740989ca3f5da484f";
export const collectionName = "TestCollection101"; // Case sensitive!
export const collectionCoverUrl = "https://cloudflare-ipfs.com/ipfs/QmV9Qkoux7Xkrm2FjZmhkrDHnWAPV4LnZ8ZjQPBzLxtduf";
export const mode = "dev"; // "dev" or "test" or "mainnet"

export let NODE_URL;
export const CONTRACT_ADDRESS = "0xc071ef709539f7f9372f16050bf984fe6f11850594b8394f11bc74d22f48836b";
export const COLLECTION_SIZE = 4444
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
