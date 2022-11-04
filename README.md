# Disclaimer 

We are not affiliated with Aptos or any NFT project. We develop tools for everyone to use, at their own risk.

# What is this ?

The Aptos NFT Mint project is designed to let creators set up a candymachine for NFT minting and a minting website ultra fast on Aptos. Candy machine is originally from Solana. We use Candy machine here to refer to general nft minting system on blockchain. 

Our twitter: https://twitter.com/FTMTeam1

Discord for questions: https://discord.gg/6ZPvDCR8Xd

Aptos is still in an early stage, We will update as soon as we can, but if you have questions, head into our discord for help.

## Features developed
* Set start and finish time for everyone.
* Won't accept your funds if they're out of NFTs to sell.
* Wallet based whitelist.
* Royalties for your NFT.
* Asset upload on IPFS.
* Integrated with all the marketplace and wallets on Aptos.
* Fully customizable website with wallet integrated and your candy machine status displayed.

## Preparations
In order to use this tool, here are the few things you need to have before continuing:

### Code 
```sh
git clone https://github.com/FTM-Labs/AptosNFTMint.git
```
### Python3
You need python version 3.9 and above.
https://www.python.org/downloads/ 
### Install dependencies
You need python version 3.9 and above

```sh
cd script/third_party
pip3 install -r requirements.txt
```
### nodeJs and npm 
https://docs.npmjs.com/downloading-and-installing-node-js-and-npm
### NFT assets 
Thre are a bunch of solutions to generate NFT art and metadata. We recommend to use [HashLips](https://github.com/HashLips/hashlips_art_engine).
Its simple and flexble.

Basically, you need layered art and use hashlips the generate images and metadata.

The metadata format we need is super simple. (the metadata format you generated from hashlips will work, we will just ignore the extra fields.)
However, make sure each metadata file has a different, unique name.
```json
{
  "name": "NFT NAME",
  "description": "NFT description",
  "attributes": [
    { "trait_type": "Background", "value": "Black" },
    { "trait_type": "Eyeball", "value": "Red" },
    { "trait_type": "Eye color", "value": "Yellow" },
    { "trait_type": "Iris", "value": "Small" },
    { "trait_type": "Shine", "value": "Shapes" },
    { "trait_type": "Bottom lid", "value": "Low" },
    { "trait_type": "Top lid", "value": "Middle" }
  ]
}
```
After generated the metadata, put it in a separate folder than your images. The top level folder needs to be created like below:
```
Assets/  
├─ Images/  
|  |- cover.png
│  ├─ 1.png  
│  ├─ 2.png  
│  ├─ 3.png  
│  ├─ ...  
├─ metadata/  
│  ├─ 1.json  
│  ├─ 2.json  
│  ├─ ...  
```
where the `cover.png` is the cover image for the collection.

**The metadata and corresponding image should have the same name, eg: 1.png and 1.json**
### Aptos wallet
For mainnet and testnet [Aptos disabled the faucte to fund account in testnet], you must prepare your own Aptos wallet and transfer some funds into it to cover the transaction fee.

Martian: https://chrome.google.com/webstore/detail/martian-aptos-wallet/efbglgofoippbgcjepnhiblaibcnclgk

Petra: https://chrome.google.com/webstore/detail/petra-aptos-wallet/ejjladinnckdgjemekebdpeokbikhfci

**Our code will some check for the metadata format, you can disable it if you want in the code**

**Make sure the names for each nft (i.e the "name" field in individual NFT metadata) are unique. Two nft can not have the same name in the same collection. If you have duplicate names, there will be problem in your mint process.**

## Instructions

### Collection metadata
```json
"collection": {
    "assetDir": "/Users/Shared/assets/images",
    "metadataDir": "/Users/Shared/assets/metadata",
    "collectionName": "TestCollection101",
    "collectionDescription": "placeholder",
    "collectionCover": "",
    "collectionSize": 10,
    "maxMintPerWallet": 10,
    "mintFee": 100000000,
    "royalty_points_denominator": 1000,
    "royalty_points_numerator": 50,
    "presaleMintTime": 100000000,
    "publicMintTime": 100000000,
    "whitelistDir": "/Users/Shared/assets"
}
```
`assetDir`: Path to your image folder. Copy file path directly instead of manually putting it in to avoid errors.

`metadataDir`: Path to your metadata folder. Copy file path directly instead of manually putting it in to avoid errors.

`collectionName`: Your NFT collection name.

`collectionDescription`: Your NFT description.

`collectionCover`: if you have a image called `cover` then this will automatically be filled. Otherwise, you need to provide a link to your cover image.

`collectionSize`: Your NFT collection size.

`maxMintPerWallet`: How many mints per wallet allowed.

`mintFee`: 100000000 = 1 APT. e.g if you want 0.5 APT as mint fee, put 50000000.

`royalty_points_denominator`: denominator of royaltie points.

`royalty_points_numerator`: numerator of royaltie points.

`presaleMintTime`: presale mint time, whitelisted user can mint after this. unix timstamp in seconds. https://www.unixtimestamp.com/

`publicMintTime`: public mint time. unix timstamp in seconds. https://www.unixtimestamp.com/

`whitelistDir`: Path to whitelist file.

Whitelist file is a text file of the following format:

```txt
0x6c4e890a882b013f82a65db9b917a6d285caa892e46f2d93808b56f2aab2dd92 2
0x9d40f83eee59912bed7488d49becd5274ec21c66c40931c9db95a501e03ecee2 3
0x6c4e890a882b013f82a65db9b917a6d285caa892e46f2d93808b56f2aab2dd92 2
```
each line must have a wallet address and how many can this wallet mint in white list phase
### Candymachine metadata
```
    "candymachine": {
        "cmPublicKey": "",
        "cmPrivateKey": ""
    },
```
On devnet or testnet, leave `cmPublicKey` and `cmPrivateKey` blank as they will be generated and funded automatically.
On mainnet, you first have to create an account and send funds to it (used to create you candy machine, so make sure you have some funds to cover the gas.). You then have to export the account address and private key and input them in config.json.

### Storage 
We provide two options to upload your asstes. We will use Pinata as an example here. Please research yourself on how to set up arweave.
```
"storage": {
    "solution": "pinata",
    "pinata": {
        "pinataApi": "https://api.pinata.cloud/pinning/pinFileToIPFS",
        "pinataPublicKey": "",
        "pinataSecretKey": ""
    },
    "arweave": {
        "keyfilePath": "/Users/Shared/arweave-keyfile.json"
    }
},
```
We will be using [Pinata](https://www.pinata.cloud/?gclid=CjwKCAjwu5yYBhAjEiwAKXk_eKjm7QEJ2EiRMrXVFVECHFCmRmuHj3btPYzJCxhBLU7XdN0np5vTdBoC6n0QAvD_BwE) to batch upload your images and metadata to ipfs. Pinata is the most used service for upload NFT images and metadata to ipfs.

Register an account -> click the icon on top right -> click API key -> New Key -> enable pinFileToIPFS -> copy your public key and private key.

Open `config.json` under `src` folder (using VS code or other IDE).

Set Pinata keys.
```json
"pinata" :{
"pinataApi": "https://api.pinata.cloud/pinning/pinFileToIPFS",
"pinataPublicKey" : "your pinata public key"
"pinataSecretKey" : "your pinata secret key"
}
```

### Switch network
Go to `constants.py` and change `MODE` to be 'test' for `testnet` , 'dev' for `devnet` and 'mainnet' for using `mainnet`.
Make sure the mode in `candyMachineInfo.js` is set to the same.

### Create candy machine
under `src` folder, run
```bash
python3 cli.py
```
Choose `Create candy machine`.

***On devnet or testnet, we automatically deposited some aptos to the candy machine account.***

If you need more aptos in devnet, check how to use `faucet_client` to fund account in `prepareCandyMachineAccount` in `create_candy_machine.py`. As an example, you can write a for loop: 
```
for i in range(15):
    faucet_client.fund_account(alice.address(), 100000000)
```

If you want to change the maximum gas amount allowed, you can increase `MAX_GAS` in `constants.py`.

### Additional functions
We provide options to update presale mint time, public mint time, mint fee and whitelist. Simply modify the values in `config.json` and run the correspoinding command to update.

***Update WL will override the past WL configuration. If you want to add some more wl spots, just add below the previous file and upload it.***

### Create website
You need to have npm installed, we are using nextJS to build this simple website

change the values in `mint-site/helpers/candyMachineInfo.js` - can find those info in your config.json:

```txt
export const candyMachineAddress = "YOUR CM ADDRESS";
export const collectionName = "collection name(Case sensitive!)";
export const collectionCoverUrl = " THE COVER LINK eg: https://cloudflare-ipfs.com/ipfs/asjdhasjhd"; 
export const COLLECTION_SIZE = 10
```

open mint-site folder, run

```bash
npm install
```

then run
```bash
npm run dev
```
# Sanity check
1. Use the sample images and metadata first to check if everything works.
2. use test mint function from the cli to check if the minting is successful (preferably on devnet and testnet first). The test mint will attempt to ming ONE nft from your collection. On devnet, the program will automatically drop 3 Aptos, on testnet and mainnet, make sure your cm account has enough funds.)


# Troubleshooting

1. `ERESOURCE_ACCOUNT_EXISTS`: Currently one wallet can hold one resource account, this normally happen when creating candy machine on mainnet and for some reason (user interrupt or other errors) the process didint complete. If you collection has been successfully created, try `Retry failed uploads` from the cli menu. Otherwise, move your funds to a new wallet and paste in the account address and private key in `config.json` and try create candy machine again.
