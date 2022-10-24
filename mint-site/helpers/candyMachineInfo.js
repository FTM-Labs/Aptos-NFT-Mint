export const candyMachineAddress = process.env.NEXT_PUBLIC_CANDY_MACHINE_ID;
export const collectionName = process.env.NEXT_PUBLIC_COLLECTION_NAME;
export const collectionCoverUrl = process.env.NEXT_PUBLIC_COLLECTION_IMAGE_URI;
export const mode = process.env.NEXT_PUBLIC_APTOS_NETWORK;


export let NODE_URL;
let FAUCET_URL;

if (mode === "dev") {
  NODE_URL = "https://fullnode.devnet.aptoslabs.com/v1";
  FAUCET_URL = "https://faucet.devnet.aptoslabs.com";
} else if (mode === "test") {
  NODE_URL = "https://fullnode.testnet.aptoslabs.com/v1";
  FAUCET_URL = "https://faucet.testnet.aptoslabs.com";
} else {
  NODE_URL = "https://fullnode.mainnet.aptoslabs.com/v1";
  FAUCET_URL = null;
}
