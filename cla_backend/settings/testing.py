from .base import *
TEST_APPS = (
    #'django_pdb',
)

INSTALLED_APPS += TEST_APPS

SOUTH_TESTS_MIGRATE = False

TEST_MODE = True

ORIGINAL_DIAGNOSIS_FILE_NAME = DIAGNOSIS_FILE_NAME
DIAGNOSIS_FILE_NAME = '../tests/data/graph-2014.07.21.graphml'
