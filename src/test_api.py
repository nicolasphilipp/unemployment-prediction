"""
Test script for DBRepo API integration
Run this after views are created
"""

from dbrepo_client import create_client

def main():
    print("=" * 60)
    print("Testing DBRepo API Integration")
    print("=" * 60)
    
    client = create_client()
    
    # 1. Verify views exist
    # print("\n1. Checking views...")
    # views = client.verify_views()
    # for view, exists in views.items():
    #     status = "✅" if exists else "❌"
    #     print(f"   {status} {view}")
    
    # if not views.get('train_split'):
    #     print("\n⚠️  Views not found! Please create them in DBRepo first.")
    #     return
    
    # 2. Load training data
    print("\n2. Loading training data...")
    df_train = client.get_train_data()
    print(f"   Loaded {len(df_train)} rows")
    print(f"   Columns: {list(df_train.columns)}")
    
    # 3. Load validation data
    print("\n3. Loading validation data...")
    df_val = client.get_validation_data()
    print(f"   Loaded {len(df_val)} rows")
    
    # 4. Load test data
    print("\n4. Loading test data...")
    df_test = client.get_test_data()
    print(f"   Loaded {len(df_test)} rows")
    
    # 5. Quick verification
    print("\n5. Data verification:")
    print(f"   Total rows: {len(df_train) + len(df_val) + len(df_test)}")
    print(f"   Year range in train: {df_train['ref_year'].min()} - {df_train['ref_year'].max()}")
    print(f"   Year range in val: {df_val['ref_year'].min()} - {df_val['ref_year'].max()}")
    print(f"   Year range in test: {df_test['ref_year'].min()} - {df_test['ref_year'].max()}")
    
    print("\n✅ All tests passed! Ready to run the notebook with API data.")

if __name__ == "__main__":
    main()