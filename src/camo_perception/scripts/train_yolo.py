import argparse
from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', required=True, help='Path to data.yaml')
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--batch', type=int, default=16)
    parser.add_argument('--project', required=True)
    parser.add_argument('--name', default='camo_yolo11n')
    parser.add_argument('--weights', default='yolo11n.pt',
                         help='Pretrained weights to fine-tune from')
    args = parser.parse_args()

    model = YOLO(args.weights)  

    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=args.project,
        name=args.name,
        patience=20,          
        device='cpu',         
        verbose=True,
    )

    print('\nTraining complete.')
    print(f'Best weights saved under: {args.project}/{args.name}/weights/best.pt')


if __name__ == '__main__':
    main()