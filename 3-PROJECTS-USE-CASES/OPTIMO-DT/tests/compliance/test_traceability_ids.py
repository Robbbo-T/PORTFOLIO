"""
Test traceability ID format compliance.
Asserts DT:{SEG}:{LLC}:{DATE}:{SEQ} format.
"""
import re


def test_traceability_id_format():
    """Test that traceability IDs follow the required format."""
    # Example traceability IDs
    valid_ids = [
        "DT:AIR:AAA-STRUCTURES-AERO:20241210:001",
        "DT:SPACE:OOO-OS-NAVIGATION:20241210:002", 
        "DT:GROUND:IIF-INFRASTRUCTURE:20241210:003",
        "DT:DEFENSE:DDD-SAFETY-CYBER:20241210:004",
        "DT:CROSS:LCC-CONTROLS-COMMS:20241210:005"
    ]
    
    # Pattern: DT:{segment}:{llc}:{date}:{seq}
    pattern = r'^DT:(AIR|SPACE|GROUND|DEFENSE|CROSS):[A-Z]{3}-[A-Z-]+:\d{8}:\d{3}$'
    
    for trace_id in valid_ids:
        assert re.match(pattern, trace_id), f"Invalid traceability ID format: {trace_id}"


def test_invalid_traceability_ids():
    """Test that invalid traceability IDs are rejected."""
    invalid_ids = [
        "DT:INVALID:AAA-STRUCTURES-AERO:20241210:001",  # Invalid segment
        "DT:AIR:invalid-llc:20241210:001",  # Invalid LLC format
        "DT:AIR:AAA-STRUCTURES-AERO:20241210:1",  # Invalid sequence format
        "INVALID:AIR:AAA-STRUCTURES-AERO:20241210:001",  # Invalid prefix
    ]
    
    pattern = r'^DT:(AIR|SPACE|GROUND|DEFENSE|CROSS):[A-Z]{3}-[A-Z-]+:\d{8}:\d{3}$'
    
    for trace_id in invalid_ids:
        assert not re.match(pattern, trace_id), f"Should reject invalid traceability ID: {trace_id}"


if __name__ == "__main__":
    test_traceability_id_format()
    test_invalid_traceability_ids()
    print("All traceability ID tests passed!")