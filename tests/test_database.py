def test_delete_profile(db, sample_profiles):
    # First insert the profile to ensure it exists
    db.insert_profiles(sample_profiles)
    
    # Test deleting a profile
    linkedin_id = sample_profiles[0].get("linkedin_id")
    deleted_count = db.remove_profile(linkedin_id)
    
    # Verify deletion
    assert deleted_count == 1

def test_insert_profiles(db, sample_profiles):
    # Test inserting profiles
    inserted = db.insert_profiles(sample_profiles)
    assert inserted == 1
    
    # Test duplicate handling (should not insert)
    inserted = db.insert_profiles(sample_profiles)
    assert inserted == 0

def test_initialize_all_profiles_db(db):
    # Check if table exists and has correct schema
    db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='all_profiles'")
    assert db.cursor.fetchone() is not None