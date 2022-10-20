import Head from 'next/head'
import React, { useEffect, useState } from 'react';
import styles from '../styles/Home.module.css'
import data from '../../script/src/config.json'

import { AptosClient } from "aptos";
import { useWallet } from '@manahippo/aptos-wallet-adapter';
import cmHelper from "../helpers/candyMachineHelper"
import ConnectWalletButton from '../helpers/Aptos/ConnectWalletButton';
import {candyMachineAddress, collectionName, collectionCoverUrl, NODE_URL} from "../helpers/candyMachineInfo"

import Spinner from "react-bootstrap/Spinner"

const aptosClient = new AptosClient(NODE_URL);

export default function Home() {
  // const [sender, setSender] = useState(null)
  // const [isWalletConnected, setIsWalletConnected] = useState(false)
  // const [connenctButtonText, setConnenctButtonText] = useState('Connect');

  const wallet = useWallet();
  const [numToMint, setNumToMint] = useState(1)
  const [candyMachineData, setCandyMachineData] = useState({data: {}, fetching: false, fetch: fetchCandyMachineData})
  const [timeLeftToMint, setTimeLeftToMint] = useState({presale: "", public: ""})

  useEffect(() => {
    if (!wallet.autoConnect && wallet.wallet?.adapter) {
        wallet.connect();
    }
  }, [wallet.autoConnect, wallet.wallet, wallet.connect]);

  const mint = async () => {
    if (wallet.account?.address?.toString() === undefined) return;

    console.log(wallet.account?.address?.toString());
    // Generate a transaction
    const payload = {
      type: "entry_function_payload",
      function: "0xdcd69bc972f11bfbc3de6a8b656b66a227fe4d38c8880c781e8bf8785195e1a9::candy_machine_v2::mint_tokens",
      type_arguments: [],
      arguments: [
      	candyMachineAddress,
	      collectionName,
	      numToMint,
      ]
    };

    let txInfo;
    try {
      const txHash = await wallet.signAndSubmitTransaction(payload);
      console.log(txHash);
      txInfo = await aptosClient.waitForTransactionWithResult(txHash.hash)
    } catch (err) {
      txInfo = {
        success: false,
        vm_status: err.message,
      }
    }
    console.log(txInfo);
    console.log(txInfo.success ? "Mint success!" : `Mint failure, an error occured.`)
  }

  async function fetchCandyMachineData() {
    setCandyMachineData({...candyMachineData, fetching: true})
    const cmResourceAccount = await cmHelper.getCandyMachineResourceAccount();
    if (cmResourceAccount === null) {
      setCandyMachineData({...candyMachineData, data: {}, fetching: false})
      return
    }
    const collectionInfo = await cmHelper.getCandyMachineCollectionInfo(cmResourceAccount);
    const configData = await cmHelper.getCandyMachineConfigData(collectionInfo.candyMachineConfigHandle);
    setCandyMachineData({...candyMachineData, data: {cmResourceAccount, ...collectionInfo, ...configData}, fetching: false})
  }

  function verifyTimeLeftToMint() {
    setTimeout(verifyTimeLeftToMint, 1000)
    if (candyMachineData.data.presaleMintTime === undefined || candyMachineData.data.publicMintTime === undefined) return

    const currentTime = Math.round(new Date().getTime() / 1000);
    setTimeLeftToMint({presale: cmHelper.getTimeDifference(currentTime, candyMachineData.data.presaleMintTime), public: cmHelper.getTimeDifference(currentTime, candyMachineData.data.publicMintTime)})
  }

  useEffect(() => {
    fetchCandyMachineData()
  }, [])

  useEffect(() => {
    verifyTimeLeftToMint()
  }, [candyMachineData])

  return (
    <div className="bg-gray-500">
      <div className={styles.container}>
        <Head>
          <title>Aptos NFT Mint</title>
          <meta name="description" content="Aptos NFT Mint" />
          <link rel="icon" href="/favicon.ico" />
        </Head>

        <main className={styles.main}>
          <h1 className={styles.title}>
            Aptos NFT Mint
          </h1>
          <div className={styles.topcorner}>
            <ConnectWalletButton connectButton={!wallet.connected} className="d-flex" />
          </div>
          <img src={collectionCoverUrl} style={{ width: "480px", height:"480px" }} />
          <div id="collection-info" className="d-flex flex-column align-items-center" style={{width: "80%"}}>
            {candyMachineData.fetching ? <Spinner animation="border" role="status" className="mt-5"><span className="visually-hidden">Loading...</span></Spinner> : 
            <>
              <div className="d-flex">
                <input type="number" min="1" max={candyMachineData.data.maxMintsPerWallet === undefined ? 10 : candyMachineData.data.maxMintsPerWallet} value={numToMint} onChange={(e) => setNumToMint(e.target.value)} />
                <button className={styles.button} onClick={mint} disabled={!wallet.connected}>Mint</button>
              </div>
              <div className="d-flex justify-content-between align-items-center w-100 mt-3">
                <span>Minted NFTs: </span><span>{candyMachineData.data.numMintedTokens}/{candyMachineData.data.numUploadedTokens}</span>
              </div>
              <div className="d-flex justify-content-between align-items-center w-100">
                <span>Is Mint Public: </span><span style={{width: "15px", height: "15px", borderRadius: "50%", background: candyMachineData.data.isPublic ? "green" : "red"}}></span>
              </div>
              <div className="d-flex justify-content-between align-items-center w-100">
                <span>Mint fee: </span><span>{candyMachineData.data.mintFee} APT</span>
              </div>
              <div className="d-flex justify-content-between align-items-center w-100">
                <span>Max mints per wallet: </span><span>{candyMachineData.data.maxMintsPerWallet}</span>
              </div>
              <div className="d-flex justify-content-between align-items-center w-100">
                <span>Presale mint: </span><span>{timeLeftToMint.presale}</span>
              </div>
              <div className="d-flex justify-content-between align-items-center w-100">
                <span>Public mint: </span><span>{timeLeftToMint.public}</span>
              </div>
            </>}
          </div>
        </main>

      </div>
    </div>
  )
}
