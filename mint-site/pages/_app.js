import "bootstrap/dist/css/bootstrap.min.css";
import "react-toastify/dist/ReactToastify.css";
import '../styles/globals.css'

import {
  WalletProvider,
  HippoWalletAdapter,
  AptosWalletAdapter,
  HippoExtensionWalletAdapter,
  MartianWalletAdapter,
  FewchaWalletAdapter,
  PontemWalletAdapter,
  SpikaWalletAdapter,
  RiseWalletAdapter,
  FletchWalletAdapter
} from '@manahippo/aptos-wallet-adapter';
import { ToastContainer } from 'react-toastify';

function MyApp({ Component, pageProps }) {
  const wallets = [
    new RiseWalletAdapter(),
    // new HippoWalletAdapter(),
    new MartianWalletAdapter(),
    new AptosWalletAdapter(),
    new FewchaWalletAdapter(),
    // new HippoExtensionWalletAdapter(),
    new PontemWalletAdapter(),
    new SpikaWalletAdapter(),
    new FletchWalletAdapter()
  ];

  return <WalletProvider
      wallets={wallets}
      autoConnect={false} /** allow auto wallet connection or not **/
      onError={(error) => {
        console.log('Handle Error Message', error);
      }}>
        <Component {...pageProps} />
        <ToastContainer />
    </WalletProvider>
}

export default MyApp
