#!/usr/bin/env python3
"""
Simple Sound Trimmer

Trims sound files to 1 second using Python libraries.
"""

import os
import shutil
import wave
import struct
import math

def get_wav_duration(file_path: str) -> float:
    """Get duration of WAV file in seconds."""
    try:
        with wave.open(file_path, 'rb') as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            duration = frames / float(rate)
            return duration
    except:
        return 0.0

def trim_wav_file(input_path: str, output_path: str, max_duration: float = 1.0) -> bool:
    """
    Trim a WAV file to maximum duration.
    
    Args:
        input_path: Path to input WAV file
        output_path: Path to output trimmed file
        max_duration: Maximum duration in seconds (default 1.0)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        with wave.open(input_path, 'rb') as wav_in:
            # Get file properties
            frames = wav_in.getnframes()
            rate = wav_in.getframerate()
            channels = wav_in.getnchannels()
            sample_width = wav_in.getsampwidth()
            
            # Calculate duration
            duration = frames / float(rate)
            print(f"📊 File duration: {duration:.2f} seconds")
            
            # If duration is already under max, just copy the file
            if duration <= max_duration:
                print(f"✅ File is already under {max_duration}s, copying as-is")
                shutil.copy2(input_path, output_path)
                return True
            
            # Calculate frames to keep
            frames_to_keep = int(max_duration * rate)
            print(f"✂️  Trimming to {max_duration} seconds ({frames_to_keep} frames)...")
            
            # Read frames
            frames_data = wav_in.readframes(frames_to_keep)
            
            # Write trimmed file
            with wave.open(output_path, 'wb') as wav_out:
                wav_out.setnchannels(channels)
                wav_out.setsampwidth(sample_width)
                wav_out.setframerate(rate)
                wav_out.writeframes(frames_data)
            
            print(f"✅ Successfully trimmed to {max_duration}s")
            return True
            
    except Exception as e:
        print(f"❌ Error trimming WAV file: {e}")
        return False

def trim_any_audio_file(input_path: str, output_path: str, max_duration: float = 1.0) -> bool:
    """
    Trim any audio file to maximum duration.
    For non-WAV files, just copy them and warn the user.
    """
    file_ext = os.path.splitext(input_path)[1].lower()
    
    if file_ext == '.wav':
        return trim_wav_file(input_path, output_path, max_duration)
    else:
        # For non-WAV files, just copy and warn
        print(f"⚠️  Non-WAV file detected: {file_ext}")
        print(f"⚠️  Cannot trim {file_ext} files without ffmpeg")
        print(f"⚠️  Copying file as-is (may be longer than {max_duration}s)")
        shutil.copy2(input_path, output_path)
        return True

def main():
    """Test the simple sound trimmer."""
    print("✂️  SIMPLE SOUND TRIMMER TEST")
    print("=" * 40)
    
    # Test with a sample file
    test_file = "sounds/card_deal.wav"
    
    if os.path.exists(test_file):
        duration = get_wav_duration(test_file)
        print(f"📊 Test file: {test_file}")
        print(f"📊 Duration: {duration:.2f} seconds")
        
        if duration > 1.0:
            print(f"✂️  File needs trimming")
            output_file = "sounds/test_trimmed.wav"
            success = trim_wav_file(test_file, output_file, 1.0)
            
            if success:
                new_duration = get_wav_duration(output_file)
                print(f"✅ Trimmed file duration: {new_duration:.2f} seconds")
            else:
                print(f"❌ Failed to trim file")
        else:
            print(f"✅ File is already under 1 second")
    else:
        print(f"❌ Test file not found: {test_file}")
        print(f"📁 Available WAV files:")
        for filename in os.listdir("sounds"):
            if filename.endswith(".wav"):
                file_path = os.path.join("sounds", filename)
                duration = get_wav_duration(file_path)
                print(f"  • {filename}: {duration:.2f}s")

if __name__ == "__main__":
    main() 