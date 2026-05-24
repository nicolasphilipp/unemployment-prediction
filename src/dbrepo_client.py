"""
DBRepo API Client for Unemployment Prediction Experiment
Loads pre-split data from existing views in DBRepo.
"""

import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))


class DBRepoClient:
    """Client for fetching data from DBRepo views."""
    
    def __init__(self):
        self.base_url = os.getenv('DBREPO_BASE_URL', 'https://test.dbrepo.tuwien.ac.at').rstrip('/')
        self.database_id = os.getenv('DBREPO_DATABASE_ID')
        self.username = os.getenv('DBREPO_USERNAME')
        self.password = os.getenv('DBREPO_PASSWORD')
        
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # View IDs from the load_views notebook
        self.view_ids = {
            'train_split': '3edb9ad6-78c1-48b7-afc6-f6c88b4a1a61',
            'validation_split': 'abba7dcd-e5ab-4f5c-9cb8-b1fc1bb7d6b5',
            'test_split': '9469de00-ad14-489b-a8f1-73e1ec21218c',
            'ml_feature_table': '2a10edf4-6645-4f6f-9bb5-83919cff02ea',
            'inner_city_districts': '5a624d3a-876e-4078-83b4-c0bbec256179',
            'outer_city_districts': '96116d38-a9c9-4dda-b608-6fe65ade65ce',
            'gender_disaggregated': 'fe047ba9-61e1-433c-9bd7-52551ca15b33'
        }
    
    def _get_view_data(self, view_id: str, page_size: int = 500) -> pd.DataFrame:
        """Fetch all rows from a view using pagination."""
        url = f"{self.base_url}/api/v1/database/{self.database_id}/view/{view_id}/data"
        frames = []
        page = 0
        
        while True:
            response = self.session.get(
                url, params={"size": page_size, "page": page}
            )
            response.raise_for_status()
            
            payload = response.json()

            # DBRepo sometimes returns list directly, sometimes dict
            if isinstance(payload, list):
                data = payload
            else:
                data = payload.get("content", payload)
            
            if not data:
                break
            
            frames.append(pd.DataFrame(data))
            
            if len(data) < page_size:
                break
            page += 1
        
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    
    def get_train_data(self) -> pd.DataFrame:
        """Load training split (2002-2015)."""
        df = self._get_view_data(self.view_ids['train_split'])
        # Convert reference_date to year for consistency with original notebook
        if 'reference_date' in df.columns and 'ref_year' not in df.columns:
            df['ref_year'] = pd.to_datetime(df['reference_date']).dt.year
        return df
    
    def get_validation_data(self) -> pd.DataFrame:
        """Load validation split (2016-2018)."""
        df = self._get_view_data(self.view_ids['validation_split'])
        if 'reference_date' in df.columns and 'ref_year' not in df.columns:
            df['ref_year'] = pd.to_datetime(df['reference_date']).dt.year
        return df
    
    def get_test_data(self) -> pd.DataFrame:
        """Load test split (2019+)."""
        df = self._get_view_data(self.view_ids['test_split'])
        if 'reference_date' in df.columns and 'ref_year' not in df.columns:
            df['ref_year'] = pd.to_datetime(df['reference_date']).dt.year
        return df
    
    def get_all_data(self) -> pd.DataFrame:
        """Load all data from ml_feature_table."""
        return self._get_view_data(self.view_ids['ml_feature_table'])


def create_client():
    return DBRepoClient()


if __name__ == "__main__":
    client = create_client()
    
    print("Testing DBRepo API Client...")
    print("-" * 40)
    
    # Test each split
    df_train = client.get_train_data()
    print(f"train_split: {len(df_train)} rows")
    
    df_val = client.get_validation_data()
    print(f"validation_split: {len(df_val)} rows")
    
    df_test = client.get_test_data()
    print(f"test_split: {len(df_test)} rows")
    
    print("-" * 40)
    print(f"Total: {len(df_train) + len(df_val) + len(df_test)} rows")
    
    if len(df_train) > 0:
        print("\nSample columns:", list(df_train.columns))