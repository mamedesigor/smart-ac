#!/bin/sh

while true; do
	if [ -f "sqlite3bkp.db" ]; then
		rclone copy sqlite3bkp.db database_backup: && echo "[BACKUP] $(date)"
		rm sqlite3bkp.db
	fi
	sleep 5;
done

