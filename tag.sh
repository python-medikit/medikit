
if [ -z "$1" ]; then
  echo "please provide release."
  exit 1
fi

echo $1 > version.txt
git add version.txt
git commit -m "release: $1"
git tag -am $1 $1


