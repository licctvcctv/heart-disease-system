#!/bin/bash
HOSTNAME=$(hostname)
CURRENT_IP=$(ip -4 addr show ens33 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
if [ -z "$CURRENT_IP" ]; then
  CURRENT_IP=$(ip -4 addr show | grep 'inet ' | grep -v 127.0.0.1 | head -1 | awk '{print $2}' | cut -d/ -f1)
fi
if [ -n "$CURRENT_IP" ]; then
  sed -i "/$HOSTNAME/d" /etc/hosts
  echo "$CURRENT_IP $HOSTNAME" >> /etc/hosts
  echo "Updated /etc/hosts: $CURRENT_IP -> $HOSTNAME"
fi
