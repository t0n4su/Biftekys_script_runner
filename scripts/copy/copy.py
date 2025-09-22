import zipfile
import os
import shutil
import sys

# --------- Step 1: Define the folder structure ---------
folder_structure = [
    "MediaTrack/Updated Frontend Files",
    "MediaTrack/Backend Files",
    "MediaTrack/Backend Files/config",
    "MediaTrack/Backend Files/routes",
    "MediaTrack/Backend Files/services",
    "MediaTrack/Deployment Configuration",
    "MediaTrack/Deployment Configuration/.github/workflows"
]

# Create all folders
for folder in folder_structure:
    os.makedirs(folder, exist_ok=True)

# --------- Step 2: Handle ZIP file input ---------
if len(sys.argv) < 2:
    print("❌ Please drag & drop your ZIP file onto this script or provide its path as an argument.")
    sys.exit(1)

zip_path = sys.argv[1]

if not os.path.isfile(zip_path):
    print(f"❌ File not found: {zip_path}")
    sys.exit(1)

# --------- Step 3: Copy files from ZIP into tree ---------
def safe_copy(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    for member in zip_ref.namelist():
        if member.endswith('/'):
            continue  # skip directories
        
        temp_path = zip_ref.extract(member, 'temp_extract')
        filename = os.path.basename(member)

        # --- Step 4: Smart placement based on file names ---
        # Frontend files
        if filename in ["index_updated.html", "style_updated.css", "app_updated.js"]:
            dest_path = os.path.join("MediaTrack/Updated Frontend Files", filename)
        # Backend files
        elif filename in ["server.js", "package.json"]:
            dest_path = os.path.join("MediaTrack/Backend Files", filename)
        elif filename == "database.js":
            dest_path = os.path.join("MediaTrack/Backend Files/config", filename)
        elif filename.endswith(".js"):
            if filename == "externalApis.js":
                dest_path = os.path.join("MediaTrack/Backend Files/services", filename)
            else:
                dest_path = os.path.join("MediaTrack/Backend Files/routes", filename)
        # Deployment configuration
        elif filename in ["Dockerfile", "docker-compose.yml", "netlify.toml", "vercel.json", "setup.sh", "PROJECT_README.md"]:
            dest_path = os.path.join("MediaTrack/Deployment Configuration", filename)
        # GitHub workflow
        elif member.startswith(".github/workflows/"):
            dest_path = os.path.join("MediaTrack/Deployment Configuration", member)
        # Environment template
        elif filename == ".env.example":
            dest_path = os.path.join("MediaTrack/Backend Files", filename)
        else:
            # Unknown files go to root MediaTrack
            dest_path = os.path.join("MediaTrack", filename)

        safe_copy(temp_path, dest_path)

# Clean up temp folder
shutil.rmtree('temp_extract')

print("✅ MediaTrack tree created and files added successfully!")
