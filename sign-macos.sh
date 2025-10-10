#!/bin/bash
set -euxo pipefail

P12_BASE64=$1
P12_PASSWORD=$2

echo "Signing macOS app..."
RUNNER_TEMP="/tmp"

KEYCHAIN_PATH="~/app-signing.keychain-db"
KEYCHAIN_PASSWORD="buildkeychainpassword"

echo "Deleting existing keychain..."
security delete-keychain "$KEYCHAIN_PATH" || true

echo "Creating keychain..." 
security create-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH"

echo "Unlocking keychain..."
security unlock-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH"

echo "Setting keychain settings..."
security set-keychain-settings -t 7200 -l "$KEYCHAIN_PATH"

echo "Importing certificate..."
echo "$P12_BASE64" | base64 --decode > $RUNNER_TEMP/certificate.p12
security import $RUNNER_TEMP/certificate.p12 -k "$KEYCHAIN_PATH" -P "$P12_PASSWORD" -T /usr/bin/codesign

echo "Setting key partition list..."
security set-key-partition-list -S apple-tool:,apple: -s -k "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH"

echo "Setting default keychain..."
security default-keychain -s "$KEYCHAIN_PATH"

echo "Listing available identities..."
security find-identity

echo "Deleting keychain..."
# security default-keychain -s ~/Library/Keychains/login.keychain-db
# security delete-keychain "$KEYCHAIN_PATH"