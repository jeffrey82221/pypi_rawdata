python3 -m venv venv/$1
source venv/$1/bin/activate
python3 -m pip install --upgrade pip --quiet
python3 -m pip install wheel --quiet
python3 -m pip install setuptools --quiet
python3 -m pip install pipdeptree --quiet
python3 -m pip install $1 --quiet
pipdeptree --warn silence --package $1 --json-tree >> data/pipdeptree/$1.json
deactivate
rm -r venv/$1