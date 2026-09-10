from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess


def generate_launch_description():
    teleop = ExecuteProcess(
        cmd=[
            'ros2', 'run', 'teleop_twist_keyboard', 'teleop_twist_keyboard',
            '--ros-args', '--remap', '/cmd_vel:=/cmd_vel_raw'
        ],
        output='screen',
        prefix='xterm -e'
    )

    return LaunchDescription([teleop])