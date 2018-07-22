import os

SCAN_FRONT_LABEL = 'Label_4339693487728562381'
SCAN_BACK_LABEL = 'Label_1584516295397953489'

WATCH_LABELS = [SCAN_FRONT_LABEL, SCAN_BACK_LABEL]

DUPLEX_TARGET_LABEL = 'Label_7664683611205332333'

PROJECT_ID = os.environ['GOOGLE_CLOUD_PROJECT']

# dont use PROJECT_ID substitution in this variable, they could be on separate projects
TOPIC_NAME = 'projects/api-project-175925620434/topics/cloud-duplex'

# Processor settings

# Filesystem processor
FS_TARGET_DIR = 'combined_pdfs'
FS_FILENAME_FORMAT = '%d-%m-%Y_%H.%I.%S'