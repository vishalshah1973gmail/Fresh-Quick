"""Build the narrated customer demo video from storyboard.json.

Usage (from the repo root):
  python scripts/demo-video/build.py            # full video
  python scripts/demo-video/build.py --only 04-signup-empty   # one scene, for checking

Needs: ffmpeg/ffprobe on PATH, Pillow, edge-tts (narration is synthesised by
Microsoft's online speech service, so the narration text leaves this machine).
Screenshots live in frames/ (git-ignored); output goes to out/ (git-ignored).
"""

import argparse
import asyncio
import hashlib
import json
import subprocess
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FRAMES = HERE / "frames"
BUILD = HERE / "build"
OUT = HERE / "out"

W, H = 1920, 1080
SHOT_H = 826  # 1568x675 screenshots scaled to 1920 wide
CAP_H = H - SHOT_H
FPS = 30
LEAD_IN, TAIL = 0.35, 0.65
FADE = 0.3
ZOOM = 0.06

PRIMARY = (245, 130, 31)
INK = (11, 29, 58)
WHITE = (255, 255, 255)
FONT_DIR = Path("C:/Windows/Fonts")


def font(size, bold=False):
  return ImageFont.truetype(str(FONT_DIR / ("segoeuib.ttf" if bold else "segoeui.ttf")), size)


def wrap(draw, text, fnt, max_width):
  lines, line = [], ""
  for word in text.split():
    candidate = f"{line} {word}".strip()
    if draw.textlength(candidate, font=fnt) <= max_width:
      line = candidate
    else:
      lines.append(line)
      line = word
  if line:
    lines.append(line)
  return lines


def caption_panel(label, text):
  img = Image.new("RGB", (W, CAP_H), INK)
  draw = ImageDraw.Draw(img)
  pad_x = 64
  if label:
    chip_font = font(26, bold=True)
    chip_w = draw.textlength(label, font=chip_font) + 36
    draw.rounded_rectangle([pad_x, 22, pad_x + chip_w, 62], radius=20, fill=PRIMARY)
    draw.text((pad_x + 18, 42), label, font=chip_font, fill=WHITE, anchor="lm")
  top = 80 if label else 40
  # Shrink the text until the narration fits the panel.
  for size in (34, 31, 28, 25):
    fnt = font(size)
    lines = wrap(draw, text, fnt, W - 2 * pad_x)
    line_h = int(size * 1.35)
    if top + line_h * len(lines) <= CAP_H - 16:
      break
  for i, line in enumerate(lines):
    draw.text((pad_x, top + i * line_h), line, font=fnt, fill=WHITE)
  return img


def apply_masks(img, masks):
  # Paint out password-manager icons: copy each row from just left of the box.
  px = img.load()
  for x0, y0, x1, y1 in masks or []:
    for y in range(y0, y1):
      colour = px[x0 - 3, y]
      for x in range(x0, x1):
        px[x, y] = colour
  return img


def shot_image(scene):
  src = Image.open(FRAMES / scene["frame"]).convert("RGB")
  src = apply_masks(src, scene.get("masks"))
  scale = W / src.width
  img = src.resize((W, round(src.height * scale)), Image.LANCZOS).crop((0, 0, W, SHOT_H))
  hl = scene.get("highlight")
  if hl:
    x0, y0, x1, y1 = [round(v * scale) for v in hl]
    y1 = min(y1, SHOT_H - 4)
    shade = Image.new("RGBA", img.size, (11, 29, 58, 95))
    ImageDraw.Draw(shade).rectangle([x0, y0, x1, y1], fill=(0, 0, 0, 0))
    img = Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB")
    ImageDraw.Draw(img).rounded_rectangle([x0, y0, x1, y1], radius=14, outline=PRIMARY, width=6)
    focus = ((x0 + x1) / 2 / W, (y0 + y1) / 2 / SHOT_H)
  else:
    focus = (0.5, 0.5)
  return img, focus


def card_image(card):
  img = Image.new("RGB", (W, SHOT_H), PRIMARY)
  draw = ImageDraw.Draw(img)
  # Soft diagonal fade to a lighter orange, echoing the site's hero banner.
  for x in range(W):
    t = max(0.0, (x - W * 0.45) / (W * 0.55))
    colour = tuple(round(c + (255 - c) * 0.75 * t) for c in PRIMARY)
    draw.line([(x, 0), (x, SHOT_H)], fill=colour)
  title_font = font(96 if len(card["title"]) < 20 else 70, bold=True)
  draw.text((W / 2, SHOT_H / 2 - 40), card["title"], font=title_font, fill=WHITE, anchor="mm")
  draw.text((W / 2, SHOT_H / 2 + 60), card.get("subtitle", ""), font=font(44), fill=WHITE, anchor="mm")
  return img, (0.5, 0.5)


