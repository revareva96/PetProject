echo 'sorting ...'
sh tools/ci/isort.sh
echo 'pre commit ...'
pre-commit run --all-files
echo 'run testing ...'
sh tools/ci/coverage.sh