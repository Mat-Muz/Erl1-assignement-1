import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from aruco_opencv_msg.msg import MarkerPose
from sensor_msgs.msg import Image
from sensor_msgs.msg import CameraInfo
import sys
import math


class RobotController(Node):

    

    def __init__(self):

        # --- 2. DECLARING MESSAGES ---
        # Instead of just declaring, we create the empty object instance here.
        self.marker_info = MarkerPose()
        self.image_info = Image()

        # --- 3. DECLARING VARIABLES ---
        self.marker_id = 0.0
        self.pose = 0.0
        self.orientation = 0.0

        super().__init__('robot_controller')

        self.subscription = self.create_subscription(MarkerPose, 'marker_pose', self.marker_callback, 10)
        self.subscription_image = self.create_subscription(Image, 'camera/image',self.image_callback, 10)
        self.publisher_msg = self.create_publisher(Custom, 'marker_image', 10)

        self.timer_ = self.create_timer(0.05, self.timer_callback)
        self.get_logger().info('Robot Controller Node has been started.')



    def marker_callback(self, msg):

        if len(msg.id) == 0:
            self.get_logger().info('No marker detected.')
            return

        self.marker_info = msg
        self.marker_id = self.marker_info.id
        self.pose = self.marker_info.position
        self.orientation = self.marker_info.orientation
        
        # Log the marker information
        self.get_logger().info(f'Marker ID: {self.marker_info.id}, Position: ({self.marker_info.position.x}, {self.marker_info.position.y}, {self.marker_info.position.z}), Orientation: ({self.marker_info.orientation.x}, {self.marker_info.orientation.y}, {self.marker_info.orientation.z}, {self.marker_info.orientation.w})')


    def image_callback(self, msg):

        self.image_info = msg



        # Log the image information
        self.get_logger().info(f'Received image with width: {msg.width}, height: {msg.height}, encoding: {msg.encoding}')

    def timer_callback(self):

        # Create a new message to publish
        msg = Custom()
        msg.id = self.marker_id
        msg.position = self.pose
        msg.orientation = self.orientation

        # Publish the message
        self.publisher_msg.publish(msg)
        self.get_logger().info(f'Published marker info to messages'))

def main(args=None):
    rclpy.init(args=args)
    robot_controller = RobotController()
    rclpy.spin(robot_controller)
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()   