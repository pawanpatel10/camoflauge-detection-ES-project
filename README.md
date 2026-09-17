# Camouflage Detection ROS 2 Project

This workspace contains the ROS 2 packages for the camouflage-detection simulation:

- `camo_bringup`: top-level launch package
- `camo_control`: control package scaffold
- `camo_description`: robot description package scaffold
- `camo_gazebo`: Gazebo Sim world and model assets
- `camo_perception`: perception package scaffold

## Prerequisites

The commands below assume Ubuntu 24.04 in WSL and ROS 2 Jazzy. If a different ROS 2 distribution is installed, replace `jazzy` in the commands with that distribution name.

Install WSL from an Administrator PowerShell if WSL is not installed:

```powershell
wsl --install
```

For an existing WSL installation, update WSL:

```powershell
wsl.exe --update
```

Check the installed distributions and their WSL versions:

```powershell
wsl.exe --list --verbose
```

Sources:

- [Microsoft: Install WSL](https://learn.microsoft.com/en-us/windows/wsl/install)
- [Microsoft: Run Linux GUI apps with WSL](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps)

Install ROS 2 Jazzy by following the official Ubuntu Debian-package instructions:

- [ROS 2 Jazzy: Ubuntu installation](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)

Install the workspace tools:

```bash
sudo apt update
sudo apt install python3-colcon-common-extensions python3-rosdep
```

The ROS 2 installation guide is the source for ROS 2 system packages. The `colcon` package provides the workspace build command, and `rosdep` installs dependencies declared by ROS package manifests.

## Install Package Dependencies

Open Ubuntu/WSL and move to the workspace root:

```bash
cd ~/camo_ws
```

Load the system ROS 2 environment:

```bash
source /opt/ros/jazzy/setup.bash
```

Initialize `rosdep` once per machine. If it was already initialized, skip `sudo rosdep init` and run only `rosdep update`:

```bash
sudo rosdep init
rosdep update
```

Install all dependencies declared by the packages under `src`:

```bash
rosdep install --from-paths src --ignore-src -r -y
```

Command details:

- `--from-paths src`: inspect package manifests under `src`.
- `--ignore-src`: do not try to install packages that are part of this workspace.
- `-r`: continue when a dependency cannot be resolved.
- `-y`: automatically confirm apt installation prompts.

The dependencies are declared in each package's `package.xml`, including `ament_python`, `ament_cmake`, `rclpy`, `ros_gz_sim`, `ros_gz_bridge`, and `ros_gz_image`.

Source:

- [ROS 2 Jazzy: Using rosdep](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Rosdep.html)

## Build the Workspace

From the workspace root, after loading ROS 2:

```bash
cd ~/camo_ws
source /opt/ros/jazzy/setup.bash
colcon build
```

`colcon build` discovers the packages in `src`, builds them in dependency order, and creates the `build`, `install`, and `log` directories.

For a clean rebuild, remove generated directories first:

```bash
rm -rf build install log
colcon build
```

Source:

- [colcon: Quick start](https://colcon.readthedocs.io/en/released/user/quick-start.html)
- [ROS 2: Creating a workspace](https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Creating-A-Workspace/Creating-A-Workspace.html)

## Load the Built Workspace

After a successful build, load the local workspace overlay:

```bash
source ~/camo_ws/install/setup.bash
```

This makes the packages built in this workspace discoverable by ROS 2 commands such as `ros2 pkg list` and `ros2 launch`.

Source:

- [ROS 2: Configuring the environment](https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Configuring-ROS2-Environment.html)
- [colcon: Quick start](https://colcon.readthedocs.io/en/released/user/quick-start.html)

## Run Gazebo

Launch the current Gazebo Sim world:

```bash
cd ~/camo_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch camo_gazebo world.launch.py
```

The launch file finds `camo_world.sdf` from the installed `camo_gazebo` package and includes the `ros_gz_sim` launch file. The `-r` argument starts the simulation running immediately.

The current world contains the ground plane, lighting, physics and sensor systems, rocks, and trees. The robot description, control nodes, and perception nodes are not yet implemented.

Sources:

- [Gazebo Sim: ROS 2 integration](https://gazebosim.org/docs/gz-sim/latest/ros2_integration/)
- [ROS 2: Gazebo simulator tutorial](https://docs.ros.org/en/jazzy/Tutorials/Advanced/Simulators/Gazebo/Gazebo.html)

## Gazebo GUI Troubleshooting on WSL

If Gazebo exits immediately because of graphics rendering, try software rendering:

```bash
cd ~/camo_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
LIBGL_ALWAYS_SOFTWARE=1 ros2 launch camo_gazebo world.launch.py
```

`LIBGL_ALWAYS_SOFTWARE=1` is a temporary environment setting. It forces OpenGL/Mesa to use CPU rendering instead of the GPU. It is a troubleshooting option, not a project installation requirement.

WSL GUI applications require WSL 2 and WSLg support. GPU drivers may also be required for hardware-accelerated rendering.

Source:

- [Microsoft: Run Linux GUI apps with WSL](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps)

## Run from PowerShell

The equivalent command from Windows PowerShell is:

```powershell
wsl.exe -d Ubuntu-24.04 bash -lc "cd /home/pawan/camo_ws && source /opt/ros/jazzy/setup.bash && colcon build && source install/setup.bash && ros2 launch camo_gazebo world.launch.py"
```

This enters the `Ubuntu-24.04` WSL distribution and executes the normal Linux setup, build, and launch commands there.

## Command Summary

| Command | Purpose |
| --- | --- |
| `sudo apt update` | Refresh Ubuntu package metadata |
| `sudo apt install ...` | Install Ubuntu tools and packages |
| `source /opt/ros/jazzy/setup.bash` | Load the system ROS 2 installation |
| `rosdep install ...` | Install dependencies declared in `package.xml` files |
| `colcon build` | Build this ROS 2 workspace |
| `source install/setup.bash` | Load this workspace's built packages |
| `ros2 launch camo_gazebo world.launch.py` | Start the Gazebo simulation |
| `LIBGL_ALWAYS_SOFTWARE=1 ...` | Run with software OpenGL rendering |
| `wsl.exe -d Ubuntu-24.04 ...` | Run Linux commands from Windows PowerShell |

## Open-Source Sources and References for the Gazebo Files

The files in `src/camo_gazebo` are based on the official open-source ROS 2 and Gazebo patterns used in public examples and upstream repositories. These are source references for the structure and conventions used here, not proprietary content.

- `src/camo_gazebo/CMakeLists.txt`: standard ROS 2 `ament_cmake` package structure used by public ROS examples. Source: [ROS 2 examples repo](https://github.com/ros2/examples), [ROS 2 documentation repo](https://github.com/ros2/ros2_documentation).
- `src/camo_gazebo/package.xml`: ROS 2 package manifest format defined by the official package specification. Source: [ROS 2 package format docs](https://docs.ros.org/en/jazzy/Concepts/Package-Format.html), [ROS 2 examples repo](https://github.com/ros2/examples).
- `src/camo_gazebo/launch/world.launch.py`: launch pattern from the official `ros_gz` project. Source: [ros_gz repository](https://github.com/gazebosim/ros_gz), [ros_gz_sim launch directory](https://github.com/gazebosim/ros_gz/tree/ros2/ros_gz_sim/launch).
- `src/camo_gazebo/worlds/camo_world.sdf`: SDF world structure from the official Gazebo ecosystem. Source: [SDFormat repo](https://github.com/osrf/sdformat), [gz-sim examples](https://github.com/gazebosim/gz-sim/tree/gz-sim9/examples).
- `src/camo_gazebo/models/camo_decal/model.config`: standard model metadata pattern used by open-source Gazebo model collections. Source: [Gazebo model database](https://github.com/osrf/gazebo_models), [Gazebo model structure docs](https://github.com/osrf/gazebo_models#readme).
- `src/camo_gazebo/models/camo_decal/model.sdf`: SDF model structure used in public Gazebo model examples. Source: [SDFormat repo](https://github.com/osrf/sdformat), [Gazebo model database](https://github.com/osrf/gazebo_models).

The project follows upstream, openly available ROS 2 and Gazebo conventions for package structure, launch files, and SDF model definitions.

