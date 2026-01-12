from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import os
import time
import asyncio
import logging

logger = logging.getLogger("alpha_terminal_dashboard")

class GasService:
    def __init__(self):
        # Default to a public Polygon RPC if not set
        self.rpc_url = os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com")
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Polygon PoS chain requires PoA middleware
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        
        if self.w3.is_connected():
            logger.info(f"Connected to Polygon RPC: {self.rpc_url}")
        else:
            logger.warning(f"Failed to connect to Polygon RPC: {self.rpc_url}")

    def get_gas_price_gwei(self) -> float:
        """
        Fetch current gas price in Gwei.
        """
        try:
            wei_price = self.w3.eth.gas_price
            return self.w3.from_wei(wei_price, 'gwei')
        except Exception as e:
            logger.error(f"Error fetching gas price: {e}")
            return 0.0

    def is_network_congested(self, threshold_gwei: float = 100.0) -> bool:
        """
        Check if current gas price exceeds a 'congestion' threshold.
        """
        current_gwei = self.get_gas_price_gwei()
        return current_gwei > threshold_gwei

    def estimate_optimal_gas(self) -> dict:
        """
        Return a dictionary of gas estimates (standard, fast, rapid).
        For EIP-1559, this would be more complex (maxFeePerGas, maxPriorityFeePerGas).
        Simple legacy approach for now or basic EIP-1559 fetch if supported.
        """
        try:
            wei_price = self.w3.eth.gas_price
            base_gwei = float(self.w3.from_wei(wei_price, 'gwei'))
            
            return {
                "safe_low": base_gwei * 0.9,
                "standard": base_gwei,
                "fast": base_gwei * 1.1,
                "rapid": base_gwei * 1.25,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Error estimating gas: {e}")
            return {}

    async def wait_for_low_gas(self, threshold_gwei: float, timeout: int = 300, check_interval: int = 10):
        """
        Polls until gas price is below threshold or timeout is reached.
        Returns True if target reached, False on timeout.
        """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            current = self.get_gas_price_gwei()
            if current > 0 and current <= threshold_gwei:
                return True
            await asyncio.sleep(check_interval)
        
        logger.warning(f"Timeout waiting for gas < {threshold_gwei} Gwei")
        return False
