#!/bin/bash
# decrypt-repo.sh - Decrypt AES-256 encrypted repository archive
# Usage: ./decrypt-repo.sh <encrypted_file> <key_file> [output_dir]

set -e

if [ $# -lt 2 ]; then
    echo "Usage: $0 <encrypted_file.zip.enc> <key_file.key> [output_dir]"
    echo ""
    echo "Example:"
    echo "  $0 PLA-Defense-CAD_20240125.zip.enc PLA-Defense-CAD_20240125.key"
    echo "  $0 PLA-Defense-CAD_20240125.zip.enc PLA-Defense-CAD_20240125.key ./decrypted"
    exit 1
fi

ENCRYPTED_FILE="$1"
KEY_FILE="$2"
OUTPUT_DIR="${3:-./decrypted_$(date +%Y%m%d_%H%M%S)}"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  PLA-Defense-CAD Decryption Script                         ║"
echo "║  AES-256-CBC Decryption                                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Validate files exist
if [ ! -f "$ENCRYPTED_FILE" ]; then
    echo "Error: Encrypted file not found: $ENCRYPTED_FILE"
    exit 1
fi

if [ ! -f "$KEY_FILE" ]; then
    echo "Error: Key file not found: $KEY_FILE"
    exit 1
fi

echo "[1/4] Reading encryption key..."

# Extract KEY and IV from key file
KEY=$(grep "^KEY=" "$KEY_FILE" | cut -d'=' -f2)
IV=$(grep "^IV=" "$KEY_FILE" | cut -d'=' -f2)

if [ -z "$KEY" ] || [ -z "$IV" ]; then
    echo "Error: Could not extract KEY or IV from key file"
    echo "Key file should contain:"
    echo "  KEY=<hex_key>"
    echo "  IV=<hex_iv>"
    exit 1
fi

echo "   Key loaded successfully"

echo "[2/4] Decrypting archive..."

# Create temp file for decrypted zip
TEMP_ZIP=$(mktemp).zip

# Decrypt the file
openssl enc -aes-256-cbc -d -in "$ENCRYPTED_FILE" -out "$TEMP_ZIP" -K "$KEY" -iv "$IV"

DECRYPTED_SIZE=$(du -h "$TEMP_ZIP" | cut -f1)
echo "   Decrypted archive: $DECRYPTED_SIZE"

echo "[3/4] Extracting files..."

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Extract zip
unzip -q "$TEMP_ZIP" -d "$OUTPUT_DIR"

FILE_COUNT=$(find "$OUTPUT_DIR" -type f | wc -l | tr -d ' ')
echo "   Extracted $FILE_COUNT files to: $OUTPUT_DIR"

echo "[4/4] Cleaning up..."
rm "$TEMP_ZIP"
echo "   Removed temporary files"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  DECRYPTION COMPLETE                                       ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  Output directory: $OUTPUT_DIR"
echo "║  Files extracted:  $FILE_COUNT"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Contents:"
ls -la "$OUTPUT_DIR" | head -20
