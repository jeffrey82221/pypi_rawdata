python3 -m venv venv/$1
source venv/$1/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install pipdeptree
echo 'pip freeze before install' $1
python3 -m pip freeze
python3 -m pip install $1 --quiet
echo 'pip freeze after install' $1
python3 -m pip freeze
pipdeptree --warn silence --package $1 --json-tree >> data/pipdeptree/$1.json
deactivate
rm -r venv/$1