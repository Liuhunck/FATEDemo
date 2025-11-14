"""
Guest Party Implementation for Secure Function Component
"""

from fate.arch.dataframe.manager import BlockType
from fate.arch.dataframe import DataFrame
from fate.arch import Context
from torch import Tensor
import logging
import copy

logger = logging.getLogger(__name__)


class SecureFuncGuest:
    """
    Guest party implementation for secure function computation.

    The guest party:
    1. Initializes homomorphic encryption kit
    2. Encrypts input values
    3. Sends encrypted values to host
    4. Receives and decrypts results
    """

    values: DataFrame
    idxvalues: dict

    def __init__(self, ctx: Context):
        """
        Initialize guest component

        Parameters
        ----------
        ctx : Context
            FATE context
        """
        self.ctx = ctx
        self._init_encrypt_kit()

    def _init_encrypt_kit(self):
        """Initialize homomorphic encryption kit"""
        kit = self.ctx.cipher.phe.setup()
        self._encrypt_kit = kit
        self._en_key_length = kit.key_size
        (
            self._sk,
            self._pk,
            self._coder,
            self._evaluator,
            self._encryptor,
            self._decryptor,
        ) = (
            kit.sk,
            kit.pk,
            kit.coder,
            kit.evaluator,
            kit.get_tensor_encryptor(),
            kit.get_tensor_decryptor(),
        )
        logger.info(
            f"Encryption kit initialized with key length: {self._en_key_length}"
        )

    def encrypt_and_send(self, values: DataFrame):
        """
        Encrypt values and send to host

        Parameters
        ----------
        values : DataFrame or dict
            Input values to encrypt
        """

        self.values = values

        # Encrypt each value
        logger.info(f"Encrypting {len(values)} values...")

        values_df = values.as_pd_df()
        self.idxvalues = {vidx: idx for idx, vidx in enumerate(values_df["id"])}
        en_vals = {
            col: self._encryptor.encrypt_tensor(Tensor(values_df[col]))
            for col in values.columns
        }

        # Send encrypted values and encryption kit to host
        logger.info("Sending encrypted values and encryption kit to host...")
        self.ctx.hosts.put("en_vals", en_vals)
        self.ctx.hosts.put("en_kit", [self._pk, self._evaluator])

        logger.info("Encrypted values sent to host")

    def receive_and_decrypt(self) -> DataFrame:
        """
        Receive and decrypt result from host

        Returns
        -------
        DataFrame
            Decrypted result as DataFrame
        """
        logger.info("Receiving encrypted result from host...")
        en_result = self.ctx.hosts.get("result")[0]

        logger.info("Decrypting result from host...")
        decrypted_values = {
            idx: self._decryptor.decrypt_tensor(tensor).tolist()
            for idx, tensor in en_result.items()
        }
        logger.info("Decryption complete...")

        new_columns = list(decrypted_values.keys())
        new_dm = self.values.data_manager.duplicate()
        bids = new_dm.append_columns(
            new_columns, [BlockType.get_block_type(float)] * len(new_columns)
        )

        match_id_loc = new_dm.loc_block("id", with_offset=True)
        if isinstance(match_id_loc, tuple):
            match_id_block_id, match_id_offset = match_id_loc
        else:
            match_id_block_id = match_id_loc
            match_id_offset = 0

        idxvalues = self.idxvalues

        def append_col_by_id_separate(blocks):
            match_id_block = blocks[match_id_block_id]

            ret_blocks = [block for block in blocks]
            for bid, col in zip(bids, new_columns):
                ret_blocks.append(
                    new_dm.blocks[bid].convert_block(
                        [
                            [
                                decrypted_values[col][
                                    idxvalues[
                                        (
                                            row[match_id_offset]
                                            if isinstance(row, list)
                                            else row
                                        )
                                    ]
                                ]
                            ]
                            for row in match_id_block
                        ]
                    )
                )
            return ret_blocks

        ret = DataFrame(
            self.values._ctx,
            self.values.block_table.mapValues(append_col_by_id_separate),
            copy.deepcopy(self.values.partition_order_mappings),
            new_dm,
        )

        logger.info("Decrypted result DataFrame constructed...")

        return ret
