Our twitter: https://twitter.com/FTMTeam1

Discord for questions: https://discord.gg/6ZPvDCR8Xd

Aptos is still in an early stage, source code keeps changing. We will update as soon as we can, but if you have questions, head into our discord for help.
# Aptos NFT Mint

The Aptos NFT Mint project is designed to let users make a mint contract and website ultra fast on Aptos.

An onchain contract which let user to create mint contract fast.

## Features developed
* Set start and finish time for everyone.
* Won't accept your funds if they're out of NFTs to sell.
* Wallet based white list
* Royalties for your NFT
* Asset upload on IPFS
* Integrated with all the marketplace and wallets on Aptos
* Simple website with wallet integrated and monitor your candy machine status

## Getting Set Up
```sh
git clone https://github.com/FTM-Labs/AptosNFTMint.git
```

## Switch network
go to `constants.py` and change `MODE` to be 'test' for using 'devnet' or 'mainnet' for using 'mainnet'.


### Generate art and metadata

Thre are a bunch of solutions to generate NFT art and metadata. We recommend to use [HashLips](https://github.com/HashLips/hashlips_art_engine).
Its simple and flexble.

Basically, you need layered art and use hashlips the generate images and metadata.

The metadata format we need is super simple. (the metadata format you generated from hashlips will work, we will just ignore the other attributes)

```json
{
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
After generated the metadata, put it in a folder with your images. The folder needs to be created like below:
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

### Install dependencies

You need python version 3.9 and above

```sh
cd script/third_party
pip3 install -r requirements.txt
```
### Create candy machine
Open config.json under src folder (using VS code or other IDE). 
#### Collection metadata
```json
    "collection": {
        "assetDir": "the Assets folder path you created above, eg: /User/ftm/Assets",
        "metadataDir": "the metadata folder path you created above, eg: /User/ftm/Assets",
        "collectionName": "your collection name, eg: TestCollection",
        "collectionDescription": "eg: Follow us on twitter https://twitter.com/FTMTeam1",
        "collectionCover": "this is will be updated autmatically",
        "collectionSize": "e.g:10000",
        "mintFee": "mint fee by Aptos Coin, e.g inpit 1 for 1 Aptos mint fee",
        "presaleMintTime": "Unix timestamp, go to https://www.unixtimestamp.com/, covert your desired time to unix time, eg: 1661257636",
        "publicMintTime": "Unix timestamp, go to https://www.unixtimestamp.com/, covert your desired time to unix time, eg: 1661257636",
        "whitelistDir": "the folder path that contains whitelist.txt."
    }
```
#### Candymachine metadata
```
    "candymachine": {
        "cmPublicKey": "",
        "cmPrivateKey": "",
        "account_address": "",
        "account_private_key": ""
    },
```
leave `cmPublicKey` and `cmPrivateKey` blank. You need to have an account with some funds in it and put the account address and private key. This is used to create you candy machine, so make sure you have some funds to cover the gas.
#### Pinata API key
We will be using [Pinata](https://www.pinata.cloud/?gclid=CjwKCAjwu5yYBhAjEiwAKXk_eKjm7QEJ2EiRMrXVFVECHFCmRmuHj3btPYzJCxhBLU7XdN0np5vTdBoC6n0QAvD_BwE) to batch upload your images and metadata to ipfs. Pinata is the most used service for upload NFT images and metadata to ipfs.

Register an account -> click the icon on top right -> click API key -> New Key -> enable pinFileToIPFS -> copy your public key and private key.

Open config.json under src folder (using VS code or other IDE).

Set Pinata keys.
```json
"pinata" :{
"pinataApi": "https://api.pinata.cloud/pinning/pinFileToIPFS",
"pinataPublicKey" : "your pinata public key"
"pinataSecretKey" : "your pinata secret key"
}
```

under src folder, run
```bash
python3 cli.py
```
Choose "Create candy machine"
Enter yes to if you have transferred at least 2 aptos to candy machine account: yes
*** on testnet, we automatically deposited 2000 aptos to the candy machine account.
***Update WL will override the past WL configuration. If you want to add some more wl spots, just add below the previous file and upload it.***

### WhiteList
Create a txt file with you white list info
```txt
0x6c4e890a882b013f82a65db9b917a6d285caa892e46f2d93808b56f2aab2dd92 2
0x9d40f83eee59912bed7488d49becd5274ec21c66c40931c9db95a501e03ecee2 3
0x6c4e890a882b013f82a65db9b917a6d285caa892e46f2d93808b56f2aab2dd92 2
```
each line must have a wallet address and how many can this wallet mint in white list phase

Open config.json under src folder (using VS code or other IDE). 

change whitelistDir
```json
    "collection": {
        "whitelistDir": "the folder path that contains whitelist.txt."
    }
```
under src folder, run
```bash
python3 cli.py
```
Choose "Update WL for existing collection"

### Create website
You need to have npm installed, we are using nextJS to build this simple website
open mint-site folder, run

```bash
npm install next react react-dom
```

then run
```bash
npm run dev
```
