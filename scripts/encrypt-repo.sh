#!/bin/bash
# encrypt-repo.sh - Zip non-gitignored files and encrypt with AES-256 random key
# Usage: ./encrypt-repo.sh [output_name]

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUTPUT_NAME="${1:-PLA-Defense-CAD}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="$REPO_ROOT/encrypted_exports"
ZIP_FILE="$OUTPUT_DIR/${OUTPUT_NAME}_${TIMESTAMP}.zip"
ENCRYPTED_FILE="$OUTPUT_DIR/${OUTPUT_NAME}_${TIMESTAMP}.zip.enc"
KEY_FILE="$OUTPUT_DIR/${OUTPUT_NAME}_${TIMESTAMP}.key"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  PLA-Defense-CAD Encryption Script                         ║"
echo "║  AES-256 Encryption with Random Key                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Navigate to repo root
cd "$REPO_ROOT"

echo "[1/5] Collecting non-gitignored files..."

# Create a temporary file list
TEMP_LIST=$(mktemp)

# Get all files tracked by git + untracked but not ignored
git ls-files > "$TEMP_LIST"
git ls-files --others --exclude-standard >> "$TEMP_LIST"

# Remove duplicates and sort
sort -u "$TEMP_LIST" -o "$TEMP_LIST"

FILE_COUNT=$(wc -l < "$TEMP_LIST" | tr -d ' ')
echo "   Found $FILE_COUNT files to include"

echo "[2/5] Creating zip archive..."
# Create zip from the file list
cat "$TEMP_LIST" | zip -@ "$ZIP_FILE" > /dev/null 2>&1

ZIP_SIZE=$(du -h "$ZIP_FILE" | cut -f1)
echo "   Created: $ZIP_FILE ($ZIP_SIZE)"

# Clean up temp file
rm "$TEMP_LIST"

echo "[3/5] Generating random AES-256 key..."
# Generate 256-bit (32 byte) random key and encode as hex
RANDOM_KEY=$(openssl rand -hex 32)

# Also generate random IV (16 bytes for AES)
RANDOM_IV=$(openssl rand -hex 16)

# Save key and IV to file
echo "# AES-256-CBC Encryption Key" > "$KEY_FILE"
echo "# Generated: $(date)" >> "$KEY_FILE"
echo "# File: ${OUTPUT_NAME}_${TIMESTAMP}.zip.enc" >> "$KEY_FILE"
echo "" >> "$KEY_FILE"
echo "KEY=$RANDOM_KEY" >> "$KEY_FILE"
echo "IV=$RANDOM_IV" >> "$KEY_FILE"

echo "   Key generated and saved to: $KEY_FILE"

echo "[4/5] Encrypting with AES-256-CBC..."
# Encrypt the zip file with AES-256-CBC
openssl enc -aes-256-cbc -salt -in "$ZIP_FILE" -out "$ENCRYPTED_FILE" -K "$RANDOM_KEY" -iv "$RANDOM_IV"

ENCRYPTED_SIZE=$(du -h "$ENCRYPTED_FILE" | cut -f1)
echo "   Encrypted: $ENCRYPTED_FILE ($ENCRYPTED_SIZE)"

echo "[5/5] Cleaning up unencrypted zip..."
rm "$ZIP_FILE"
echo "   Removed unencrypted zip"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ENCRYPTION COMPLETE                                       ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  Encrypted file: ${OUTPUT_NAME}_${TIMESTAMP}.zip.enc"
echo "║  Key file:       ${OUTPUT_NAME}_${TIMESTAMP}.key"
echo "║  Location:       $OUTPUT_DIR"
echo "║                                                            ║"
echo "║  ⚠ KEEP THE .key FILE SECURE - Required for decryption   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "To decrypt, run:"
echo "  ./scripts/decrypt-repo.sh $ENCRYPTED_FILE $KEY_FILE"
