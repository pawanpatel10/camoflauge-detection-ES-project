import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    gz_sim_share = get_package_share_directory('ros_gz_sim')
    camo_gazebo_share = get_package_share_directory('camo_gazebo')
    world_path = os.path.join(camo_gazebo_share, 'worlds', 'camo_world.sdf')

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gz_sim_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_path}'}.items()
    )

    return LaunchDescription([gz_sim])