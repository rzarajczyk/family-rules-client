PYTHON_VERSION=$(/usr/bin/env python -c 'import sys; print(sys.version_info[:][0])')

if [[ "$PYTHON_VERSION" -lt "3" ]]; then
  >&2 echo "Python installed in ≪/usr/bin/env python≫ should be in version at least 3"
  exit 1
fi

mkdir -p ~/Library/family-rules-client

if [ "$(ls -A ~/Library/family-rules-client)" ]; then
  >&2 echo "Directory ~/Library/family-rules-client is not empty. Cannot perform clean install."
  exit 1
fi

cd ~/Library/family-rules-client
git clone https://github.com/rzarajczyk/family-rules-client.git .

/usr/bin/env python -m pip install -r /path/to/requirements.txt

envsubst < pl.zarajczyk.family-rules-client.plist > ~/Library/LaunchAgents/pl.zarajczyk.family-rules-client.plist
