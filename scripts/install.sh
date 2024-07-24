mkdir -p ~/Library/family-rules-client
cd ~/Library/family-rules-client
cp /Users/rafal/Developer/my-family/build/libs/my-family-1.0-SNAPSHOT.jar ~/Library/my-family/my-family.jar
cp my-family.sh ~/Library/my-family

envsubst < pl.zarajczyk.my-family.plist > ~/Library/LaunchAgents/pl.zarajczyk.my-family.plist
