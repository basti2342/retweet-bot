GOOGLE_STORAGE_BUCKET=

gcsfuse $GOOGLE_STORAGE_BUCKET /app/store

exec "$@"