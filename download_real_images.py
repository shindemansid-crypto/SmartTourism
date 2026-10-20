import os
import requests

images = {
    "ajanta-caves.jpg":
        "https://live.staticflickr.com/203/452434892_6f88a28ccf_b.jpg",

    "ellora-caves.jpg":
        "https://blog.novatr.com/hs-fs/hubfs/An%20image%20showing%20a%20detailed%20rock-cut%20structure%20highlighting%20Kailash%20temple%20architecture%20at%20Ellora.jpg?height=1024&width=1536",
}

os.makedirs("static/images", exist_ok=True)

headers = {"User-Agent": "Mozilla/5.0"}

for filename, url in images.items():
    try:
        print("Downloading:", filename)
        r = requests.get(url, headers=headers, timeout=30)

        if r.status_code == 200 and r.headers.get("Content-Type", "").startswith("image/"):
            with open(os.path.join("static/images", filename), "wb") as f:
                f.write(r.content)
            print("SUCCESS:", filename)
        else:
            print("FAILED:", filename, "HTTP", r.status_code)
    except Exception as e:
        print("ERROR:", filename, e)