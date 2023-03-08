"""Parent for predeployed contract wrapper classes"""
from abc import ABC, abstractmethod

from starkware.starknet.testing.starknet import Starknet
from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starknet.testing.contract import StarknetContract


class PredeployedContractWrapper(ABC):
    """Parent class for all predeployed contract wrapper classes"""

    # Cannot import it because of circular imports
    # from .starknet_wrapper import StarknetWrapper

    starknet_wrapper = NotImplemented

    @property
    def address(self) -> int:
        try:
            return self.ADDRESS
        except AttributeError:
            try:
                return self._address
            except AttributeError:
                raise NotImplementedError(
                    "Predeployed contracts should provide an address attribute or an ADDRESS class attribute"
                )

    @address.setter
    def address(self, address: int):
        self._address = address

    @property
    def class_hash_bytes(self) -> bytes:
        try:
            return self._class_hash_bytes
        except AttributeError:
            try:
                return self.HASH_BYTES
            except AttributeError:
                raise NotImplementedError(
                    "Predeployed contracts should provide a class_hash_bytes attribute or a HASH_BYTES class attribute"
                )

    @class_hash_bytes.setter
    def class_hash_bytes(self, class_hash_bytes: bytes):
        self._class_hash_bytes = class_hash_bytes

    @property
    def contract_class(self) -> ContractClass:
        try:
            return self._contract_class
        except AttributeError:
            try:
                return self.get_contract_class()
            except AttributeError:
                raise NotImplementedError(
                    "Predeployed contracts should provide a contract_class attribute or get_contract_class method"
                )

    @contract_class.setter
    def contract_class(self, contract_class):
        self._contract_class = contract_class

    async def mimic_constructor(self):
        pass

    async def deploy(self):
        """Deploy the contract wrapper to devnet"""
        starknet: Starknet = self.starknet_wrapper.starknet

        await starknet.state.state.set_contract_class(
            self.class_hash_bytes, self.contract_class
        )

        # pylint: disable=protected-access
        starknet: Starknet = self.starknet_wrapper.starknet
        starknet.state.state.cache._class_hash_writes[
            self.address
        ] = self.class_hash_bytes
        # replace with await starknet.state.state.deploy_contract
        # await starknet.state.state.deploy_contract(self.address, self.class_hash_bytes)
        # For now, it fails for fee token since the address is the same as the
        # ETH Token, see:
        # https://starkscan.co/token/0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7:
        # Requested contract address
        # 0x49d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7
        # is unavailable for deployment

        await self.mimic_constructor()

        self.contract = StarknetContract(
            state=starknet.state,
            abi=self.contract_class.abi,
            contract_address=self.address,
            deploy_call_info=None,
        )
