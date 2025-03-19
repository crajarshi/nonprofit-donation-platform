from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from app.blockchain.xrpl_client import xrpl_client


async def initiate_xrp_payment(
    from_address: str,
    to_address: str,
    amount: float,
    use_escrow: bool = False,
    memo: Optional[str] = None
) -> Dict[str, Any]:
    """
    Initiate an XRP payment.
    
    Args:
        from_address: The sender's XRPL address
        to_address: The recipient's XRPL address
        amount: The amount of XRP to send
        use_escrow: Whether to use an escrow for conditional release
        memo: Optional memo to include with the transaction
    
    Returns:
        Transaction details dictionary
    """
    if use_escrow:
        # Calculate escrow finish time (30 days from now)
        release_time = datetime.utcnow() + timedelta(days=30)
        
        # Create the escrow
        result = await xrpl_client.create_escrow(
            from_wallet=from_address,
            to_address=to_address,
            amount=amount,
            release_time=release_time,
            memo=memo
        )
    else:
        # Direct payment
        result = await xrpl_client.send_xrp_payment(
            from_wallet=from_address,
            to_address=to_address,
            amount=amount,
            memo=memo
        )
    
    return result


async def check_transaction_status(tx_hash: str) -> str:
    """
    Check the status of a transaction.
    
    Args:
        tx_hash: The transaction hash to check
    
    Returns:
        Transaction status: "pending", "completed", or "failed"
    """
    return await xrpl_client.check_transaction_status(tx_hash)


async def finish_escrow(
    from_address: str,
    owner: str,
    escrow_sequence: int,
    fulfillment: Optional[str] = None
) -> Dict[str, Any]:
    """
    Finish an escrow and release the funds.
    
    Args:
        from_address: The sender's XRPL address
        owner: The address of the account that created the escrow
        escrow_sequence: The sequence number of the escrow
        fulfillment: Optional fulfillment for crypto-conditions
    
    Returns:
        Transaction details dictionary
    """
    return await xrpl_client.finish_escrow(
        from_wallet=from_address,
        owner=owner,
        escrow_sequence=escrow_sequence,
        fulfillment=fulfillment
    )


async def get_account_transactions(address: str, limit: int = 20) -> list:
    """
    Get recent transactions for an account.
    
    Args:
        address: The XRPL address to check
        limit: Maximum number of transactions to return
    
    Returns:
        List of transactions
    """
    return await xrpl_client.get_account_transactions(address, limit)


async def get_account_info(address: str) -> Dict[str, Any]:
    """
    Get information about an XRPL account.
    
    Args:
        address: The XRPL address to check
    
    Returns:
        Account information dictionary
    """
    return await xrpl_client.get_account_info(address) 