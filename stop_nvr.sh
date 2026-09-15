#!/bin/bash
# stop_nvr.sh — остановка всех процессов NVR

pkill -f bubble_full.py
pkill vlc
rm -f /tmp/nvr/ch0 /tmp/nvr/ch1 /tmp/nvr/ch2 /tmp/nvr/ch3
echo "Stopped"
