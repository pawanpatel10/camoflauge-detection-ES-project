"""
Evaluate Trained YOLO Model on Held-out Test Set
Loads a trained checkpoint (.pt) and evaluates box detection metrics (mAP@50, mAP@50-95, inference speed).
"""

import argparse
from ultralytics import YOLO

def main():
    parser = argparse.ArgumentParser(description="Evaluate YOLO model on test set.")
    parser.add_argument('--weights', required=True, help="Path to trained model weights (e.g. best.pt)")
    parser.add_argument('--data', required=True, help="Path to data.yaml dataset config file")
    args = parser.parse_args()

    print(f"Loading model from {args.weights}...")
    model = YOLO(args.weights)

    print("\nEvaluating on the held-out TEST set...")
    metrics = model.val(data=args.data, split='test')

    print("\n" + "="*40)
    print("       TEST SET EVALUATION RESULTS")
    print("="*40)
    print(f"mAP@50         : {metrics.box.map50:.4f}")
    print(f"mAP@50-95      : {metrics.box.map:.4f}")
    print(f"Inference Time : {metrics.speed['inference']:.2f} ms per image")
    print("="*40)

if __name__ == '__main__':
    main()

