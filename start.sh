GOOGLE_STORAGE_BUCKET=pvsketch-145416.appspot.com

gcsfuse $GOOGLE_STORAGE_BUCKET /app/store

exec "$@"
