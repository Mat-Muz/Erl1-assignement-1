# Setup Instructions for Group Members

Follow these steps to clone the repository and set up your local ROS 2 workspace correctly.

### 1. Create the Workspace

If you haven't already, create a standard ROS 2 workspace and navigate into its `src` folder:

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

```

### 2. Clone the Repository

Clone our group repository directly into the `src` folder (replace the URL with our actual GitHub link):

```bash
git clone https://github.com/YourUsername/YourNewRepo.git erl1

```

### 3. Build the Package

Navigate back to the root of the workspace to build the package, then source the overlay:

```bash
cd ~/ros2_ws
colcon build --packages-select erl1
source install/setup.bash

```

### 4. Getting Future Updates

Whenever someone in the group pushes new code, update your local copy by running:

```bash
cd ~/ros2_ws/src/erl1
git pull origin main

```

*(Remember to run `colcon build` again in `~/ros2_ws` if there are new dependencies or CMake changes!)*