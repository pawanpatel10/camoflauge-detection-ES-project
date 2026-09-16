"""
Train YOLO Model (Baseline or Knowledge Distillation Mode)
Executes YOLO training using Ultralytics API with customizable hyperparameters via Command-Line Arguments.
"""

import argparse
from ultralytics import YOLO

def main():
    parser = argparse.ArgumentParser(description="Train YOLO model for Camouflage Detection.")
    parser.add_argument('--data', required=True, help="Path to data.yaml dataset config file")
    parser.add_argument('--epochs', type=int, default=100, help="Number of training epochs (default: 100)")
    parser.add_argument('--imgsz', type=int, default=640, help="Input image resolution in pixels (default: 640)")
    parser.add_argument('--batch', type=int, default=16, help="Batch size for training (default: 16)")
    parser.add_argument('--workers', type=int, default=8, help="Number of dataloader worker processes (default: 8)")
    parser.add_argument('--project', required=True, help="Directory to save output runs (e.g., camo_runs)")
    parser.add_argument('--name', default='camo_yolo11n', help="Subfolder name for this specific training run")
    parser.add_argument('--weights', default='yolo11n.pt', help="Initial model weights (e.g. yolo11n.pt or pretrained path)")
    parser.add_argument('--distill-model', default=None, help="Path to Teacher weights (.pt) for Knowledge Distillation")
    args = parser.parse_args()

    train_kwargs = dict(
        data=args.data, 
        epochs=args.epochs, 
        imgsz=args.imgsz,
        batch=args.batch, 
        workers=args.workers, 
        project=args.project, 
        name=args.name,
        patience=20,    
        verbose=True,   
        plots=True     
    )

    if args.distill_model:
        train_kwargs['distill_model'] = args.distill_model
        print(f'\n=== Knowledge Distillation Mode Activated ===')
        print(f'Teacher Model : {args.distill_model}')
        print(f'Student Model : {args.weights}\n')

    results = YOLO(args.weights).train(**train_kwargs)

    print(f'\n--- Training Complete ---')
    print(f'Best weights saved to               : {args.project}/{args.name}/weights/best.pt')
    print(f'Accuracy metrics per epoch saved to  : {args.project}/{args.name}/results.csv')
    print(f'Training plots saved to              : {args.project}/{args.name}/results.png')

if __name__ == '__main__':
    main()