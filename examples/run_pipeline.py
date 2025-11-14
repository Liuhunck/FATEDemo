"""
Run Secure Function Pipeline Example

This example demonstrates how to use the secure function component
in a FATE pipeline.
"""

import argparse
import sys
import os

from fate_client.pipeline import FateFlowPipeline
from fate_client.pipeline.components.fate import Reader
from fate_client.pipeline.utils import test_utils

# Add parent directory to path to import the client component
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fate_secure_func_client import SecureFunc


def main(config="./config.yaml", namespace=""):
    """
    Run the secure function pipeline

    Parameters
    ----------
    config : str
        Path to config file
    namespace : str
        Data namespace suffix
    """
    print("=" * 60)
    print("FATE Secure Function Pipeline Example")
    print("=" * 60)

    # Load configuration
    if isinstance(config, str):
        config = test_utils.load_job_config(config)

    parties = config.parties
    guest = parties.guest[0]
    host = parties.host[0]

    print(f"\n📋 Configuration:")
    print(f"   Guest Party: {guest}")
    print(f"   Host Party:  {host}")

    # Create pipeline
    print("\n🔧 Creating pipeline...")
    pipeline = FateFlowPipeline().set_parties(guest=guest, host=host)

    # Read data
    print("📖 Setting up data readers...")
    reader_0 = Reader("reader_0")
    reader_0.guest.task_parameters(
        namespace=f"experiment{namespace}", name="guest_values"
    )
    reader_0.hosts[0].task_parameters(
        namespace=f"experiment{namespace}", name="host_formula"
    )

    # Add secure function component
    print("🔐 Adding secure function component...")
    secure_func_0 = SecureFunc(
        "secure_func_0",
        values=reader_0.guest.outputs["output_data"],
        formula=reader_0.hosts[0].outputs["output_data"],
        he_param={"kind": "paillier", "key_length": 1024},
    )

    # Build pipeline
    print("⚙️  Adding tasks to pipeline...")
    pipeline.add_tasks([reader_0, secure_func_0])

    # Compile and run
    print("\n⚙️  Compiling pipeline...")
    pipeline.compile()

    print("\n🚀 Running pipeline...")
    print("   This may take a few minutes...")
    pipeline.fit()

    # Get results
    print("\n📊 Retrieving results...")
    try:
        result = pipeline.get_task_info("secure_func_0").get_output_data()
        print(f"\n✅ Result:")
        print(result)
    except Exception as e:
        print(f"\n⚠️  Could not retrieve result: {e}")
        print("   Check FATE Flow logs for details")

    print("\n" + "=" * 60)
    print("Pipeline completed!")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run FATE Secure Function Pipeline Example"
    )
    parser.add_argument(
        "--config", type=str, default="./config.yaml", help="Path to configuration file"
    )
    parser.add_argument(
        "--namespace", type=str, default="", help="Data namespace suffix"
    )
    args = parser.parse_args()

    main(config=args.config, namespace=args.namespace)
