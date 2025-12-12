import os

site_packages = r"C:\Users\wahyu\AppData\Local\Programs\Python\Python312\Lib\site-packages"
packages = ['google', 'grpc', 'fastapi', 'uvicorn', 'pypdf', 'docx', 'pydantic', 'numpy', 'pandas', 'protobuf', 'google_api_core', 'google_auth', 'requests']

def get_dir_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                try:
                    total_size += os.path.getsize(fp)
                except:
                    pass
    return total_size

print(f"Checking sizes in {site_packages}")
for pkg in packages:
    pkg_path = os.path.join(site_packages, pkg)
    if os.path.exists(pkg_path):
        size = get_dir_size(pkg_path)
        print(f"{pkg}: {size / (1024*1024):.2f} MB")
    else:
        # Try finding it with metadata to see real name? or just prefix
        # for google it is often a namespace package
        print(f"{pkg}: Not found (possibly inside another folder or namespace)")

# Check google-related specifically
google_path = os.path.join(site_packages, 'google')
if os.path.exists(google_path):
    print(f"google (total): {get_dir_size(google_path) / (1024*1024):.2f} MB")
