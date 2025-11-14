"""
Client-side wrapper for SecureFunc component
"""

import os
from fate_client.pipeline.components.component_base import Component
from fate_client.pipeline.conf.types import PlaceHolder


class SecureFunc(Component):
    """
    Secure Function Client Component

    Client-side wrapper for the secure function computation component.

    Parameters
    ----------
    _name : str
        Component instance name
    runtime_parties : dict, optional
        Runtime party configuration
    values : object
        Input values (from guest)
    formula : object
        Formula/coefficients (from host)
    he_param : dict
        Homomorphic encryption parameters

    Examples
    --------
    >>> from fate_client.pipeline import FateFlowPipeline
    >>> from fate_client.pipeline.components.fate import Reader
    >>> from fate_secure_func_client import SecureFunc
    >>>
    >>> pipeline = FateFlowPipeline().set_parties(guest=9999, host=10000)
    >>> reader_0 = Reader("reader_0")
    >>>
    >>> secure_func_0 = SecureFunc(
    ...     "secure_func_0",
    ...     values=reader_0.guest.outputs["output_data"],
    ...     formula=reader_0.hosts[0].outputs["output_data"],
    ...     he_param={"kind": "paillier", "key_length": 1024}
    ... )
    """

    yaml_define_path = os.path.join(
        os.path.dirname(__file__), "component_define", "secure_func.yaml"
    )

    def __init__(
        self,
        _name: str,
        runtime_parties: dict = None,
        values: object = PlaceHolder(),
        formula: object = PlaceHolder(),
        he_param: dict = PlaceHolder(),
    ):
        inputs = locals()
        self._process_init_inputs(inputs)
        super().__init__()
        self._name = _name
        self.runtime_parties = runtime_parties
        self.values = values
        self.formula = formula
        self.he_param = he_param
