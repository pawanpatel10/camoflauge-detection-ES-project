from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():
    teleop = ExecuteProcess(
        cmd=[
            'ros2', 'run', 'teleop_twist_keyboard', 'teleop_twist_keyboard',
            '--ros-args', '--remap', '/cmd_vel:=/cmd_vel_raw'
        ],
        output='screen',
        prefix='xterm -e'
    )

    safety = Node(
        package='camo_control',
        executable='safety_node',
        output='screen'
    )

    return LaunchDescription([teleop, safety])