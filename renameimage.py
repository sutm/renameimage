# rename images based on exif data
# can be used to merge photos from different cameras
# to sort them in sequence of time taken

from os import walk, path, chdir, getcwd
from shutil import copy2
from contextlib import contextmanager
from PIL import Image, ExifTags

srcfolder = r'd:/photo/Photos/original'
dstfolder = r'd:/photo/Photos/merged'
minleadingzeros = 4
ExifDateTimeFields = ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']

def get_exif_datetaken_keys():
    exif_datetaken_keys = {}
    for k, v in ExifTags.TAGS.items():
        if v in ExifDateTimeFields:
            exif_datetaken_keys[k] = v
    return exif_datetaken_keys;

exif_datetaken_keys = get_exif_datetaken_keys()
if len(exif_datetaken_keys) == 0:
    print("Error: not able to retrieve date taken from exif data")
    exit;

assert path.exists(srcfolder)
assert path.exists(dstfolder)

@contextmanager
def cd(path):
    old_dir = getcwd()
    chdir(path)
    yield
    chdir(old_dir)

def get_images_datetime(imagefiles):
    image_datetime = {}
    for dirname, filenames in imagefiles:
        with cd(dirname):
            for f in filenames:
                img = Image.open(f)
                exif = img._getexif()
                if exif is None:
                    print ("error in getting exif of %s" % f)
                    continue
                mtime = None
                for k in exif_datetaken_keys:
                    if k in exif:
                        mtime = exif[k]
                        image_datetime[mtime] = path.join(dirname, f)
                        break
                if mtime is None:
                    print ("error in getting exif data of %s" % f)
                    continue
    return image_datetime

files = [(dirname, filenames) for dirname, subdirs, filenames in walk(srcfolder) if not dirname.endswith('videos')]
datetimes = get_images_datetime(files)

totalimages = 0
for i, key in enumerate(sorted(datetimes)):
    _, ext = path.splitext(datetimes[key])
    newfilename = str(i+1).zfill(minleadingzeros) + ext
    outputfile = path.join(dstfolder, newfilename)
    inputfile = datetimes[key]
    copy2(inputfile, outputfile)
    print("Copy %s to %s" % (inputfile, outputfile))
    totalimages = i+1

print("Copied %d images" % totalimages)