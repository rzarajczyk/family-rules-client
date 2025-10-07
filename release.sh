#!/bin/bash

# Configure git to remember credentials for 1 hour (3600 seconds)
git config --global credential.helper 'cache --timeout=3600'

# Start SSH agent and add SSH key to remember passphrase
eval "$(ssh-agent -s)"
ssh-add --apple-use-keychain ~/.ssh/id_rsa 2>/dev/null || ssh-add ~/.ssh/id_rsa 2>/dev/null

UNCOMMITED_FILES=$(git status --porcelain=v1 2>/dev/null | wc -l)
if [[ "$UNCOMMITED_FILES" -gt 0 ]]; then
  echo "Uncommited files detected. Please commit first!"
  exit 1
fi

echo "Pulling newest changes..."
git pull

LATEST_VERSION=$(git describe --tags --abbrev=0)
NEXT_VERSION=$(echo "$LATEST_VERSION" | awk -F. -v OFS=. '{$NF += 1 ; print}')

echo "The current version is $LATEST_VERSION, preparing $NEXT_VERSION..."

echo "$NEXT_VERSION" > ./src/resources/version.txt
git add ./src/resources/version.txt
git commit -m "Version bump: $NEXT_VERSION"
git tag "$NEXT_VERSION"

echo "Pushing changes..."
git push origin
git push origin --tags