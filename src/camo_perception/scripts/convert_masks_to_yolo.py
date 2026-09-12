#!/usr/bin/env python3


import argparse
import random
import shutil
import sys
from pathlib import Path

import cv2
import yaml
from tqdm import tqdm

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp'}
MIN_BLOB_AREA_FRACTION = 0.0005
VAL_FRACTION = 0.15
RANDOM_SEED = 42


def find_all_images(images_dir: Path):
    return sorted([p for p in images_dir.rglob('*') if p.suffix.lower() in IMAGE_EXTENSIONS])


def build_mask_index(gt_dir: Path):
    index = {}
    for p in gt_dir.rglob('*'):
        if p.suffix.lower() in IMAGE_EXTENSIONS:
            index[p.stem.lower()] = p
    return index


def mask_to_yolo_lines(mask_path: Path, img_w: int, img_h: int):
    """Returns a list of YOLO-format label lines: 'class cx cy w h' (normalized)."""
    mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
    if mask is None:
        return []

    if mask.shape[1] != img_w or mask.shape[0] != img_h:
        mask = cv2.resize(mask, (img_w, img_h), interpolation=cv2.INTER_NEAREST)

    _, binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    img_area = img_w * img_h
    min_area = MIN_BLOB_AREA_FRACTION * img_area

    lines = []
    for c in contours:
        if cv2.contourArea(c) < min_area:
            continue
        x, y, w, h = cv2.boundingRect(c)
        cx = (x + w / 2) / img_w
        cy = (y + h / 2) / img_h
        norm_w = w / img_w
        norm_h = h / img_h
        lines.append(f'0 {cx:.6f} {cy:.6f} {norm_w:.6f} {norm_h:.6f}')
    return lines


def process_split(image_paths, mask_index, out_images_dir, out_labels_dir, split_name):
    out_images_dir.mkdir(parents=True, exist_ok=True)
    out_labels_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped_no_mask = 0
    skipped_no_boxes = 0

    for img_path in tqdm(image_paths, desc=f'Converting {split_name}'):
        stem = img_path.stem.lower()
        if stem not in mask_index:
            skipped_no_mask += 1
            continue

        img = cv2.imread(str(img_path))
        if img is None:
            skipped_no_mask += 1
            continue
        h, w = img.shape[:2]

        lines = mask_to_yolo_lines(mask_index[stem], w, h)
        if not lines:
            skipped_no_boxes += 1
            continue

        dest_img = out_images_dir / img_path.name
        shutil.copy2(img_path, dest_img)

        label_path = out_labels_dir / (img_path.stem + '.txt')
        label_path.write_text('\n'.join(lines) + '\n')
        written += 1

    print(f'  [{split_name}] written={written}, skipped_no_mask={skipped_no_mask}, '
          f'skipped_no_boxes={skipped_no_boxes}')
    return written


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw-dir', required=True)
    parser.add_argument('--out-dir', required=True)
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    images_dir = raw_dir / 'Images'
    gt_dir = raw_dir / 'GT'
    train_src_dir = images_dir / 'Train'
    test_src_dir = images_dir / 'Test'

    if not train_src_dir.is_dir() or not test_src_dir.is_dir():
        print(f'ERROR: expected {train_src_dir} and {test_src_dir} to exist.')
        sys.exit(1)

    print('Indexing masks...')
    mask_index = build_mask_index(gt_dir)
    print(f'{len(mask_index)} masks indexed.\n')

    train_images_all = find_all_images(train_src_dir)
    test_images = find_all_images(test_src_dir)

    random.seed(RANDOM_SEED)
    shuffled = train_images_all.copy()
    random.shuffle(shuffled)
    n_val = int(len(shuffled) * VAL_FRACTION)
    val_images = shuffled[:n_val]
    train_images = shuffled[n_val:]

    print(f'Train/Train split: {len(train_images)} train, {len(val_images)} val '
          f'(from {len(train_images_all)} total Train images)')
    print(f'Test (held out):    {len(test_images)}\n')

    counts = {}
    counts['train'] = process_split(
        train_images, mask_index,
        out_dir / 'images' / 'train', out_dir / 'labels' / 'train', 'train'
    )
    counts['val'] = process_split(
        val_images, mask_index,
        out_dir / 'images' / 'val', out_dir / 'labels' / 'val', 'val'
    )
    counts['test'] = process_split(
        test_images, mask_index,
        out_dir / 'images' / 'test', out_dir / 'labels' / 'test', 'test'
    )

    data_yaml = {
        'path': str(out_dir),
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test',
        'nc': 1,
        'names': ['camouflaged_object'],
    }
    yaml_path = out_dir / 'data.yaml'
    with open(yaml_path, 'w') as f:
        yaml.dump(data_yaml, f, default_flow_style=False)

    print(f'\nWrote {yaml_path}')
    print(f'Final counts: {counts}')
    print('\nDone.')


if __name__ == '__main__':
    main()