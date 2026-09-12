
import argparse
import sys
from pathlib import Path
from collections import Counter

import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp'}
MIN_BLOB_AREA_FRACTION = 0.0005  # ignore mask blobs smaller than 0.05% of image area (noise)


def find_all_images(images_dir: Path):
    return sorted([p for p in images_dir.rglob('*') if p.suffix.lower() in IMAGE_EXTENSIONS])


def build_mask_index(gt_dir: Path):
    """Maps filename stem (lowercase, no extension) -> mask file path."""
    index = {}
    for p in gt_dir.rglob('*'):
        if p.suffix.lower() in IMAGE_EXTENSIONS:
            index[p.stem.lower()] = p
    return index


def is_readable_image(path: Path) -> bool:
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception:
        return False


def count_mask_blobs(mask_path: Path, img_area: int) -> int:
    mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
    if mask is None:
        return -1
    _, binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_area = MIN_BLOB_AREA_FRACTION * img_area
    return sum(1 for c in contours if cv2.contourArea(c) >= min_area)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw-dir', required=True, help='Path to CAMO-V.1.0-CVIU2019 folder')
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir).expanduser().resolve()
    images_dir = raw_dir / 'Images'
    gt_dir = raw_dir / 'GT'

    if not images_dir.is_dir() or not gt_dir.is_dir():
        print(f'ERROR: expected {images_dir} and {gt_dir} to both exist. Check --raw-dir.')
        sys.exit(1)

    print(f'Scanning images under: {images_dir}')
    images = find_all_images(images_dir)
    print(f'Found {len(images)} image files.\n')

    print(f'Indexing masks under: {gt_dir}')
    mask_index = build_mask_index(gt_dir)
    print(f'Found {len(mask_index)} mask files.\n')

    corrupted = []
    missing_mask = []
    dims = Counter()
    blob_counts = Counter()
    split_counts = Counter()

    for img_path in tqdm(images, desc='Inspecting'):
        split = 'Train' if 'train' in str(img_path).lower() else ('Test' if 'test' in str(img_path).lower() else 'Unknown')
        split_counts[split] += 1

        if not is_readable_image(img_path):
            corrupted.append(str(img_path))
            continue

        stem = img_path.stem.lower()
        if stem not in mask_index:
            missing_mask.append(str(img_path))
            continue

        with Image.open(img_path) as im:
            dims[im.size] += 1
            area = im.size[0] * im.size[1]

        n_blobs = count_mask_blobs(mask_index[stem], area)
        blob_counts[n_blobs] += 1

    print('\n========== SUMMARY ==========')
    print(f'Total images:            {len(images)}')
    print(f'  by split:              {dict(split_counts)}')
    print(f'Corrupted/unreadable:    {len(corrupted)}')
    print(f'Missing a matching mask: {len(missing_mask)}')
    print(f'Most common dimensions (top 5): {dims.most_common(5)}')
    print(f'Number of masks with 0 detected blobs (all-black / fully noise-filtered): {blob_counts.get(0, 0)}')
    print(f'Blob-count distribution (instances per image, top 10): {blob_counts.most_common(10)}')

    if corrupted:
        print('\nFirst 5 corrupted files:')
        for f in corrupted[:5]:
            print(f'  {f}')

    if missing_mask:
        print('\nFirst 5 images with no matching mask:')
        for f in missing_mask[:5]:
            print(f'  {f}')

    print('\nDone. Use these numbers to sanity-check against the README before converting.')


if __name__ == '__main__':
    main()