import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from app.blockchain.xrpl_client import XRPLClient
from xrpl.wallet import Wallet # type: ignore


class TestXRPLClient:
    """Tests for the XRPL client integration."""
    
    @pytest.fixture
    def client(self):
        """Create a test XRPL client."""
        client = XRPLClient()
        # Override the network_url for testing
        client.network_url = "https://s.altnet.rippletest.net:51234"
        return client
    
    @pytest.fixture
    def mock_wallet(self):
        """Create a mock wallet for testing."""
        wallet = MagicMock(spec=Wallet)
        wallet.classic_address = "rTest1234567890Address"
        wallet.seed = "sTest1234567890Seed"
        return wallet
    
    @patch("app.blockchain.xrpl_client.submit_and_wait")
    @pytest.mark.asyncio
    async def test_send_xrp_payment(self, mock_submit, client, mock_wallet):
        """Test sending an XRP payment."""
        # Mock response
        mock_response = MagicMock()
        mock_response.result = {
            "hash": "0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF",
            "meta": {"TransactionResult": "tesSUCCESS"},
            "Fee": "12"
        }
        mock_submit.return_value = mock_response
        
        # Test parameters
        to_address = "rRecipient1234567890Address"
        amount = 100.0
        memo = "Test payment"
        
        # Call the method
        result = await client.send_xrp_payment(mock_wallet, to_address, amount, memo)
        
        # Check the result
        assert result["tx_hash"] == mock_response.result["hash"]
        assert result["status"] == "complete"
        assert "fee" in result
        assert "timestamp" in result
        
        # Check that the mock was called correctly
        mock_submit.assert_called_once()
        args, kwargs = mock_submit.call_args
        assert args[1] == mock_wallet  # Check wallet
        assert kwargs["client"] == client.client  # Check client
        
        # Test with a failed transaction
        mock_response.result["meta"]["TransactionResult"] = "tecPATH_DRY"
        result = await client.send_xrp_payment(mock_wallet, to_address, amount, memo)
        assert result["status"] == "failed"
    
    @patch("app.blockchain.xrpl_client.submit_and_wait")
    @pytest.mark.asyncio
    async def test_create_escrow(self, mock_submit, client, mock_wallet):
        """Test creating an escrow payment."""
        # Mock response for success
        mock_response_success = MagicMock()
        mock_response_success.result = {
            "hash": "0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF",
            "meta": {
                "TransactionResult": "tesSUCCESS",
                "AffectedNodes": [
                    {
                        "CreatedNode": {
                            "LedgerEntryType": "Escrow",
                            "LedgerIndex": "ESCROW123456789"
                        }
                    }
                ]
            },
            "Fee": "12"
        }
        mock_submit.return_value = mock_response_success
        
        # Test parameters
        to_address = "rRecipient1234567890Address"
        amount = 100.0
        release_time = datetime.utcnow() + timedelta(days=30)
        
        # Call the method
        result = await client.create_escrow(mock_wallet, to_address, amount, release_time)
        
        # Check the result
        assert result["tx_hash"] == mock_response_success.result["hash"]
        assert result["status"] == "pending"
        assert result["escrow_id"] == "ESCROW123456789"
        assert "release_time" in result
        assert "fee" in result
        assert "timestamp" in result
        
        # Test with a failed escrow creation
        mock_response_fail = MagicMock()
        mock_response_fail.result = {
            "hash": "FAIL0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789AB",
            "meta": {"TransactionResult": "tecINSUFFICIENT_RESERVE"},
            "Fee": "12"
        }
        mock_submit.return_value = mock_response_fail
        
        result = await client.create_escrow(mock_wallet, to_address, amount, release_time)
        assert result["status"] == "failed"
        assert "error" in result
    
    @patch("app.blockchain.xrpl_client.submit_and_wait")
    @pytest.mark.asyncio
    async def test_finish_escrow(self, mock_submit, client, mock_wallet):
        """Test finishing an escrow."""
        # Mock response
        mock_response = MagicMock()
        mock_response.result = {
            "hash": "0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF",
            "meta": {"TransactionResult": "tesSUCCESS"},
            "Fee": "12"
        }
        mock_submit.return_value = mock_response
        
        # Test parameters
        owner = "rOwner1234567890Address"
        escrow_sequence = 12345
        
        # Call the method
        result = await client.finish_escrow(mock_wallet, owner, escrow_sequence)
        
        # Check the result
        assert result["tx_hash"] == mock_response.result["hash"]
        assert result["status"] == "complete"
        assert "fee" in result
        assert "timestamp" in result
        
        # Check that the mock was called correctly
        mock_submit.assert_called_once()
        
        # Test with fulfillment
        fulfillment = "A0B1C2D3E4F5"
        result = await client.finish_escrow(mock_wallet, owner, escrow_sequence, fulfillment)
        assert result["status"] == "complete"
    
    @patch("app.blockchain.xrpl_client.JsonRpcClient.request")
    @pytest.mark.asyncio
    async def test_check_transaction_status(self, mock_request, client):
        """Test checking a transaction status."""
        # Mock response for completed transaction
        mock_response_complete = MagicMock()
        mock_response_complete.is_successful.return_value = True
        mock_response_complete.result = {
            "meta": {"TransactionResult": "tesSUCCESS"}
        }
        mock_request.return_value = mock_response_complete
        
        # Test parameters
        tx_hash = "0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF"
        
        # Call the method
        status = await client.check_transaction_status(tx_hash)
        
        # Check the result
        assert status == "completed"
        
        # Test with a failed transaction
        mock_response_fail = MagicMock()
        mock_response_fail.is_successful.return_value = True
        mock_response_fail.result = {
            "meta": {"TransactionResult": "tecPATH_DRY"}
        }
        mock_request.return_value = mock_response_fail
        
        status = await client.check_transaction_status(tx_hash)
        assert status == "failed"
        
        # Test with a pending transaction
        mock_response_pending = MagicMock()
        mock_response_pending.is_successful.return_value = False
        mock_request.return_value = mock_response_pending
        
        status = await client.check_transaction_status(tx_hash)
        assert status == "pending"
        
        # Test with an exception
        mock_request.side_effect = Exception("Test exception")
        
        status = await client.check_transaction_status(tx_hash)
        assert status == "pending"
    
    @patch("app.blockchain.xrpl_client.JsonRpcClient.request")
    @pytest.mark.asyncio
    async def test_get_account_transactions(self, mock_request, client):
        """Test getting account transactions."""
        # Mock response
        mock_response = MagicMock()
        mock_response.is_successful.return_value = True
        mock_response.result = {
            "transactions": [
                {"tx_hash": "HASH1", "amount": "100000000"},
                {"tx_hash": "HASH2", "amount": "200000000"}
            ]
        }
        mock_request.return_value = mock_response
        
        # Test parameters
        address = "rTest1234567890Address"
        
        # Call the method
        transactions = await client.get_account_transactions(address)
        
        # Check the result
        assert len(transactions) == 2
        assert transactions[0]["tx_hash"] == "HASH1"
        
        # Test with failed request
        mock_response.is_successful.return_value = False
        transactions = await client.get_account_transactions(address)
        assert transactions == [] 