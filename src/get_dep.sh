python3 -m venv $1
source $1/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install pipdeptree
# python3 -m pip freeze >> $1.before.log
python3 -m pip install $1
# python3 -m pip freeze >> $1.after.log
pipdeptree --warn silence --package $1 --json-tree >> data/pipdeptree/$1.json
deactivate
rm -r $1