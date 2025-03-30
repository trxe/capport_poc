if [[ -z "${VIRTUAL_ENV}" ]];
then 
    echo "Enable venv";
    exit 1;
fi

PROJ_DIR=${VIRTUAL_ENV}/..

echo "Running black"
python -m black ${PROJ_DIR}/src ${PROJ_DIR}/tests
echo "Running isort"
python -m isort ${PROJ_DIR}/src ${PROJ_DIR}/tests
echo "Running pylint"
python -m pylint ${PROJ_DIR}/src