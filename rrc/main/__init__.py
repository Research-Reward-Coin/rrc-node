import sys
import os
import time
import hashlib
import zipfile
import json
from rrc import _debug as _debug

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def xprint(component="node", code="inf", message="\n"): # info, warning, error, debug.
    ts = time.gmtime()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)

    if code == "warn":
        color = bcolors.WARNING+bcolors.UNDERLINE
    elif code == "err":
        color = bcolors.FAIL+bcolors.UNDERLINE
    elif code == "deb":
        color = bcolors.OKBLUE+bcolors.UNDERLINE
    else:
        color = bcolors.BOLD

    # if not _debug and code == "deb":
    #     pass
    # else:
    print("{0}{1}{2} RRC {3}{4}{5} >> {6}{7}{8}".format(bcolors.HEADER, timestamp, bcolors.ENDC, bcolors.OKGREEN, component, bcolors.ENDC, color, message, bcolors.ENDC))

def persist_job(job):
    with open("rrc-{0}.job".format(job['id']), "w") as job_file:
        job_file.write(json.dumps(job, sort_keys=True, indent=4))

def sha256_digest(filename, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()

def pack(filename, distination):
    try:
        folder_path = "{0}/{1}".format(distination, filename)
        base_dir = os.path.abspath(folder_path)
        with zipfile.ZipFile("{0}/{1}.zip".format(distination, filename), "w", zipfile.ZIP_DEFLATED) as zf:
            base_path = os.path.normpath("{0}".format(distination))
            # xprint(base_path)
            for dirpath, dirnames, filenames in os.walk(base_dir):
                for name in sorted(dirnames):
                    path = os.path.normpath(os.path.join(dirpath, name))
                    # xprint(path)
                    zf.write(path, os.path.relpath(path, base_path))
                for name in filenames:
                    path = os.path.normpath(os.path.join(dirpath, name))
                    # xprint(os.path.relpath(path, base_path))
                    if os.path.isfile(path):
                        zf.write(path, os.path.relpath(path, base_path))
        return True
    except Exception as e:
        xprint("RRC Node >> Error: Could not pack {0}.".format(filename))
        xprint("RRC Node >> Exception: {0}.".format(str(e)))
        return False

def unpack(filename, distination):
    blocks = filename.split(".")
    if blocks[1] == "zip": #Only one supported for now.
        try:
            zip_ref = zipfile.ZipFile("{0}/{1}".format(distination, filename), 'r')
            zip_ref.extractall("{0}/".format(distination))
            zip_ref.close()
            return True
        except Exception as e:
            xprint("RRC Node >> Error: Could not unpack {0}.".format(filename))
            xprint("RRC Node >> Exception: {0}.".format(str(e)))
            return False
    else:
        return False
        xprint("RRC Node >> Unknown compression extension {0}. Noting will be done to the file.".format(blocks[1]))

def get_file(location, id):
    filename = location.split('/')[-1]
    origin = "/tmp/rrc/{0}/{1}".format(id, filename)
    if "http" in location:
        try:
            filename = location.split('/')[-1]
            r = requests.get(location, stream=True)
            with open(origin, 'wb') as f:
               for chunk in r.iter_content(chunk_size=1024):
                   if chunk:
                     f.write(chunk)
            return filename, "/tmp/rrc/{0}".format(id)
        except Exception as e:
            xprint("Computing", "err", "Exception: {0}".format(str(e)))
            return filename, None
    else:
        try:
            filename = location.split('/')[-1]
            with open(location, "rb") as source_f:
                with open(origin, 'wb') as f:
                    f.write(source_f.read())
            return filename, "/tmp/rrc/{0}".format(id)
        except Exception as e:
            xprint("Computing", "err", "Exception: {0}".format(str(e)))
            return filename, None
