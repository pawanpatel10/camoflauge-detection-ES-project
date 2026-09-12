
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose
from cv_bridge import CvBridge
import cv2

from ultralytics import YOLO


class DetectorNode(Node):

    WEIGHTS_PATH = '/home/USERNAME/camo_ws/training/runs/camo_yolo11n/weights/best.pt'
    CONFIDENCE_THRESHOLD = 0.25
    CLASS_NAMES = ['camouflaged_object']

    def __init__(self):
        super().__init__('detector_node')
        self.declare_parameter('weights_path', self.WEIGHTS_PATH)
        weights_path = self.get_parameter('weights_path').get_parameter_value().string_value

        self.get_logger().info(f'Loading YOLO model from: {weights_path}')
        self.model = YOLO(weights_path)
        self.bridge = CvBridge()

        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10
        )
        self.annotated_pub = self.create_publisher(Image, '/camera/image_detected', 10)
        self.detections_pub = self.create_publisher(Detection2DArray, '/detections', 10)

        self.frame_count = 0
        self.last_fps_log_time = time.time()

        self.get_logger().info('Detector node ready, subscribed to /camera/image_raw')

    def image_callback(self, msg: Image):
        start_time = time.time()

        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        results = self.model.predict(
            cv_image, conf=self.CONFIDENCE_THRESHOLD, verbose=False
        )
        result = results[0]

        detection_array = Detection2DArray()
        detection_array.header = msg.header

        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])

            detection = Detection2D()
            detection.header = msg.header
            detection.bbox.center.position.x = (x1 + x2) / 2.0
            detection.bbox.center.position.y = (y1 + y2) / 2.0
            detection.bbox.size_x = x2 - x1
            detection.bbox.size_y = y2 - y1

            hypothesis = ObjectHypothesisWithPose()
            hypothesis.hypothesis.class_id = self.CLASS_NAMES[class_id]
            hypothesis.hypothesis.score = confidence
            detection.results.append(hypothesis)

            detection_array.detections.append(detection)

            self.get_logger().info(
                f'Detected: {self.CLASS_NAMES[class_id]}  '
                f'Confidence: {confidence:.2f}  '
                f'Bounding box: {x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f}'
            )

        self.detections_pub.publish(detection_array)

        annotated_frame = result.plot()
        annotated_msg = self.bridge.cv2_to_imgmsg(annotated_frame, encoding='bgr8')
        annotated_msg.header = msg.header
        self.annotated_pub.publish(annotated_msg)

        self.frame_count += 1
        elapsed_since_log = time.time() - self.last_fps_log_time
        if elapsed_since_log >= 5.0:
            fps = self.frame_count / elapsed_since_log
            inference_ms = (time.time() - start_time) * 1000
            self.get_logger().info(
                f'Detection FPS (5s window): {fps:.2f}, last inference time: {inference_ms:.1f} ms'
            )
            self.frame_count = 0
            self.last_fps_log_time = time.time()


def main(args=None):
    rclpy.init(args=args)
    node = DetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()