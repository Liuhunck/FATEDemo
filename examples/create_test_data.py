"""
Create Test Data for Secure Function Component

This script creates sample CSV files for testing the secure function component.
"""

import os
import pandas as pd


def create_test_data():
    """Create test data files for guest and host"""

    # Create data directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    print("=" * 60)
    print("Creating Test Data for Secure Function Component")
    print("=" * 60)

    # Guest data (values)
    guest_data = pd.DataFrame(
        {
            "id": ["id_0", "id_1", "id_2", "id_3", "id_4", "id_5", "id_6", "id_7"],
            "x": [3, 5, 7, 1, 4, 6, 8, 2],
            "y": [5, 8, 2, 4, 7, 3, 9, 6],
        }
    )
    guest_path = os.path.join(data_dir, "guest_values.csv")
    guest_data.to_csv(guest_path, index=False)
    print(f"\n✓ Created guest data: {guest_path}")
    print("\nGuest Data (values):")
    print(guest_data)

    # Host data (formula)
    host_data = pd.DataFrame(
        {
            "id": ["formula_0", "formula_1", "formula_2", "formula_3"],
            "formula": ["x+y", "x-y", "x+y", "x-y"],
        }
    )
    host_path = os.path.join(data_dir, "host_formula.csv")
    host_data.to_csv(host_path, index=False)
    print(f"\n✓ Created host data: {host_path}")
    print("\nHost Data (formula):")
    print(host_data)

    print(f"\n" + "=" * 60)
    print(f"✓ Test data created in {data_dir}/")
    print("=" * 60)
    print("\n📋 Next steps:")
    print("   1. python upload_data.py --config config.yaml")
    print("   2. python run_pipeline.py --config config.yaml")


if __name__ == "__main__":
    create_test_data()
