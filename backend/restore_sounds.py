#!/usr/bin/env python3
"""
Script to restore all sound files from git history.
This will download all sound files that were previously in the repository.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), -1

def get_sound_files_list():
    """Get the list of all sound files from git history."""
    cmd = "git log --all --full-history --name-only | grep -E '\\.(wav|mp3|ogg)$' | sort | uniq"
    stdout, stderr, returncode = run_command(cmd)
    
    if returncode != 0:
        print(f"Error getting sound files list: {stderr}")
        return []
    
    return [line.strip() for line in stdout.split('\n') if line.strip()]

def restore_sound_file(file_path):
    """Restore a single sound file from git history."""
    try:
        # Get the file content from git
        cmd = f"git show HEAD:{file_path}"
        stdout, stderr, returncode = run_command(cmd)
        
        if returncode != 0:
            # Try to find the file in any commit
            cmd = f"git log --all --full-history --name-only | grep '{file_path}' | head -1"
            stdout, stderr, returncode = run_command(cmd)
            
            if returncode != 0 or not stdout:
                print(f"Could not find {file_path} in git history")
                return False
            
            # Get the commit hash
            commit_hash = stdout.strip().split()[0]
            cmd = f"git show {commit_hash}:{file_path}"
            stdout, stderr, returncode = run_command(cmd)
            
            if returncode != 0:
                print(f"Could not restore {file_path} from commit {commit_hash}")
                return False
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write the file
        with open(file_path, 'wb') as f:
            f.write(stdout.encode('latin-1'))
        
        print(f"✅ Restored: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error restoring {file_path}: {e}")
        return False

def main():
    """Main function to restore all sound files."""
    print("🎵 Restoring all sound files from git history...")
    
    # Change to the Poker directory
    poker_dir = Path(__file__).parent.parent
    os.chdir(poker_dir)
    
    # Get list of sound files
    sound_files = get_sound_files_list()
    
    if not sound_files:
        print("❌ No sound files found in git history")
        return
    
    print(f"📁 Found {len(sound_files)} sound files to restore")
    
    # Restore each file
    restored_count = 0
    for sound_file in sound_files:
        if restore_sound_file(sound_file):
            restored_count += 1
    
    print(f"\n🎉 Restored {restored_count} out of {len(sound_files)} sound files")
    
    # List current sounds directory
    print("\n📂 Current sounds directory contents:")
    sounds_dir = Path("backend/sounds")
    if sounds_dir.exists():
        for file_path in sounds_dir.rglob("*"):
            if file_path.is_file():
                size = file_path.stat().st_size
                print(f"   {file_path.relative_to(sounds_dir)} ({size} bytes)")

if __name__ == "__main__":
    main()
