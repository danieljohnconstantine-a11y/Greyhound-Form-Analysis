"""
Test suite for dog detail parser - validates proper extraction and error handling
"""
from src.parser import parse_race_form, _find_block, _extract_fields, _extract_recent_runs


# Sample text with two dogs in section 2
SAMPLE_MULTI_DOG = """
Race No 1 Oct 25 05:57PM RICHMOND 320m
1. Go Forward Tiger 1d 0.0kg 1 Adam Campton 0 - 2 - 2 $630 3 7 Mdn
2. Luna Rupee 1b 0.0kg 2 Guiseppe Denardo 0 - 0 - 0 $0 FU 0 Mdn
3. Hooked On Gin 2d 0.0kg 3 Troy Vella 0 - 0 - 5 $75 6 16 Mdn

GO FORWARD TIGER
j50s j350s t50s t350s
1. 0kg (1) bdl 1 D ADAM CAMPTON Horse: 0-2-2 0%-100%
FERAL FRANKY (AUS) - GO FORWARD BARBS (AUS)
Owner: Adam Campton
CarPM/s 12mPM/s API RTC/km RDistTC DLS DLW DOD
$315 $315 0.3 3/0.644 2 7 0 -4.3

LUNA RUPEE
j50s j350s t50s t350s
2. 0kg (2) bl 1 B GUISEPPE DENARDO Horse: First Ride
ASTON RUPEE (AUS) - LITTLE MISS KADE (AUS)
Owner: Valerie Denardo
CarPM/s 12mPM/s API RTC/km RDistTC DLS DLW DOD
$0 $0 0.0 FU/0 0 0 0 FU

HOOKED ON GIN
j50s j350s t50s t350s
3. 0kg (3) blu 2 D TROY VELLA Horse: 0-0-5 0%-0%
HOOKED ON SCOTCH (AUS) - BORN FOR THIS (AUS)
Owner: Anthony Saab
CarPM/s 12mPM/s API RTC/km RDistTC DLS DLW DOD
$15 $15 0.0 6/1.608 5 16 0 -4.3
"""


def test_dog_separation():
    """Test that each dog gets its own unique data, not shared data"""
    df = parse_race_form(SAMPLE_MULTI_DOG)
    
    # Should have 3 dogs
    assert len(df) == 3
    
    # Each dog should have different owner
    owners = df['Owner'].dropna().unique()
    assert len(owners) > 1, "All dogs have the same owner - block separation failed!"
    
    # Check specific owners
    tiger = df[df['DogName'] == 'GO FORWARD TIGER']
    luna = df[df['DogName'] == 'LUNA RUPEE']
    gin = df[df['DogName'] == 'HOOKED ON GIN']
    
    if len(tiger) > 0 and 'Owner' in tiger.columns:
        assert 'Adam Campton' in str(tiger.iloc[0]['Owner'])
    
    if len(luna) > 0 and 'Owner' in luna.columns:
        assert 'Valerie Denardo' in str(luna.iloc[0]['Owner'])
    
    if len(gin) > 0 and 'Owner' in gin.columns:
        assert 'Anthony Saab' in str(gin.iloc[0]['Owner'])


def test_missing_fields():
    """Test handling of missing fields without crashes"""
    incomplete_text = """
Race No 1 Oct 25 05:57PM RICHMOND 320m
1. Test Dog 1d 0.0kg 1 John Trainer 0 - 2 - 2 $630 3 7 Mdn

TEST DOG
1. 0kg (1) bdl 1 D JOHN TRAINER Horse: 0-2-2 0%-100%
"""
    
    # Should not crash
    df = parse_race_form(incomplete_text)
    assert len(df) >= 1
    assert df.iloc[0]['DogName'] == 'TEST DOG'


def test_malformed_race_results():
    """Test handling of malformed race result lines"""
    text_with_bad_results = """
Race No 1 Oct 25 05:57PM RICHMOND 320m
1. Test Dog 1d 0.0kg 1 John Trainer 0 - 2 - 2 $630 3 7 Mdn

TEST DOG
1. 0kg (1) bdl 1 D JOHN TRAINER Horse: 0-2-2 0%-100%
Owner: Test Owner

This is a malformed line that should be ignored
2nd of 8 12/10/2025 RICHMOND Margin 1.5 Lengths Distance 320m
Another bad line without proper structure
"""
    
    # Should not crash
    df = parse_race_form(text_with_bad_results)
    assert len(df) >= 1


def test_extra_whitespace():
    """Test handling of extra whitespace and irregular formatting"""
    text_with_spaces = """
Race No 1 Oct 25 05:57PM RICHMOND 320m
1.    Test Dog      1d    0.0kg    1    John Trainer    0 - 2 - 2    $630    3    7    Mdn

TEST DOG
1.   0kg   (1)   bdl   1   D   JOHN TRAINER   Horse:   0-2-2   0%-100%
Owner:    Test Owner   
"""
    
    # Should not crash and should normalize
    df = parse_race_form(text_with_spaces)
    assert len(df) >= 1
    if 'Owner' in df.columns and df.iloc[0]['Owner'] is not None:
        assert 'Test Owner' in str(df.iloc[0]['Owner'])


def test_extract_fields_with_partial_data():
    """Test _extract_fields with only some fields present"""
    block = """
0kg (1) bdl 1 D
SIRE NAME - DAM NAME
Owner: Test Owner
API 0.5
"""
    
    fields = _extract_fields(block)
    assert fields['Owner'] is not None
    assert 'Test Owner' in fields['Owner']
    assert fields['API'] == '0.5'
    assert fields['Sire'] is not None
    assert fields['Dam'] is not None


def test_extract_recent_runs_with_missing_fields():
    """Test recent runs extraction tolerates missing fields"""
    block = """
2nd of 8 12/10/2025 RICHMOND Margin 1.5 Lengths Distance 320m Prize $1,790
3rd of 6 10/10/2025 RICHMOND Distance 320m
"""
    
    runs = _extract_recent_runs(block)
    # Should extract at least one run, even if incomplete
    assert len(runs) >= 1


if __name__ == "__main__":
    # Run tests manually
    print("Running manual tests...")
    
    try:
        test_dog_separation()
        print("✅ test_dog_separation passed")
    except AssertionError as e:
        print(f"❌ test_dog_separation failed: {e}")
    
    try:
        test_missing_fields()
        print("✅ test_missing_fields passed")
    except Exception as e:
        print(f"❌ test_missing_fields failed: {e}")
    
    try:
        test_malformed_race_results()
        print("✅ test_malformed_race_results passed")
    except Exception as e:
        print(f"❌ test_malformed_race_results failed: {e}")
    
    try:
        test_extra_whitespace()
        print("✅ test_extra_whitespace passed")
    except Exception as e:
        print(f"❌ test_extra_whitespace failed: {e}")
    
    try:
        test_extract_fields_with_partial_data()
        print("✅ test_extract_fields_with_partial_data passed")
    except Exception as e:
        print(f"❌ test_extract_fields_with_partial_data failed: {e}")
    
    try:
        test_extract_recent_runs_with_missing_fields()
        print("✅ test_extract_recent_runs_with_missing_fields passed")
    except Exception as e:
        print(f"❌ test_extract_recent_runs_with_missing_fields failed: {e}")
