import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union, cast

from xrpl.clients import JsonRpcClient, WebsocketClient
from xrpl.models.transactions import Payment, EscrowCreate, EscrowFinish
from xrpl.models.requests import AccountInfo, AccountTx, Tx
from xrpl.wallet import Wallet
from xrpl.utils import xrp_to_drops, drops_to_xrp
from xrpl.transaction import submit_and_wait, XRPLReliableSubmissionException
from xrpl.models.response import Response

from app.core.config import settings


class XRPLClientException(Exception):
    """Custom exception for XRPL client errors."""
    pass


class XRPLClient:
    """Client for interacting with the XRP Ledger."""
    
    def __init__(self):
        """Initialize the XRPL client based on network configuration."""
        # Set up the appropriate network URL
        if settings.XRPL_NETWORK == "testnet":
            self.network_url = "https://s.altnet.rippletest.net:51234"
            self.ws_url = "wss://s.altnet.rippletest.net:51233"
        elif settings.XRPL_NETWORK == "devnet":
            self.network_url = "https://s.devnet.rippletest.net:51234"
            self.ws_url = "wss://s.devnet.rippletest.net:51233"
        elif settings.XRPL_NETWORK == "mainnet":
            self.network_url = "https://xrplcluster.com"
            self.ws_url = "wss://xrplcluster.com"
        else:
            raise XRPLClientException(f"Unsupported XRPL network: {settings.XRPL_NETWORK}")
        
        try:
            # Create JSON-RPC client
            self.client = JsonRpcClient(self.network_url)
            
            # Set up the platform wallet if seed is available
            self.platform_wallet = None
            if settings.XRPL_SEED:
                self.platform_wallet = Wallet(seed=settings.XRPL_SEED, sequence=0)
        except Exception as e:
            raise XRPLClientException(f"Failed to initialize XRPL client: {str(e)}")
    
    async def get_account_info(self, address: str) -> Dict[str, Any]:
        """Get information about an XRPL account."""
        try:
            request = AccountInfo(account=address)
            response = await self.client.request(request)
            if not response.is_successful():
                raise XRPLClientException("Failed to get account info")
            return cast(Dict[str, Any], response.result)
        except Exception as e:
            raise XRPLClientException(f"Error getting account info: {str(e)}")
    
    async def send_xrp_payment(
        self, 
        from_wallet: Union[Wallet, str], 
        to_address: str, 
        amount: float,
        memo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an XRP payment transaction.
        
        Args:
            from_wallet: The sender's wallet or seed
            to_address: The recipient's XRPL address
            amount: The amount of XRP to send
            memo: Optional memo to include with the transaction
            
        Returns:
            Transaction result dictionary
        """
        try:
            # Convert wallet if needed
            if isinstance(from_wallet, str):
                from_wallet = Wallet(seed=from_wallet, sequence=0)
            
            # Prepare the payment transaction
            payment_tx = Payment(
                account=from_wallet.classic_address,
                destination=to_address,
                amount=xrp_to_drops(amount)
            )
            
            # Add memo if provided
            if memo:
                payment_tx.memos = [{
                    "Memo": {
                        "MemoData": memo.encode().hex()
                    }
                }]
            
            # Submit the transaction
            response = await submit_and_wait(payment_tx, from_wallet, self.client)
            
            if response.result["meta"]["TransactionResult"] == "tesSUCCESS":
                return {
                    "tx_hash": response.result["hash"],
                    "status": "complete",
                    "fee": drops_to_xrp(response.result["Fee"]),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "tx_hash": response.result["hash"],
                    "status": "failed",
                    "error": response.result["meta"]["TransactionResult"],
                    "fee": drops_to_xrp(response.result["Fee"]),
                    "timestamp": datetime.utcnow().isoformat()
                }
        except XRPLReliableSubmissionException as e:
            raise XRPLClientException(f"Transaction submission failed: {str(e)}")
        except Exception as e:
            raise XRPLClientException(f"Error sending XRP payment: {str(e)}")
    
    async def create_escrow(
        self, 
        from_wallet: Union[Wallet, str], 
        to_address: str, 
        amount: float,
        release_time: datetime,
        condition: Optional[str] = None,
        memo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an escrow payment.
        
        Args:
            from_wallet: The sender's wallet or seed
            to_address: The recipient's XRPL address
            amount: The amount of XRP to place in escrow
            release_time: When the escrow can be released
            condition: Optional crypto-condition for release
            memo: Optional memo to include with the transaction
            
        Returns:
            Transaction result dictionary
        """
        # Convert wallet if needed
        if isinstance(from_wallet, str):
            from_wallet = Wallet(seed=from_wallet, sequence=0)
        
        # Calculate finish_after in seconds since Ripple Epoch
        ripple_epoch = datetime(2000, 1, 1)
        finish_after = int((release_time - ripple_epoch).total_seconds())
        
        # Prepare the escrow create transaction
        escrow_tx = EscrowCreate(
            account=from_wallet.classic_address,
            destination=to_address,
            amount=xrp_to_drops(amount),
            finish_after=finish_after
        )
        
        # Add condition if provided
        if condition:
            escrow_tx.condition = condition
        
        # Add memo if provided
        if memo:
            escrow_tx.memos = [{"Memo": {"MemoData": memo.encode("hex")}}]
        
        # Submit the transaction
        response = await submit_and_wait(escrow_tx, from_wallet, self.client)
        
        if response.result["meta"]["TransactionResult"] == "tesSUCCESS":
            # Extract the escrow sequence ID from the metadata
            affected_nodes = response.result["meta"]["AffectedNodes"]
            escrow_node = next(
                (node for node in affected_nodes if "CreatedNode" in node 
                 and node["CreatedNode"]["LedgerEntryType"] == "Escrow"), 
                None
            )
            
            if escrow_node:
                escrow_id = escrow_node["CreatedNode"]["LedgerIndex"]
            else:
                escrow_id = None
                
            return {
                "tx_hash": response.result["hash"],
                "escrow_id": escrow_id,
                "status": "pending",
                "release_time": release_time.isoformat(),
                "fee": drops_to_xrp(response.result["Fee"]),
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            return {
                "tx_hash": response.result["hash"],
                "status": "failed",
                "error": response.result["meta"]["TransactionResult"],
                "fee": drops_to_xrp(response.result["Fee"]),
                "timestamp": datetime.utcnow().isoformat(),
            }
    
    async def finish_escrow(
        self, 
        from_wallet: Union[Wallet, str], 
        owner: str,
        escrow_sequence: int,
        fulfillment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Finish an escrow and release the funds.
        
        Args:
            from_wallet: The wallet or seed to sign the finish transaction
            owner: The address of the account that created the escrow
            escrow_sequence: The sequence number of the escrow
            fulfillment: The fulfillment for the crypto-condition if required
            
        Returns:
            Transaction result dictionary
        """
        # Convert wallet if needed
        if isinstance(from_wallet, str):
            from_wallet = Wallet(seed=from_wallet, sequence=0)
        
        # Prepare the escrow finish transaction
        finish_tx = EscrowFinish(
            account=from_wallet.classic_address,
            owner=owner,
            offer_sequence=escrow_sequence
        )
        
        # Add fulfillment if provided
        if fulfillment:
            finish_tx.fulfillment = fulfillment
        
        # Submit the transaction
        response = await submit_and_wait(finish_tx, from_wallet, self.client)
        
        return {
            "tx_hash": response.result["hash"],
            "status": "complete" if response.result["meta"]["TransactionResult"] == "tesSUCCESS" else "failed",
            "fee": drops_to_xrp(response.result["Fee"]),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def check_transaction_status(self, tx_hash: str) -> str:
        """
        Check the status of a transaction.
        
        Args:
            tx_hash: The transaction hash to check
            
        Returns:
            Transaction status: "pending", "completed", or "failed"
        """
        request = Tx(transaction=tx_hash)
        
        try:
            response = await self.client.request(request)
            if response.is_successful():
                if response.result["meta"]["TransactionResult"] == "tesSUCCESS":
                    return "completed"
                else:
                    return "failed"
            else:
                # Transaction not found or not validated yet
                return "pending"
        except Exception:
            # Transaction not found or other error
            return "pending"
    
    async def get_account_transactions(
        self, 
        address: str, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get recent transactions for an account.
        
        Args:
            address: The XRPL address to check
            limit: Maximum number of transactions to return
            
        Returns:
            List of transactions
        """
        request = AccountTx(account=address, limit=limit)
        response = await self.client.request(request)
        
        if response.is_successful():
            return response.result["transactions"]
        else:
            return []


# Singleton instance
xrpl_client = XRPLClient() 