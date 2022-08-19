import Head from 'next/head'
import React, { useEffect, useState } from 'react';
import styles from '../styles/Home.module.css'

export default function Home() {
  const [sender, setSender] = useState(null)
  const [isWalletConnected, setIsWalletConnected] = useState(false)
  const connectWallet = async () => {
    if ("martian" in window) {
      console.log("connecting wallet")
      const response = await window.martian.connect();
      sender = response.address
      setSender(sender)
      const isConnected = await window.martian.isConnected()
      if(isConnected) {
        setIsWalletConnected(true)
      }
      console.log("wallet connected");
      return;
    }
    window.open("https://www.martianwallet.xyz/", "_blank");
  };

  const mint = async () => {
    // Generate a transaction
    var collection_name = "Test collection."
    const payload = {
      type: "script_function_payload",
      function: "0xFE1B69789117820C8CB68811E453FAB0FE0C67CE7E25EBF51DEEB7EE9083BD50::candy_machine_v2::mint_tokens",
      type_arguments: [],
      arguments: [
      	"0x16516ed571cb90ca28cf8361663ba7fab155b005b5eb6326c9a74373af5ae253",
	"Test collection.",
	"5",
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
            <button className={styles.button} onClick={connectWallet}>Connect</button>
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