async def narrate(text, voice, rate, path):
  await edge_tts.Communicate(text, voice, rate=rate).save(str(path))


def probe_duration(path):
  out = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
    check=True, capture_output=True, text=True,
  )
  return float(out.stdout.strip())


def render_scene(scene, cfg):
  sid = scene["id"]
  text = scene["narration"]
  key = hashlib.sha1(f"{cfg['voice']}|{cfg['rate']}|{text}".encode()).hexdigest()[:10]
  audio = BUILD / f"{sid}-{key}.mp3"
  if not audio.exists():
    asyncio.run(narrate(text, cfg["voice"], cfg["rate"], audio))
  duration = LEAD_IN + probe_duration(audio) + TAIL

  top, focus = card_image(scene["card"]) if "card" in scene else shot_image(scene)
  top_path = BUILD / f"{sid}-top.png"
  cap_path = BUILD / f"{sid}-cap.png"
  top.save(top_path)
  caption_panel(scene.get("label"), text).save(cap_path)

  frames = round(duration * FPS)
  zoom = 0 if "card" in scene else ZOOM
  fx, fy = focus
  # Upscale 2x before zoompan so the slow zoom does not judder.
  zoompan = (
    f"scale={W * 2}:{SHOT_H * 2},"
    f"zoompan=z='1+{zoom}*on/{frames}':"
    f"x='max(0,min(iw-iw/zoom,{fx}*iw-iw/zoom/2))':"
    f"y='max(0,min(ih-ih/zoom,{fy}*ih-ih/zoom/2))':"
    f"d=1:s={W}x{SHOT_H}:fps={FPS}"
  )
  delay_ms = round(LEAD_IN * 1000)
  graph = (
    f"[0:v]{zoompan}[z];[z]pad={W}:{H}:0:0[p];[p][1:v]overlay=0:{SHOT_H},"
    f"fade=in:st=0:d={FADE},fade=out:st={duration - FADE:.3f}:d={FADE},format=yuv420p[v];"
    f"[2:a]adelay={delay_ms}|{delay_ms},apad,atrim=0:{duration:.3f},aresample=48000[a]"
  )
  clip = BUILD / f"{sid}.mp4"
  subprocess.run(
    [
      "ffmpeg", "-y", "-v", "error",
      "-loop", "1", "-framerate", str(FPS), "-i", str(top_path),
      "-loop", "1", "-framerate", str(FPS), "-i", str(cap_path),
      "-i", str(audio),
      "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
      "-t", f"{duration:.3f}", "-r", str(FPS),
      "-c:v", "libx264", "-preset", "medium", "-crf", "20",
      "-c:a", "aac", "-b:a", "160k", "-ac", "2",
      str(clip),
    ],
    check=True,
  )
  return clip, probe_duration(clip)


def srt_time(seconds):
  ms = round(seconds * 1000)
  h, ms = divmod(ms, 3_600_000)
  m, ms = divmod(ms, 60_000)
  s, ms = divmod(ms, 1000)
  return f"{h:02}:{m:02}:{s:02},{ms:03}"


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--only", help="render a single scene id")
  args = parser.parse_args()

  cfg = json.loads((HERE / "storyboard.json").read_text(encoding="utf-8"))
  BUILD.mkdir(exist_ok=True)
  OUT.mkdir(exist_ok=True)
  scenes = [s for s in cfg["scenes"] if not args.only or s["id"] == args.only]
  if not scenes:
    raise SystemExit(f"No scene with id {args.only!r}")

  clips, srt, t = [], [], 0.0
  for i, scene in enumerate(scenes, 1):
    clip, dur = render_scene(scene, cfg)
    print(f"{scene['id']}: {dur:.1f}s")
    clips.append(clip)
    srt.append(f"{i}\n{srt_time(t + LEAD_IN)} --> {srt_time(t + dur - 0.2)}\n{scene['narration']}\n")
    t += dur

  name = f"scene-{args.only}" if args.only else "Fresh_and_Quick_Demo"
  listing = BUILD / "concat.txt"
  listing.write_text("".join(f"file '{c.as_posix()}'\n" for c in clips), encoding="utf-8")
  subprocess.run(
    ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
     "-c", "copy", "-movflags", "+faststart", str(OUT / f"{name}.mp4")],
    check=True,
  )
  (OUT / f"{name}.srt").write_text("\n".join(srt), encoding="utf-8")
  print(f"Wrote {OUT / (name + '.mp4')} ({t / 60:.1f} min)")


if __name__ == "__main__":
  main()
