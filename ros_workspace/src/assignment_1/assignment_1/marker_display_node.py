import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from aruco_opencv_msg.msg import MarkerPose
from sensor_msgs.msg import Image
from sensor_msgs.msg import CameraInfo
from visualization_msgs.msg import Marker, MarkerArray
import sys
import math


class RobotController(Node):
   

    def __init__(self):

        # --- 2. DECLARING MESSAGES ---
        # Instead of just declaring, we create the empty object instance here.
        self.marker_info = MarkerPose()
        self.image_info = Image()
        self.marker_array = MarkerArray()

        # --- 3. DECLARING VARIABLES ---
        self.marker_id = 0.0
        self.pose = 0.0
        self.orientation = 0.0
        self.k_matrix = 0.0
        self.frame_id: str = "camera_color_optical_frame"
        

        super().__init__('robot_controller')

        self.subscription = self.create_subscription(MarkerPose, 'marker_pose', self.marker_callback, 10)
        self.subscription_image = self.create_subscription(Image, 'camera/image',self.image_callback, 10)
        self.publisher_msg = self.create_publisher(Custom, 'marker_image', 10)
        self.publisher_marker = self.create_publisher(MarkerArray, 'visualize_marker', 10)

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

        self.k_matrix = msg.k

        # Log the image information
        self.get_logger().info(f'Recieved intrinsic matrix for raw image')

    def timer_callback(self):

        self.x_px = self.k_matrix[0,0]*self.pose.x/self.pose.z + self.k_matrix[0,2]
        self.y_px = self.k_matrix[1,1]*self.pose.y/self.pose.z + self.k_matrix[1,2]
        self.radius = (self.x_px*sqrt(2))/2
        self.z_depth = self.pose.z
        
        # Create a new message to publish
        msg = Custom()
        msg.id = self.marker_id
        msg.x_px = self.x_px
        msg.y_px = self.y_px

        #Drawing a circle around the marker and displaying the marker id on the image
        cv2.circle(img, (self.x_px, self.y_px), self.radius, (0, 255, 0), 2)
        cv2.putText(img,f"id {self.marker_id}",(self.x_px - self.radius, self.y_px - self.radius - 10),cv2.FONT_HERSHEY_SIMPLEX,1.0,(0, 255, 0),3,)

       
        stamp = self.get_clock().now().to_msg()

        sphere = Marker()
        sphere.header.frame_id = self.frame_id
        sphere.header.stamp = stamp
        sphere.ns = "marker_spheres"
        sphere.id = int(self.marker_id)
        sphere.type = Marker.SPHERE
        sphere.action = Marker.ADD

        # Position (meters)
        sphere.pose.position.x = float(self.pose.x)
        sphere.pose.position.y = float(self.pose.y)
        sphere.pose.position.z = float(self.pose.z)
        sphere.pose.orientation.w = 1.0  # MUST be 1.0 (Unit quaternion)

        # Size in meters (5 cm sphere)
        sphere.scale.x = 0.05
        sphere.scale.y = 0.05
        sphere.scale.z = 0.05

        # Color: Solid Green
        sphere.color.r = 0.0
        sphere.color.g = 1.0
        sphere.color.b = 0.0
        sphere.color.a = 1.0  # Alpha must be > 0 to be visible

        # Automatically expire marker if not re-detected in 0.5s
        sphere.lifetime.sec = 0
        sphere.lifetime.nanosec = 500000000

        # -------------------------------------------------------------
        # 2. TEXT MARKER (Floating ID Label)
        # -------------------------------------------------------------
        text = Marker()
        text.header.frame_id = self.frame_id
        text.header.stamp = stamp
        text.ns = "marker_labels"
        text.id = int(self.marker_id) + 10000  # Unique ID for array
        text.type = Marker.TEXT_VIEW_FACING
        text.action = Marker.ADD

        # In ROS optical frame (X-Right, Y-Down, Z-Forward):
        # Subtracting from Y moves the text UP in physical space
        text.pose.position.x = float(self.pose.x)
        text.pose.position.y = float(self.pose.y) - 0.06  
        text.pose.position.z = float(self.pose.z) 
        text.pose.orientation.w = 1.0

        text.text = f"ID: {self.marker_id}"
        text.scale.z = 0.04  # Text height in meters (4 cm)

        # Color: Solid White
        text.color.r = 1.0
        text.color.g = 1.0
        text.color.b = 1.0
        text.color.a = 1.0
        text.lifetime = sphere.lifetime

        # Package and publish
        marker_array.markers = [sphere, text]
        self.marker_pub.publish(marker_array)

        # Publish the message
        self.publisher_msg.publish(msg)
        self.get_logger().info(f'Published marker info to messages')

def main(args=None):
    rclpy.init(args=args)
    robot_controller = RobotController()
    rclpy.spin(robot_controller)
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()   