import os

def create_dummy_file(file_path, size_in_mb):
    """Creates a dummy file of a specific size in MB with a PDF header."""
    size_in_bytes = int(size_in_mb * 1024 * 1024)
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "wb") as f:
        # Write a basic PDF header to satisfy simple format checks
        header = b"%PDF-1.4\n%TEST_DATA\n"
        f.write(header)
        
        # Fill the rest with repeated content (more robust than null bytes)
        footer = b"\n%%EOF"
        remaining = size_in_bytes - len(header) - len(footer)
        if remaining > 0:
            # Writing in chunks of 1MB to avoid memory issues
            chunk = b"A" * (1024 * 1024)
            for _ in range(remaining // len(chunk)):
                f.write(chunk)
            f.write(b"A" * (remaining % len(chunk)))
            
        f.write(footer)
    
    print(f"Created {file_path} ({size_in_mb} MB)")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.abspath(os.path.join(base_dir, "..", "data", "test_files"))
    
    files_to_create = [
        ("small_file.pdf", 1),
        ("boundary_file.pdf", 19.5), # Slightly under 20MB to ensure success if 20 is exact rejection
        ("oversized_file.pdf", 21),
        ("dummy_file.pdf", 0.01)
    ]
    
    for filename, size in files_to_create:
        path = os.path.join(target_dir, filename)
        create_dummy_file(path, size)
