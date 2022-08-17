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
    var collection_name = "Rekt Cats"
    var name = "test"
    var description = "des"
    var supply = 1
    var uri = ""
    const payload = {
      type: "script_function_payload",
      function: "0xAECDE6ADBA10C2996AD0D8A18513404876C87C11924529A34D672195846EA3F1::candy_machine::create_token",
      type_arguments: [],
      arguments: [
          collection_name.encode("utf-8").hex(),
          name.encode("utf-8").hex(),
          description.encode("utf-8").hex(),
          str(supply),
          str(U64_MAX),
          uri.encode("utf-8").hex(),
          account.address(),
          str(0),
          str(0),
          mutate_setting,
          ["GiftTo".encode("utf-8").hex()],
          ["Bob".encode("utf-8").hex()],
          ["string".encode("utf-8").hex()]
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
