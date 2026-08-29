import os
import psycopg

# 1. Connect to active DB and get news images
try:
    conn = psycopg.connect(
        dbname="postgres",
        user="postgres.xmrnlckrazptjbnmmhjj",
        password="Oa023568910@",
        host="aws-0-us-west-2.pooler.supabase.com",
        port="5432"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT featured_image FROM public.news_article WHERE featured_image IS NOT NULL AND featured_image != ''")
    img_paths = [r[0] for r in cursor.fetchall()]
    cursor.close()
    conn.close()
except Exception as e:
    print(f"DB Error: {e}")
    exit(1)

# Extract filenames (case-insensitive)
missing_filenames = set()
for ip in img_paths:
    norm = ip.replace('\\', '/')
    fname = norm.split('/')[-1].lower()
    missing_filenames.add(fname)

print(f"Searching for {len(missing_filenames)} unique news image filenames on all drives...")

# Local search roots
drives = ["C:\\", "D:\\"]
exclude_prefixes = [
    "c:\\windows",
    "c:\\program files",
    "c:\\program files (x86)",
    "c:\\users\\claud\\appdata",
    "c:\\users\\all users",
    "c:\\users\\default",
    "d:\\$recycle.bin",
    "d:\\system volume information",
    "d:\\config.msi"
]

found_paths = {} # filename -> list of full paths

for drive in drives:
    if not os.path.exists(drive):
        continue
    print(f"Scanning drive {drive}...")
    for root, dirs, files in os.walk(drive):
        root_lower = root.lower()
        if any(root_lower.startswith(prefix) for prefix in exclude_prefixes):
            dirs[:] = [] # don't recurse
            continue
            
        for f in files:
            f_lower = f.lower()
            if f_lower in missing_filenames:
                if f_lower not in found_paths:
                    found_paths[f_lower] = []
                found_paths[f_lower].append(os.path.join(root, f))

print("-" * 60)
print(f"Search Results:")
print(f"Total files searched: {len(missing_filenames)}")
print(f"Files found on disk: {len(found_paths)}")

if found_paths:
    print("\nFiles found on disk:")
    for fname, paths in found_paths.items():
        print(f"  - {fname}:")
        for p in paths:
            print(f"    {p}")
else:
    print("Nenhum arquivo encontrado localmente.")
