import Head from 'next/head'
import React, { useEffect, useState } from 'react';
import styles from '../styles/Home.module.css'
import data from '../../script/src/config.json'

export default function Home() {
  const [sender, setSender] = useState(null)
  const [isWalletConnected, setIsWalletConnected] = useState(false)
  const [connenctButtonText, setConnenctButtonText] = useState('Connect');
  const connectWallet = async () => {
    if ("martian" in window) {
      console.log("connecting wallet")
      const response = await window.martian.connect();
      sender = response.address
      console.log(sender);
      setSender(sender)
      const isConnected = await window.martian.isConnected()
      if(isConnected) {
        setIsWalletConnected(true)
      }
      console.log("wallet connected");
      setConnenctButtonText('Connected');
      return;
    }
    window.open("https://www.martianwallet.xyz/", "_blank");
  };

  const mint = async () => {
    console.log(sender);
    // Generate a transaction
    const cmAddress = data.candymachine.cmPublicKey;
    const collectionName = data.collection.collectionName;
    const payload = {
      type: "entry_function_payload",
      function: "0xBDCDFC476D4DB40CBF4BF3B62E3973D10E1CB53B89D915F0815982A78BFCDE1F::candy_machine_v2::mint_tokens",
      type_arguments: [],
      arguments: [
      	cmAddress,
	      collectionName,
	      "1",
      ]
    };
    const transaction = await window.martian.generateTransaction(sender, payload);
    const txnHash = await window.martian.signAndSubmitTransaction(transaction);
    console.log(txnHash);
  }

  useEffect(() => {
    connectWallet()
  }, [])

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
            <button className={styles.button} onClick={connectWallet}>{connenctButtonText}</button>
          </div>
          <img src={"/Aptos.png"} style={{ width: "960px", height:"480px" }} />
          <div>
            <button className={styles.button} onClick={mint} disabled={!isWalletConnected}>Mint</button>
          </div>
        </main>

      </div>
    </div>
  )
}
