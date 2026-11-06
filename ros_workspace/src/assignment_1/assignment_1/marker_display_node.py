import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from aruco_opencv_msgs.msg import MarkerPose
from aruco_opencv_msgs.msg import ArucoDetection
from sensor_msgs.msg import Image
from sensor_msgs.msg import CameraInfo
from custom_msgs.msg import Box
from cv_bridge import CvBridge
from std_msgs.msg import Bool
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from math import sqrt
import threading
import sys
import math
import cv2

class RobotController(Node):
   

    def __init__(self):


        # --- 2. DECLARING MESSAGES ---
        # Instead of just declaring, we create the empty object instance here.
        self.marker_info = ArucoDetection()
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

        # 2D position of the marker in image frame
        self.x_px = 0.0
        self.y_px = 0.0
        self.radius = 0.0
        self.z_depth = 0.0

        #3D position of the marker in camera frame
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.first_marker = []      

        super().__init__('robot_controller')

        #Multi-threaded executor to handle multiple callbacks simultaneously
        # self._cb_group = ReentrantCallbackGroup()
        # self._lock = threading.Lock()

        self.subscription = self.create_subscription(ArucoDetection, 'aruco_detections', self.aruco_callback, 10)
        self.subscription_intrinsic = self.create_subscription(CameraInfo, 'camera/camera_info',self.intrinsic_callback, 10)
        self.subscription_marker_ingo = self.create_subscription(Bool, 'target_reached',self.target_reached_callback, 10)
        self.subscription_image = self.create_subscription(Image, 'camera/image',self.image_callback, 10)

        self.publisher_marker = self.create_publisher(Image, 'marker_image', 10)
        self.publisher_msg = self.create_publisher(Box, 'custom_msg', 10)

        self.timer_ = self.create_timer(0.05, self.timer_callback)
        self.get_logger().info('Robot Controller Node has been started.')


    def aruco_callback(self, msg):

        self.marker_info = msg

        #only registers the marker detected when the robot is near the marker (target_reached topic is True)
        if (self.notify == True) and (len(self.marker_info.markers) > 0):

            self.first_marker = self.marker_info.markers[0]
            self.marker_id = self.first_marker.marker_id       

            # 3d position of the marker in camera frame               
            self.x = self.first_marker.pose.position.x
            self.y = self.first_marker.pose.position.y
            self.z = self.first_marker.pose.position.z
            self.orientation = self.first_marker.pose.orientation               # x, y, z, w
            self.get_logger().info(f'Marker information received.')


            

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
        marker_size = 0.2

       # with self._lock:
        if getattr(self, 'k_matrix', None) is None or getattr(self, 'z', 0.0) == 0.0:
            return

        self.x_px = self.k_matrix[0,0]*self.x/self.z + self.k_matrix[0,2]
        self.y_px = self.k_matrix[1,1]*self.y/self.z + self.k_matrix[1,2]
        self.radius = (marker_size*sqrt(2)/2)*self.k_matrix[0,0]/self.z
        self.z_depth = self.z
    
        # Info needed for second part of assignment 
        self.custom_msg.id = int(self.marker_id)
        self.custom_msg.cx = int(self.x_px)
        self.custom_msg.cy = int(self.y_px)
        self.custom_msg.d = int(self.z_depth)

        self.publisher_msg.publish(self.custom_msg)
        self.get_logger().info(f'Published custom message')


    def image_callback(self, msg):

        self.get_logger().info('Image received.')

        # convert ROS Image message to OpenCV image
        img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        #with self._lock:
        # Publishing on the marker visualization topic
        # Ever time the robot is near the marker then we will publish the red circle and the marker id on the image
        # Will be visualized in rviz2
        marker_cx = int(self.x_px)
        marker_cy = int(self.y_px)
        r = int(self.radius)
                
        if self.notify:   
            #Drawing a circle around the marker and displaying the marker id on the image
            cv2.circle(img, (marker_cx,marker_cy ), r, (0, 0, 255), 2)
            cv2.putText(img,f"id {self.marker_id}",(marker_cx - r, marker_cy - r - 10),cv2.FONT_HERSHEY_SIMPLEX,1.0,(0, 0, 255),3,)

        out_msg = self.bridge.cv2_to_imgmsg(img, encoding='bgr8')
        out_msg.header = msg.header   
            
        # Publish the message 
        self.publisher_marker.publish(out_msg)
        self.get_logger().info(f'Reached Target and drawn circle')
        

    

def main(args=None):
    rclpy.init(args=args)
    robot_controller = RobotController()
    rclpy.spin(robot_controller)

    # executor = MultiThreadedExecutor()
    # executor.add_node(robot_controller)
    # executor.spin()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()   