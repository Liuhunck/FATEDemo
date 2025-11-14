"""
Upload Test Data to FATE

This script uploads the test data to FATE's data storage system.
"""

import os
from fate_client.pipeline import FateFlowPipeline
from fate_client.pipeline.utils import test_utils


def upload_data(config="./config.yaml"):
    """Upload test data to FATE storage system"""

    print("=" * 60)
    print("Uploading Test Data to FATE")
    print("=" * 60)

    # Load configuration
    if isinstance(config, str):
        config = test_utils.load_job_config(config)

    # Data file paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    guest_data_path = os.path.join(base_dir, "data", "guest_values.csv")
    host_data_path = os.path.join(base_dir, "data", "host_formula.csv")

    # Check if files exist
    if not os.path.exists(guest_data_path):
        print(f"❌ Guest data file not found: {guest_data_path}")
        print("Please run: python create_test_data.py first")
        return

    if not os.path.exists(host_data_path):
        print(f"❌ Host data file not found: {host_data_path}")
        print("Please run: python create_test_data.py first")
        return

    # Create pipeline for data upload
    data_pipeline = FateFlowPipeline().set_parties(local="0")

    # Guest data metadata
    guest_meta = {
        "delimiter": ",",
        "dtype": "float64",
        "match_id_name": "id",
    }

    # Host data metadata
    host_meta = {
        "delimiter": ",",
        "dtype": "string",
        "match_id_name": "id",
    }

    # Upload Guest data
    print(f"\n📤 Uploading guest data from {guest_data_path}...")
    data_pipeline.transform_local_file_to_dataframe(
        file=guest_data_path,
        namespace="experiment",
        name="guest_values",
        meta=guest_meta,
        head=True,
        extend_sid=True,
    )
    print("   ✓ Guest data uploaded (namespace='experiment', name='guest_values')")

    # Upload Host data
    print(f"\n📤 Uploading host data from {host_data_path}...")
    data_pipeline.transform_local_file_to_dataframe(
        file=host_data_path,
        namespace="experiment",
        name="host_formula",
        meta=host_meta,
        head=True,
        extend_sid=True,
    )
    print("   ✓ Host data uploaded (namespace='experiment', name='host_formula')")

    print("\n" + "=" * 60)
    print("✅ All data uploaded successfully!")
    print("=" * 60)
    print("\n📋 Next step:")
    print("   python run_pipeline.py --config config.yaml")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("Upload Test Data to FATE")
    parser.add_argument(
        "--config", type=str, default="./config.yaml", help="Path to configuration file"
    )
    args = parser.parse_args()

    upload_data(config=args.config)
