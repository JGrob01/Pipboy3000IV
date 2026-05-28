import os

frames_dir = "assets/boot/"   # your 720x720 PNGs
out_list = "framelist.txt"

# Build the play order: 125..371 normally, but 348-371 repeated 3x total
order = list(range(125, 348))          # 125 through 347
for _ in range(3):                      # section played 3 times
    order += list(range(348, 372))      # 348 through 371
order += list(range(372, 372))          # nothing after in your case; adjust if frames go higher

with open(out_list, "w") as f:
    for n in order:
        path = os.path.join(frames_dir, f"{n}.png")
        f.write(f"file '{path}'\n")
        f.write("duration 0.0667\n")   # 15fps = 1/15s per frame

print(f"Wrote {len(order)} frame entries to {out_list}")