import Head from 'next/head'
import React, { useEffect, useState } from 'react';
import styles from '../styles/Home.module.css'

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
    const payload = {
      type: "entry_function_payload",
      function: "0xBDCDFC476D4DB40CBF4BF3B62E3973D10E1CB53B89D915F0815982A78BFCDE1F::candy_machine_v2::mint_tokens",
      type_arguments: [],
      arguments: [
      	"0xe423e793d2180d96844ca9cdf7954c84e09a33eaf9646c5495b4d1af0b4c9306",
	"Test collection.",
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
          <title>Nevemores NFT</title>
          <meta name="description" content="Nevermores NFT" />
          <link rel="icon" href="/favicon.ico" />
        </Head>

        <main className={styles.main}>
          <h1 className={styles.title}>
            Nevermores
          </h1>
          <div className={styles.topcorner}>
            <button className={styles.button} onClick={connectWallet}>{connenctButtonText}</button>
          </div>
          <video controls src={"/nevermores.mp4"} style={{ width: "960px", height:"480px" }} autoPlay muted />
          <div>
            <button className={styles.button} onClick={mint} disabled={!isWalletConnected}>Mint</button>
          </div>
        </main>

      </div>
    </div>
  )
}
