#!/bin/bash

docker run --rm \
    -v /home/marin/shared/media/paperless-inboxe:/consume \
    -v /home/marin/google-drive-sync/data:/data \
    -e DESTINATION_FOLDER=/consume \
    -e DELETE_AFTER_DOWNLOAD=true \
    google-drive-sync >> /home/marin/google-drive-sync/sync.log 2>&1
