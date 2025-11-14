"""
FATE Secure Function Component

A secure computation component for FATE that enables encrypted
function evaluation using homomorphic encryption.
"""

from .__version__ import __version__
from .secure_func import secure_func

__all__ = ["secure_func", "__version__"]
