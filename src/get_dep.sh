echo 'download' $1 '...'
python3 -m pip install --ignore-installed --dry-run $1 --report pipdeptree/$1.json --quiet
echo $1 'finish'