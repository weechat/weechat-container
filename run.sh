#! /bin/sh

usermod -o -u "${PUID:-1000}" weechat 2>&1 > /dev/null
groupmod -o -g "${PGID:-1000}" weechat 2>&1 > /dev/null

chown -R weechat:weechat /weechat

exec setpriv --reuid weechat --regid weechat --clear-groups /usr/bin/weechat "$@"
