"""
Secure Function Component

Main entry point for the secure function computation component.
"""

from fate.arch import Context
from fate.components.core import GUEST, HOST, Role, cpn, params
from .secure_func_guest import SecureFuncGuest
from .secure_func_host import SecureFuncHost


@cpn.component(roles=[GUEST, HOST], provider="iotsp")
def secure_func(
    ctx: Context,
    role: Role,
    values: cpn.dataframe_input(roles=[GUEST], desc="Input values from guest"),
    formula: cpn.dataframe_input(
        roles=[HOST], desc="Input formula/coefficients from host"
    ),
    result: cpn.dataframe_output(roles=[GUEST], desc="Computed result"),
    he_param: cpn.parameter(
        type=params.he_param(),
        default=params.HEParam(kind="paillier", key_length=1024),
        desc="Homomorphic encryption parameters (paillier, ou, or mock)",
    ),
):
    """
    Secure Function Computation Component

    This component enables secure computation where:
    - Guest provides encrypted values
    - Host performs computation on encrypted data using a formula
    - Guest receives and decrypts the result

    Parameters
    ----------
    ctx : Context
        FATE context
    role : Role
        Current party role (GUEST or HOST)
    values : DataFrame
        Input values (from guest)
    formula : DataFrame
        Formula/coefficients (from host)
    result : DataFrame
        Output result (to guest)
    he_param : HEParam
        Homomorphic encryption parameters

    Examples
    --------
    >>> # In pipeline:
    >>> from fate_secure_func_client import SecureFunc
    >>>
    >>> secure_func_0 = SecureFunc(
    ...     "secure_func_0",
    ...     values=reader.guest.outputs["output_data"],
    ...     formula=reader.hosts[0].outputs["output_data"],
    ...     he_param={"kind": "paillier", "key_length": 1024}
    ... )
    """
    if role.is_guest:
        ctx.cipher.set_phe(ctx.device, he_param.dict())

        sfg = SecureFuncGuest(ctx)
        sfg.encrypt_and_send(values.read())
        result_data = sfg.receive_and_decrypt()

        result.write(result_data)

    elif role.is_host:
        sfh = SecureFuncHost(ctx)
        sfh.eval(formula.read())

    else:
        raise ValueError(f"Unsupported role: {role}. Must be GUEST or HOST.")
