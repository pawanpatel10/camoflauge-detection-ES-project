#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time


class SafetyNode(Node):


    MAX_LINEAR_VEL = 0.5   # m/s
    MAX_ANGULAR_VEL = 1.5  # rad/s
    COMMAND_TIMEOUT_SEC = 0.5
    WATCHDOG_PERIOD_SEC = 0.1

    def __init__(self):
        super().__init__('safety_node')

        self.last_command_time = self.get_clock().now()
        self.last_published_was_zero = True

        self.subscription = self.create_subscription(
            Twist, '/cmd_vel_raw', self.command_callback, 10
        )
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        self.watchdog_timer = self.create_timer(
            self.WATCHDOG_PERIOD_SEC, self.watchdog_callback
        )

        self.get_logger().info(
            f'Safety node started. Max linear={self.MAX_LINEAR_VEL} m/s, '
            f'max angular={self.MAX_ANGULAR_VEL} rad/s, '
            f'timeout={self.COMMAND_TIMEOUT_SEC}s'
        )

    def clamp(self, value, limit):
        if value > limit:
            return limit
        if value < -limit:
            return -limit
        return value

    def command_callback(self, msg: Twist):
        clamped = Twist()
        clamped.linear.x = self.clamp(msg.linear.x, self.MAX_LINEAR_VEL)
        clamped.angular.z = self.clamp(msg.angular.z, self.MAX_ANGULAR_VEL)

        if abs(msg.linear.x) > self.MAX_LINEAR_VEL or abs(msg.angular.z) > self.MAX_ANGULAR_VEL:
            self.get_logger().warn(
                f'Clamped command: requested linear.x={msg.linear.x:.2f}, '
                f'angular.z={msg.angular.z:.2f} -> published '
                f'linear.x={clamped.linear.x:.2f}, angular.z={clamped.angular.z:.2f}'
            )

        self.publisher.publish(clamped)
        self.last_command_time = self.get_clock().now()
        self.last_published_was_zero = (clamped.linear.x == 0.0 and clamped.angular.z == 0.0)

    def watchdog_callback(self):
        elapsed = (self.get_clock().now() - self.last_command_time).nanoseconds / 1e9
        if elapsed > self.COMMAND_TIMEOUT_SEC and not self.last_published_was_zero:
            stop_msg = Twist()
            self.publisher.publish(stop_msg)
            self.last_published_was_zero = True
            self.get_logger().info(
                f'No command received for {elapsed:.2f}s — publishing emergency stop.'
            )


def main(args=None):
    rclpy.init(args=args)
    node = SafetyNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()