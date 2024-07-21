MIN_JAVA_VERSION=17

if ! type -p java > /dev/null; then
  >&2 echo "Java not found (you need at least Java $MIN_JAVA_VERSION)"
  exit 1
fi

VERSION=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}' | cut -d '.' -f 1)
if [[ "$VERSION" -lt "$MIN_JAVA_VERSION" ]]; then
  >&2 echo "Java is required in version at least $MIN_JAVA_VERSION; found $VERSION"
  exit 1
fi

mkdir -p ~/Library/my-family
cp /Users/rafal/Developer/my-family/build/libs/my-family-1.0-SNAPSHOT.jar ~/Library/my-family/my-family.jar
cp my-family.sh ~/Library/my-family

envsubst < pl.zarajczyk.my-family.plist > ~/Library/LaunchAgents/pl.zarajczyk.my-family.plist
