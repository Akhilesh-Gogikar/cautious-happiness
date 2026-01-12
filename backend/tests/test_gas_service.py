import unittest
from unittest.mock import MagicMock, patch
import asyncio
from app.services.gas_service import GasService

class TestGasService(unittest.TestCase):
    @patch('app.services.gas_service.Web3')
    def setUp(self, mock_web3):
        self.mock_w3 = MagicMock()
        mock_web3.return_value = self.mock_w3
        self.mock_w3.is_connected.return_value = True
        self.gas_service = GasService()

    def test_get_gas_price_gwei(self):
        # Mock gas price to 50 Gwei (50 * 10^9 Wei)
        self.mock_w3.eth.gas_price = 50 * 10**9
        self.mock_w3.from_wei.side_effect = lambda x, unit: x / 10**9
        
        price = self.gas_service.get_gas_price_gwei()
        self.assertEqual(price, 50.0)

    def test_is_network_congested(self):
        # Case 1: Congested
        self.mock_w3.eth.gas_price = 150 * 10**9
        self.mock_w3.from_wei.side_effect = lambda x, unit: x / 10**9
        self.assertTrue(self.gas_service.is_network_congested(threshold_gwei=100))

        # Case 2: Not Congested
        self.mock_w3.eth.gas_price = 50 * 10**9
        self.assertFalse(self.gas_service.is_network_congested(threshold_gwei=100))

    def test_estimate_optimal_gas(self):
        self.mock_w3.eth.gas_price = 100 * 10**9
        self.mock_w3.from_wei.side_effect = lambda x, unit: x / 10**9
        
        estimates = self.gas_service.estimate_optimal_gas()
        self.assertEqual(estimates['standard'], 100.0)
        self.assertEqual(estimates['fast'], 110.0)
        self.assertEqual(estimates['safe_low'], 90.0)

    @patch('app.services.gas_service.asyncio.sleep', new_callable=lambda: lambda x: None) # Skip sleep
    def test_wait_for_low_gas(self, mock_sleep):
        # Mock async wait
        async def run_test():
            # Scenario: Gas starts high, then drops
            self.gas_service.get_gas_price_gwei = MagicMock(side_effect=[150.0, 120.0, 80.0])
            result = await self.gas_service.wait_for_low_gas(threshold_gwei=100, timeout=10, check_interval=0)
            self.assertTrue(result)
        
        loop = asyncio.new_event_loop()
        loop.run_until_complete(run_test())

if __name__ == '__main__':
    unittest.main()
