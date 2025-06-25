import pygame
import time
import threading
import keyboard
from math import sin
from rich.console import Console
from rich.text import Text
from rich.live import Live
from rich.panel import Panel
from rich.style import Style
import colorsys
import os

# Ruta segura para el archivo de audio
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_FILE = os.path.join(BASE_DIR, "music", "cheziile.wav")

pygame.mixer.init()

# Letras con timestamps
lyrics = [
    (0, "🎵"),
    (19, "Hear it in your tone"),
    (24, "You're slowly letting go"),
    (29, "Are you turning off your phone?"),
    (33, "(ooh)"),
    (35, "Feelings turn cold"),
    (38, "So cold"),
    (40, "for"),
    (41, "you"),
    (49, "So cold"),
    (50, "for"),
    (51, "you"),
    (62, "Oh, I try to break apart, oh-woah"),
    (68, "You don't wanna try no more, oh, no more"),
    (70, "Why, why (oh) do you live in my mind, mind? Oh"),
    (75, "Said you looked past my love"),
    (80, "While I came with open arms"),
    (85, "For you"),
    (90, "For you"),
]

console = Console()
is_paused = False

def hsv_to_rgb_str(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

def format_time(seconds):
    mins = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{mins:02}:{secs:02}"

def render_wave_line(line, progress, time_offset, elapsed_time, paused):
    text = Text(justify="left")
    start_hue = 0.72  # Violeta
    end_hue = 0.85    # Azul claro

    wave_speed = 10

    for i, char in enumerate(line[:progress]):
        ratio = i / max(len(line) - 1, 1)
        hue = (start_hue + (end_hue - start_hue) * ratio + time_offset * 0.1) % 1
        color = hsv_to_rgb_str(hue, 0.8, 1.0)

        wave = sin(time_offset * wave_speed + i * 0.5)
        style = Style(color=color, bold=True, italic=True)
        text.append(char, style=style)

    if progress < len(line) and int(time_offset * 2) % 2 == 0:
        text.append("_", style=Style(color="bright_white", bold=True))

    timer = Text(
        f"{format_time(elapsed_time)}",
        style="bold bright_magenta"
    )

    panel_content = Text()
    panel_content.append(timer + "\n\n")
    panel_content.append(text)

    if paused:
        panel_content.append("\n\n[bold red]⏸ PAUSA[/bold red]")

    border_colors = ["bright_magenta", "magenta", "bright_cyan", "cyan"]
    border_color = border_colors[int(time_offset * 2) % len(border_colors)]

    title_hue = (time_offset * 0.5) % 1
    title_color = hsv_to_rgb_str(title_hue, 0.8, 1.0)
    title_styled = f"🌙  [bold italic {title_color}]KᗩᖇᗩOKE ᗩEՏƬᕮƬᕮƇ[/bold italic {title_color}]  💫"

    panel = Panel(
        panel_content,
        title=title_styled,
        border_style=border_color,
        padding=(1, 4)
    )
    return panel

def key_listener():
    global is_paused
    while True:
        if keyboard.is_pressed("p"):
            is_paused = not is_paused
            if is_paused:
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
            time.sleep(0.3)

def karaoke_terminal():
    global is_paused

    # Verifica existencia del archivo
    if not os.path.isfile(AUDIO_FILE):
        console.print(f"[red bold]❌ Archivo de audio no encontrado:[/red bold] {AUDIO_FILE}")
        return

    pygame.mixer.music.load(AUDIO_FILE)
    pygame.mixer.music.play()

    start_time = time.time()
    pause_time = 0
    current_line = 0
    char_index = 0

    threading.Thread(target=key_listener, daemon=True).start()

    with Live(console=console, refresh_per_second=20) as live:
        while pygame.mixer.music.get_busy():
            if is_paused:
                pause_time += 0.08
                time_offset = time.time()
                elapsed = time_offset - start_time - pause_time
                live.update(render_wave_line(
                    lyrics[current_line][1], char_index,
                    time_offset, elapsed, is_paused
                ))
                time.sleep(0.08)
                continue

            now = time.time()
            elapsed = now - start_time - pause_time

            if current_line < len(lyrics) - 1 and elapsed >= lyrics[current_line + 1][0]:
                current_line += 1
                char_index = 0

            if char_index < len(lyrics[current_line][1]):
                char_index += 1

            live.update(render_wave_line(
                lyrics[current_line][1], char_index,
                now, elapsed, is_paused
            ))
            time.sleep(0.08)

    console.print("\n[bold green]✨ ¡Final del track! ✨[/bold green]")

if __name__ == "__main__":
    karaoke_terminal()
