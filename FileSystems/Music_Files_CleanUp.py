import os
import hashlib
import shutil
import subprocess
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import magic
import stat

def is_valid_mp3(file_path):
    """
    Check if the file is a valid MP3 file.
    """
    try:
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(file_path)
        return file_type == "audio/mpeg"
    except Exception as e:
        print(f"Error determining file type for {file_path}: {e}")
        return False

def fix_corrupted_mp3(file_path, output_path=None):
    """
    Use FFmpeg to fix/re-encode corrupted MP3 files.
    If the output_path is None, the fixed file will overwrite the original.
    """
    if output_path is None:
        output_path = file_path

    try:
        print(f"Attempting to fix corrupted file: {file_path}")
        # Run FFmpeg to re-encode the file
        command = ['ffmpeg', '-i', file_path, '-c:a', 'copy', output_path]
        subprocess.run(command, check=True)
        print(f"File fixed: {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to fix file with FFmpeg: {file_path} - {e}")
    except Exception as e:
        print(f"Error while fixing file: {file_path} - {e}")

def get_music_attributes(file_path):
    """
    Get the file size, duration, and tags (name, artist, year) for a music file.
    If the file cannot be read, attempt to fix it using FFmpeg.
    """
    if not is_valid_mp3(file_path):
        print(f"Skipping non-MP3 file: {file_path}")
        return None
    
    try:
        file_size = os.path.getsize(file_path)
        audio = MP3(file_path, ID3=EasyID3)
        duration = int(audio.info.length)
        title = audio.get("title", ["Unknown"])[0]
        artist = audio.get("artist", ["Unknown"])[0]
        year = audio.get("date", ["Unknown"])[0]  # Extract year
        return file_size, duration, title, artist, year
    except Exception as e:
        print(f"Error getting attributes for {file_path}: {e}")
        # If we encounter an error, try fixing the file
        fixed_path = file_path.replace(".mp3", "_fixed.mp3")
        fix_corrupted_mp3(file_path, fixed_path)
        return None

def find_and_delete_duplicates(music_dir):
    """
    Find and delete duplicate music files based on their name, size, and attributes (title, artist, etc.).
    """
    files_hash_map = {}
    duplicates = []

    for root, _, files in os.walk(music_dir):
        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                file_hash = get_file_hash(file_path)
                attributes = get_music_attributes(file_path)
                
                if attributes:
                    file_size, duration, title, artist, year = attributes
                    file_key = (file_size, duration, title, artist)

                    if file_key in files_hash_map:
                        # Found a duplicate; delete this file
                        print(f"Deleting duplicate: {file_path}")
                        try:
                            make_writable(file_path)
                            os.remove(file_path)
                        except PermissionError as e:
                            print(f"Permission error: {e}. Could not delete {file_path}.")
                        except Exception as e:
                            print(f"Error deleting {file_path}: {e}")
                    else:
                        files_hash_map[file_key] = file_path
                        duplicates.append(file_path)

    return duplicates

def make_writable(file_path):
    """ Make the file writable (remove read-only flag) """
    try:
        os.chmod(file_path, stat.S_IWRITE)
    except Exception as e:
        print(f"Could not change permissions for {file_path}: {e}")

def get_file_hash(file_path):
    """
    Calculate the hash of the file contents for comparison.
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def restructure_music_by_year(music_dir, output_dir):
    """
    Move music files into folders structured by year.
    """
    for root, _, files in os.walk(music_dir):
        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                attributes = get_music_attributes(file_path)
                
                if attributes:
                    _, _, title, artist, year = attributes
                    if year != "Unknown" and len(str(year)) == 4:
                        year_folder = os.path.join(output_dir, str(year))
                    else:
                        year_folder = os.path.join(output_dir, "Unknown Year")

                    os.makedirs(year_folder, exist_ok=True)
                    
                    try:
                        print(f"Moving {file_path} to {year_folder}")
                        shutil.move(file_path, os.path.join(year_folder, file))
                    except Exception as e:
                        print(f"Error moving {file_path}: {e}")

def remove_empty_folders(directory):
    """
    Recursively remove empty folders from the given directory.
    """
    for foldername, subfolders, files in os.walk(directory, topdown=False):
        if not subfolders and not files:
            try:
                print(f"Removing empty folder: {foldername}")
                os.rmdir(foldername)
            except OSError as e:
                print(f"Error removing folder {foldername}: {e}")

if __name__ == "__main__":
    music_directory = input("Enter the path to your music directory: ")
    output_directory = input("Enter the path to the output directory (where music will be restructured): ")

    print("Finding and deleting duplicates...")
    find_and_delete_duplicates(music_directory)

    print("Restructuring music files by year...")
    restructure_music_by_year(music_directory, output_directory)

    dir_to_clean = input("Enter the path to the directory to clean up empty folders: ")
    remove_empty_folders(dir_to_clean)

    print("Process completed.")
