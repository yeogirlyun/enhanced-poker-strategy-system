#!/usr/bin/env python3
"""
Sound Trimmer

Automatically trims sound files to 1 second when replacing them.
"""

import os
import subprocess
import tempfile
from pathlib import Path

def trim_sound_file(input_path: str, output_path: str, max_duration: float = 1.0) -> bool:
    """
    Trim a sound file to maximum duration using ffmpeg.
    
    Args:
        input_path: Path to input sound file
        output_path: Path to output trimmed file
        max_duration: Maximum duration in seconds (default 1.0)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if ffmpeg is available
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️  ffmpeg not available, skipping trim")
            return False
        
        # Get file duration
        duration_cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', input_path
        ]
        
        result = subprocess.run(duration_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Could not get duration for {input_path}")
            return False
        
        try:
            duration = float(result.stdout.strip())
        except ValueError:
            print(f"❌ Invalid duration format for {input_path}")
            return False
        
        print(f"📊 File duration: {duration:.2f} seconds")
        
        # If duration is already under max, just copy the file
        if duration <= max_duration:
            print(f"✅ File is already under {max_duration}s, copying as-is")
            import shutil
            shutil.copy2(input_path, output_path)
            return True
        
        # Trim the file using ffmpeg
        print(f"✂️  Trimming to {max_duration} seconds...")
        
        trim_cmd = [
            'ffmpeg', '-i', input_path, '-t', str(max_duration),
            '-c', 'copy', output_path, '-y'
        ]
        
        result = subprocess.run(trim_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully trimmed to {max_duration}s")
            return True
        else:
            print(f"❌ Failed to trim file: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error trimming file: {e}")
        return False

def get_sound_duration(file_path: str) -> float:
    """Get the duration of a sound file in seconds."""
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', file_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return float(result.stdout.strip())
        else:
            return 0.0
    except:
        return 0.0

def main():
    """Test the sound trimmer."""
    print("✂️  SOUND TRIMMER TEST")
    print("=" * 40)
    
    # Test with a sample file
    test_file = "sounds/coin-257878.mp3"
    
    if os.path.exists(test_file):
        duration = get_sound_duration(test_file)
        print(f"📊 Test file: {test_file}")
        print(f"📊 Duration: {duration:.2f} seconds")
        
        if duration > 1.0:
            print(f"✂️  File needs trimming")
            output_file = "sounds/test_trimmed.mp3"
            success = trim_sound_file(test_file, output_file, 1.0)
            
            if success:
                new_duration = get_sound_duration(output_file)
                print(f"✅ Trimmed file duration: {new_duration:.2f} seconds")
            else:
                print(f"❌ Failed to trim file")
        else:
            print(f"✅ File is already under 1 second")
    else:
        print(f"❌ Test file not found: {test_file}")

if __name__ == "__main__":
    main() 