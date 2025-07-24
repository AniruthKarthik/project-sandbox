# Vidascii

ASCII-Based Video Playback in Terminal

## Overview

Vidascii was an experimental project aimed at rendering video playback within the terminal using ASCII characters.  
Each frame of the video was converted into ASCII art and displayed sequentially to simulate video playback.

## Challenges & Closure

While frame-to-ASCII conversion was successful, real-time playback proved infeasible due to several core limitations:

- **Terminal Refresh Bottleneck:** Most terminal emulators are not optimized for high frame rate rendering. Frequent `stdout` writes (e.g., 24+ frames/sec) overwhelmed the terminal, leading to noticeable lag and flicker.
- **Lack of True Framebuffer Access:** Terminals don't allow low-level control over screen redraw timing or pixel regions, unlike graphics APIs.
- **System I/O Overhead:** Reading and converting video frames on-the-fly added additional latency that compounded with output delays.
- **No Native Timing Sync:** Terminal apps lack vertical sync or hardware buffer timing, making smooth playback coordination nearly impossible.

Due to these architectural and hardware constraints, the project was discontinued as terminal-based video rendering isn’t viable for smooth playback at acceptable frame rates.

## Status

**Closed** – Inherent limitations in terminal rendering prevent usable video playback performance.


