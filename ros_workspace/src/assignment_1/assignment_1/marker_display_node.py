import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from aruco_opencv_msgs.msg import MarkerPose
from sensor_msgs.msg import Image
from sensor_msgs.msg import CameraInfo
from custom_msgs.msg import Box
from cv_bridge import CvBridge
from std_msgs.msg import Bool
import sys
import math
import cv2

class RobotController(Node):
   

    def __init__(self):

        # --- 2. DECLARING MESSAGES ---
        # Instead of just declaring, we create the empty object instance here.
        self.marker_info = MarkerPose()
        self.image_info = CameraInfo()
        self.raw_image  = Image()
        self.custom_msg = Box()
        self.bridge = CvBridge()


        # --- 3. DECLARING VARIABLES ---
        self.marker_id = 0.0
        self.pose = 0.0
        self.orientation = 0.0
        self.k_matrix = 0.0
        self.frame_id: str = "camera_color_optical_frame"
        self.notify = True
        self.x_px = 0.0
        self.y_px = 0.0
        self.radius = 0.0
        self.z_depth = 0.0
        

        super().__init__('robot_controller')

        self.subscription = self.create_subscription(MarkerPose, 'marker_pose', self.marker_callback, 10)
        self.subscription_intrinsic = self.create_subscription(CameraInfo, 'camera/camera_info',self.intrinsic_callback, 10)
        self.subscription_marker_ingo = self.create_subscription(Bool, 'target_reached',self.target_reached_callback, 10)
        self.subscription_image = self.create_subscription(Image, 'camera/image',self.image_callback, 10)

        self.publisher_marker = self.create_publisher(Image, 'marker_image', 10)
        self.publisher_info = self.create_publisher(Box, 'custom_msg', 10)

        self.timer_ = self.create_timer(0.05, self.timer_callback)
        self.get_logger().info('Robot Controller Node has been started.')


    def marker_callback(self, msg):

        self.get_logger().info('Marker information received.')
        if len(msg.id) == 0:
            self.get_logger().info('No marker detected.')
            return

        self.marker_info = msg
        self.marker_id = self.marker_info.id
        self.pose = self.marker_info.position
        self.orientation = self.marker_info.orientation
        
        # Log the marker information
        self.get_logger().info(f'Marker ID: {self.marker_info.id}, Position: ({self.marker_info.position.x}, {self.marker_info.position.y}, {self.marker_info.position.z}), Orientation: ({self.marker_info.orientation.x}, {self.marker_info.orientation.y}, {self.marker_info.orientation.z}, {self.marker_info.orientation.w})')


    def target_reached_callback(self, Boolean):
        if Boolean.data== True:
            self.notify = True
        else:
            self.notify = False

    def intrinsic_callback(self, msg):

        self.image_info = msg
        self.k_matrix = self.image_info.k

        self.get_logger().info(f'Intrinsic matrix for camera')

    def timer_callback(self):

        self.get_logger().info(f'starting time callback')
        self.x_px = self.k_matrix[0,0]*self.pose.x/self.pose.z + self.k_matrix[0,2]
        self.y_px = self.k_matrix[1,1]*self.pose.y/self.pose.z + self.k_matrix[1,2]
        self.radius = (self.x_px*sqrt(2))/2
        self.z_depth = self.pose.z
        
        # Info needed for second part of assignment 
        self.custom_msg.id = int(self.marker_id)
        self.custom_msg.cy = int(self.x_px/2)
        self.custom_msg.cy = int(self.y_px/2)
        self.custom_msg.d = int(self.z_depth)

        self.get_logger().info(f'about to publish from time callback')
        self.publisher_msg.publish(self.custom_msg)
        self.get_logger().info(f'Published custom message')
        

    def image_callback(self, msg):
        self.raw_image = msg
        self.get_logger().info('Image received.')

        # convert ROS Image message to OpenCV image
        img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Publishing on the marker visualization topic
        # Ever time the robot is near the marker then we will publish the red circle and the marker id on the image
        # Will be visualized in rviz2
        if self.notify:

            cx = int(self.x_px)
            cy = int(self.y_px)
            r = int(self.radius)
            #Drawing a circle around the marker and displaying the marker id on the image
            cv2.circle(img, (cx, cy), r, (0, 0, 255), 2)
            cv2.putText(img,f"id {self.marker_id}",(cx - r, cy - r - 10),cv2.FONT_HERSHEY_SIMPLEX,1.0,(0, 0, 255),3,)

            out_msg = self.bridge.cv2_to_imgmsg(img, encoding='bgr8')
            out_msg.header = msg.header   
            
            # Publish the message
            self.publisher_marker.publish(out_msg)
            self.get_logger().info(f'Reached Target and drawn circle')

def main(args=None):
    rclpy.init(args=args)
    robot_controller = RobotController()
    rclpy.spin(robot_controller)
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()   