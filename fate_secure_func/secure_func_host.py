"""
Host Party Implementation for Secure Function Component
"""

from fate.arch.dataframe import DataFrame

import logging

logger = logging.getLogger(__name__)


class SecureFuncHost:
    """
    Host party implementation for secure function computation.

    The host party:
    1. Receives encryption kit from guest
    2. Receives encrypted values from guest
    3. Performs computation on encrypted data
    4. Sends encrypted result back to guest
    """

    def __init__(self, ctx):
        """
        Initialize host component

        Parameters
        ----------
        ctx : Context
            FATE context
        """
        self.ctx = ctx
        self._init_encrypt_kit()

    def _init_encrypt_kit(self):
        """Receive encryption kit from guest"""
        self.pk, self.evaluator = self.ctx.guest.get("en_kit")
        logger.info("Received encryption kit from guest")

    def eval(self, formula: DataFrame):
        """
        Evaluate formula on encrypted data

        Parameters
        ----------
        formula : DataFrame
            Formula to evaluate (e.g., "x+y", "2*x+3*y")
        """
        logger.info(f"Evaluating formula shape of: {formula.shape}")

        # Receive encrypted values from guest (dict of PHETensor)
        en_vals = self.ctx.guest.get("en_vals")

        # Perform computation based on formula
        xAy = en_vals["x"] + en_vals["y"]
        xSy = en_vals["x"] - en_vals["y"]

        result = {}

        for row in formula.as_pd_df().to_dict(orient="records"):
            idx = row["id"]
            f = row["formula"]
            logger.info(f"Processing formula: {f}")

            if f == "x+y":
                result[idx] = xAy
            elif f == "x-y":
                result[idx] = xSy
            else:
                logger.warning(f"Unknown formula '{f}', using default (sum all values)")
                result[idx] = xAy

        # Send encrypted result back to guest
        self.ctx.guest.put("result", result)
        logger.info(f"Encrypted result sent to guest (count: {len(result)})")
