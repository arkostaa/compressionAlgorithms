import zipfile
import os


def compress_to_zip(input_file_path, output_zip_path):
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(input_file_path, os.path.basename(input_file_path))
    print(f"File compressed to {output_zip_path}")


def decompress_from_zip(input_zip_path, output_dir_path):
    with zipfile.ZipFile(input_zip_path, 'r') as zipf:
        zipf.extractall(output_dir_path)
    print(f"File decompressed to {output_dir_path}")
