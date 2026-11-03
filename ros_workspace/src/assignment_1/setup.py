from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'assignment_1'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        # --- ADD THIS BLOCK ---
        # This tells ROS: "Take all .launch.py files from the 'launch' folder
        # and copy them to the installed share folder."
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        # ----------------------
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='root@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'robot_controller_node = assignment_1.marker_display_node:main',
        ],
    },
)
