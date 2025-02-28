# DB CRUD operations
import sqlite3
from typing import List, Dict, Any
from src.database import shared, client
from src.export import columns_for_export
import logging

class DatabaseOps:
    """Class to handle database operations"""
    def __init__(self):
        self.db_path = shared.get_db_path()
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def insert_profiles(self, table_name: str, data_list: List[Dict]) -> int:
        """ Insert data into any specified table with conflict handling """
        if len(data_list) == 0:
            logging.warning("No values to insert")
            return 0
        # Ensure data_list contains actual dictionaries, not coroutines
        if not data_list or not isinstance(data_list[0], dict):
            # If it's a coroutine or other non-dict object, handle the error
            logging.error(f"Expected list of dictionaries for insert_profiles, got: {type(data_list[0])}")
            return 0
        
        count = 0
        for data_item in data_list:
            # Dynamic column names and placeholders
            columns = ", ".join(data_item.keys())
            placeholders = ", ".join(["?" for _ in data_item.keys()])
            values = list(data_item.values())
            
            # Construct and execute the query
            query = f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, values)
            count += 1
        
        self.conn.commit()
        return count

    def remove_profile(self, linkedin_id: str) -> int:
        self.cursor.execute('''
            DELETE FROM 
                all_profiles
            WHERE
                linkedin_id = ?
        ''', (linkedin_id,))
        self.conn.commit()
        return self.cursor.rowcount

    def get_parsed_names(self) -> List[str]:
        """Get list of discovery_inputs that have already been parsed.
        
        Returns:
            List[str]: List of lowercase discovery_input values from the database
        """
        try:
            # First check if the table exists
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='all_profiles'")
            if not self.cursor.fetchone():
                return []  # Return empty list if table doesn't exist yet
                
            self.cursor.execute('SELECT DISTINCT LOWER(discovery_input) FROM all_profiles WHERE discovery_input IS NOT NULL')
            parsed_names = [row[0] for row in self.cursor.fetchall()]
            return parsed_names
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                return []  # Table doesn't exist yet, return empty list
            print(f"Database operational error: {e}")
            return []
        except sqlite3.Error as e:
            print(f"Error getting parsed names: {e}")
            return []
        
    def tag_qualified_basic_profiles(self) -> None:
        """ Tags profiles that meet basic qualifications to be processed by NLP """

        self.cursor.execute('''
        INSERT OR IGNORE INTO
            qualified_profiles (
                linkedin_id,
                qualified_basic_info
            )
        SELECT
            linkedin_id,
            TRUE
        FROM
            all_profiles
        WHERE
            country_code = 'US' AND
            number_of_connections > 300
        ;''')
        self.conn.commit()
    
    def get_tagged_basic_profiles(self) -> List[str]:
        """ Gets linkedin_ids of profiles tagged for basic qualifications but not yet reviewed by nlp """

        self.cursor.execute('''
        SELECT
            linkedin_id
        FROM
            all_profiles
        WHERE
            linkedin_id NOT IN (SELECT linkedin_id FROM nlp_attributes) AND
            linkedin_id IN (SELECT linkedin_id FROM qualified_profiles)
        ;''')
        self.conn.commit()
        tagged_profiles = [row[0] for row in self.cursor.fetchall()]
        return tagged_profiles
    
    def tag_qualified_nlp_profiles(self) -> None:
        """ Tags profiles that meet qualifications to be manually reviewed """
        query = client.client_query() # This will need to be changed by the user
        self.cursor.execute(query)
        self.conn.commit()

    def get_tagged_qualified_nlp_profiles(self):
        """ Gets the data we want to export for manual review """
        query = columns_for_export.export_query()
        self.cursor.execute(query)
        self.conn.commit()

    def __del__(self):
        self.cursor.close()
        self.conn.close()