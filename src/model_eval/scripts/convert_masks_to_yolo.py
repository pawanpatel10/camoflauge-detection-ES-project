"""
Convert Binary Mask Images (Segmentation Dataset) into YOLO Bounding Box Format (.txt)
Organizes data into train/val/test splits and generates data.yaml configuration.
"""

import argparse, random, shutil, sys
from pathlib import Path
import cv2, yaml

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.bmp'}

MIN_AREA_FRAC = 0.0005


def mask_to_yolo(mask_path, w, h):
    """
    Reads a binary mask image, detects contours, and converts object boundaries into normalized YOLO format lines.
    
    YOLO Format: <class_id> <x_center> <y_center> <width> <height> (all normalized between 0.0 and 1.0)
    """
    mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
    if mask is None: 
        return []
    
    if mask.shape[1] != w or mask.shape[0] != h:
        mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)
        
    _, binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    lines = []
    for c in contours:
        if cv2.contourArea(c) < (MIN_AREA_FRAC * w * h): 
            continue
            
        rx, ry, rw, rh = cv2.boundingRect(c)
        
        x_center = (rx + rw / 2) / w
        y_center = (ry + rh / 2) / h
        norm_w = rw / w
        norm_h = rh / h
        
        lines.append(f"0 {x_center:.6f} {y_center:.6f} {norm_w:.6f} {norm_h:.6f}")
        
    return lines


def process(paths, m_idx, out_dir, split):
    """
    Processes a list of image paths for a specific split ('train', 'val', or 'test'),
    copies images to out_dir/images/<split>/, and writes YOLO labels to out_dir/labels/<split>/.
    """
    i_dir = out_dir / 'images' / split
    l_dir = out_dir / 'labels' / split
    i_dir.mkdir(parents=True, exist_ok=True)
    l_dir.mkdir(parents=True, exist_ok=True)
    
    for p in paths:
        if p.stem.lower() not in m_idx: 
            continue
            
        img = cv2.imread(str(p))
        if img is None: 
            continue
            
        lines = mask_to_yolo(m_idx[p.stem.lower()], img.shape[1], img.shape[0])
        
        if lines:
            shutil.copy2(p, i_dir / p.name)  # Copy image to images/<split>/
            (l_dir / f"{p.stem}.txt").write_text('\n'.join(lines) + '\n')  # Save .txt label


def main():
    parser = argparse.ArgumentParser(description="Convert raw dataset masks into YOLO format.")
    parser.add_argument('--raw-dir', required=True, help="Path to raw dataset root folder")
    parser.add_argument('--out-dir', required=True, help="Path to save processed YOLO dataset")
    args = parser.parse_args()

    raw, out = Path(args.raw_dir).resolve(), Path(args.out_dir).resolve()

    if not (raw / 'GT').exists():
        subdirs = [d for d in raw.iterdir() if d.is_dir() and (d / 'GT').exists()]
        if subdirs:
            raw = subdirs[0]
            print(f"Auto-detected dataset root: {raw}")
        else:
            print(f"ERROR: Could not find 'GT' folder in {raw} or any subdirectory.")
            sys.exit(1)

    m_idx = {p.stem.lower(): p for p in (raw / 'GT').rglob('*') if p.suffix.lower() in IMAGE_EXTS}
    
    train_imgs = [p for p in (raw / 'Images' / 'Train').rglob('*') if p.suffix.lower() in IMAGE_EXTS]
    test_imgs = [p for p in (raw / 'Images' / 'Test').rglob('*') if p.suffix.lower() in IMAGE_EXTS]

    random.seed(42)
    random.shuffle(train_imgs)
    
    n_val = int(len(train_imgs) * 0.15)
    
    process(train_imgs[n_val:], m_idx, out, 'train')
    process(train_imgs[:n_val], m_idx, out, 'val')
    process(test_imgs, m_idx, out, 'test')

    with open(out / 'data.yaml', 'w') as f:
        yaml.dump({
            'path': str(out),
            'train': 'images/train',
            'val': 'images/val',
            'test': 'images/test',
            'nc': 1,
            'names': ['camouflaged_object']
        }, f)
        
    print(f"Conversion complete! YOLO dataset saved at: {out}")


if __name__ == '__main__':
    main()