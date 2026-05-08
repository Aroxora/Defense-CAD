import { Injectable, signal } from '@angular/core';
import { BrowserProvider, parseEther, formatEther } from 'ethers';
import { environment } from '../../environments/environment';

export interface PaymentResult {
  success: boolean;
  txHash?: string;
  error?: string;
}

@Injectable({
  providedIn: 'root'
})
export class CryptoPaymentService {
  readonly walletConnected = signal(false);
  readonly walletAddress = signal<string | null>(null);
  readonly balance = signal<string>('0');

  private provider: BrowserProvider | null = null;

  async connectWallet(): Promise<boolean> {
    if (typeof window === 'undefined' || !(window as any).ethereum) {
      alert('Please install MetaMask or another Web3 wallet');
      return false;
    }

    try {
      this.provider = new BrowserProvider((window as any).ethereum);
      const accounts = await this.provider.send('eth_requestAccounts', []);

      if (accounts.length > 0) {
        this.walletAddress.set(accounts[0]);
        this.walletConnected.set(true);
        await this.updateBalance();
        return true;
      }
    } catch (error: any) {
      console.error('Wallet connection failed:', error);
      alert('Failed to connect wallet: ' + error.message);
    }
    return false;
  }

  async updateBalance(): Promise<void> {
    if (!this.provider || !this.walletAddress()) return;

    try {
      const balance = await this.provider.getBalance(this.walletAddress()!);
      this.balance.set(formatEther(balance));
    } catch (error) {
      console.error('Failed to get balance:', error);
    }
  }

  async sendPayment(amountEth: string, itemId: string): Promise<PaymentResult> {
    if (!this.provider || !this.walletConnected()) {
      return { success: false, error: 'Wallet not connected' };
    }

    try {
      const signer = await this.provider.getSigner();
      const tx = await signer.sendTransaction({
        to: environment.paymentAddress,
        value: parseEther(amountEth),
        data: '0x' + Array.from(new TextEncoder().encode(`payment:${itemId}:${environment.clientEmail}`)).map(b => b.toString(16).padStart(2, '0')).join('')
      });

      await tx.wait();

      return { success: true, txHash: tx.hash };
    } catch (error: any) {
      console.error('Payment failed:', error);
      return { success: false, error: error.message || 'Transaction failed' };
    }
  }

  disconnect(): void {
    this.walletConnected.set(false);
    this.walletAddress.set(null);
    this.balance.set('0');
    this.provider = null;
  }
}
