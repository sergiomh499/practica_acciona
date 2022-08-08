#!/usr/bin/env python  
# import roslib
# roslib.load_manifest('learning_tf')
import rospy
import math
import tf
import geometry_msgs.msg
import turtlesim.srv
import random
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist

distance_tolerance = 0.5

class Turtle:
    def __init__(self):
        # initialize variables
        self.pose = Pose()
        self.pose.x = random.uniform(1, 9)
        self.pose.y = random.uniform(1, 9)
        self.follower = False # is not a follower turtle
        self.rate = rospy.Rate(10.0)

    def spawn(self, turtle_number):
        # define turtle propierties
        self.turtle_number = turtle_number
        self.turtle_name = 'turtle' + str(self.turtle_number)
        # call turtlesim service to spawn turtle
        rospy.wait_for_service('spawn')
        spawner = rospy.ServiceProxy('spawn', turtlesim.srv.Spawn)
        spawner(self.pose.x, self.pose.y, 0, self.turtle_name)
        # setting the turtle velocity publisher
        self.vel_pub = rospy.Publisher(self.turtle_name + '/cmd_vel', geometry_msgs.msg.Twist,queue_size=1)

    def check_collision(self, trans):
        if math.sqrt(trans[0] ** 2 + trans[1] ** 2) < distance_tolerance:
            collision = True
            self.follower = True
        else:
            collision = False
        return collision

    def follow_next_turtle(self, trans):
        if math.sqrt(trans[0] ** 2 + trans[1] ** 2) >= distance_tolerance:
            angular = 6 * math.atan2(trans[1], trans[0])
            linear = 2 * math.sqrt(trans[0] ** 2 + trans[1] ** 2)
        else:
            angular = 0
            linear = 0
        cmd = Twist()
        cmd.linear.x = linear
        cmd.angular.z = angular
        self.vel_pub.publish(cmd)



if __name__ == '__main__':

    turtle_number = 2
    rospy.init_node('turtle' + str(turtle_number))
    
    turtle = Turtle()
    turtle.spawn(turtle_number)

    listener = tf.TransformListener() 
    rate = rospy.Rate(10.0)

    while not rospy.is_shutdown():
        try:
            (trans,rot) = listener.lookupTransform('/turtle2', '/turtle1', rospy.Time(0))
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            continue

        if not turtle.follower:
            turtle.check_collision(trans)
        else:
            turtle.follow_next_turtle(trans)
        
        rate.sleep()