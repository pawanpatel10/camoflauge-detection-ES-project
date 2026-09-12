#!/usr/bin/env python3
"""
Draws YOLO-format label boxes back onto their source images, for
visually confirming the mask-to-bbox conversion is correct.

Run:
    python3 visualize_labels.py --dataset-dir ~/camo_ws/dataset/yolo \
        --split train --num-samples 12 \
        --out-dir ~/camo_ws/results/label_sanity_check
"""

import argparse
import random
from pathlib import Path

import cv2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset-dir', required=True)
    parser.add_argument('--split', default='train', choices=['train', 'val', 'test'])
    parser.add_argument('--num-samples', type=int, default=12)
    parser.add_argument('--out-dir', required=True)
    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir).expanduser().resolve()
    images_dir = dataset_dir / 'images' / args.split
    labels_dir = dataset_dir / 'labels' / args.split
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    image_paths = sorted(images_dir.glob('*'))
    random.seed(7)
    sample = random.sample(image_paths, min(args.num_samples, len(image_paths)))

    for img_path in sample:
        label_path = labels_dir / (img_path.stem + '.txt')
        if not label_path.exists():
            continue

        img = cv2.imread(str(img_path))
        h, w = img.shape[:2]

        for line in label_path.read_text().strip().splitlines():
            cls, cx, cy, bw, bh = map(float, line.split())
            x1 = int((cx - bw / 2) * w)
            y1 = int((cy - bh / 2) * h)
            x2 = int((cx + bw / 2) * w)
            y2 = int((cy + bh / 2) * h)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        out_path = out_dir / img_path.name
        cv2.imwrite(str(out_path), img)

    print(f'Wrote {len(sample)} annotated sample images to {out_dir}')


if __name__ == '__main__':
    main()