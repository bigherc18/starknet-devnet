"""Parent for predeployed contract wrapper classes"""


class PredeployedContractWrapper:
    """Parent class for all predeployed contract wrapper classes"""

    async def deploy(self):
        """Deploy the contract wrapper to devnet"""
        raise NotImplementedError()
