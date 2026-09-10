import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')
    camo_gazebo_share = get_package_share_directory('camo_gazebo')
    camo_description_share = get_package_share_directory('camo_description')

    world_path = os.path.join(camo_gazebo_share, 'worlds', 'camo_world.sdf')
    xacro_path = os.path.join(camo_description_share, 'urdf', 'camo_robot.urdf.xacro')
    bridge_config = os.path.join(camo_gazebo_share, 'config', 'bridge.yaml')

    # Process Xacro file directly in Python (immune to path spaces)
    doc = xacro.process_file(xacro_path)
    robot_description = doc.toxml()

    # 1. Start Gazebo Simulator with world
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r "{world_path}"'}.items()
    )

    # 2. Robot State Publisher Node
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}]
    )

    # 3. Spawn Robot Entity into Gazebo
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-string', robot_description,
            '-name', 'camo_robot',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.15'
        ],
        output='screen'
    )

    # 4. ROS-Gazebo Bridge Node
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_config}],
        output='screen'
    )

    return LaunchDescription([
        gz_sim,
        robot_state_publisher,
        spawn_robot,
        bridge,
    ])
