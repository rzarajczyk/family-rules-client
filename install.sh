command -v python3 >/dev/null 2>&1 || echo Python 3 is not installed

echo "Using python in version $(python3 --version)"

mkdir -p ~/Library/family-rules-client

if [ "$(ls -A ~/Library/family-rules-client)" ]; then
  >&2 echo "Directory ~/Library/family-rules-client is not empty. Cannot perform clean install."
  exit 1
fi

cd ~/Library/family-rules-client
git clone https://github.com/rzarajczyk/family-rules-client.git .

python3 -m pip install -r ~/Library/family-rules-client/requirements.txt

envsubst < pl.zarajczyk.family-rules-client.plist > ~/Library/LaunchAgents/pl.zarajczyk.family-rules-client.plist
