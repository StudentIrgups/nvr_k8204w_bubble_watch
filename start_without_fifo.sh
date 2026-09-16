#!/bin/bash
# start_nvr.sh — 4 окна VLC напрямую через pipe, без FIFO

pkill -f bubble_full.py
pkill vlc
sleep 1

python3 ~/nvr_k8204w_bubble_watch/bubble_full.py 0 1 2>/dev/null | \
  vlc fd://0 --demux h264 --intf dummy \
      --video-x 0   --video-y 0   --width 640 --height 360 \
      --no-video-title-show &

python3 ~/nvr_k8204w_bubble_watch/bubble_full.py 1 1 2>/dev/null | \
  vlc fd://0 --demux h264 --intf dummy \
      --video-x 640 --video-y 0   --width 640 --height 360 \
      --no-video-title-show &

python3 ~/nvr_k8204w_bubble_watch/bubble_full.py 2 1 2>/dev/null | \
  vlc fd://0 --demux h264 --intf dummy \
      --video-x 0   --video-y 360 --width 640 --height 360 \
      --no-video-title-show &

python3 ~/nvr_k8204w_bubble_watch/bubble_full.py 3 1 2>/dev/null | \
  vlc fd://0 --demux h264 --intf dummy \
      --video-x 640 --video-y 360 --width 640 --height 360 \
      --no-video-title-show &
