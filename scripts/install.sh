mkdir -p ~/Library/family-rules-client
cd ~/Library/family-rules-client
git clone https://github.com/rzarajczyk/family-rules-client.git

cd scripts
envsubst < pl.zarajczyk.family-rules-client.plist > ~/Library/LaunchAgents/pl.zarajczyk.family-rules-client.plist
