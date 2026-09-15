#!/bin/bash
# start_nvr.sh — запуск 4 окон VLC с каналами NVR

# Убить старые процессы
pkill -f bubble_full.py
pkill vlc
sleep 1

# Создать FIFO
mkdir -p /tmp/nvr
rm -f /tmp/nvr/ch0 /tmp/nvr/ch1 /tmp/nvr/ch2 /tmp/nvr/ch3
mkfifo /tmp/nvr/ch0 /tmp/nvr/ch1 /tmp/nvr/ch2 /tmp/nvr/ch3

# Запустить Python
python3 ~/nvr_k8204w_bubble_watch/bubble_full.py 0 1 > /tmp/nvr/ch0 2>/dev/null &
python3 ~/nvr_k8204w_bubble_watch/bubble_full.py 1 1 > /tmp/nvr/ch1 2>/dev/null &
python3 ~/nvr_k8204w_bubble_watch/bubble_full.py 2 1 > /tmp/nvr/ch2 2>/dev/null &
python3 ~/nvr_k8204w_bubble_watch/bubble_full.py 3 1 > /tmp/nvr/ch3 2>/dev/null &
sleep 3

# Запустить 4 окна VLC
vlc /tmp/nvr/ch0 --demux h264 --intf dummy --video-x 0   --video-y 0   --width 640 --height 360 --no-video-title-show &
vlc /tmp/nvr/ch1 --demux h264 --intf dummy --video-x 640 --video-y 0   --width 640 --height 360 --no-video-title-show &
vlc /tmp/nvr/ch2 --demux h264 --intf dummy --video-x 0   --video-y 360 --width 640 --height 360 --no-video-title-show &
vlc /tmp/nvr/ch3 --demux h264 --intf dummy --video-x 640 --video-y 360 --width 640 --height 360 --no-video-title-show &
