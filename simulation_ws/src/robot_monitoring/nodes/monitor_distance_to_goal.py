#!/usr/bin/env python

import time
import rospy
import numpy as np
#from itertools import izip
from std_msgs.msg import Header
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Path
from ros_monitoring_msgs.msg import MetricList, MetricData, MetricDimension


class MonitorDistanceToGoal():
    def __init__(self):
        self.scan_sub = rospy.Subscriber("/move_base/NavfnROS/plan", Path, callback=self.report_metric)
        self.metrics_pub = rospy.Publisher("/metrics", MetricList, queue_size=1)

    def calc_path_distance(self, msg):
        points = [(p.pose.position.x, p.pose.position.y) for p in msg.poses]
        array = np.array(points, dtype=np.dtype('f8','f8'))
        return sum((np.linalg.norm(p0-p1) for p0,p1 in zip(array[:-2],array[1:])))

    def report_metric(self, msg):
        if not msg.poses:
            rospy.logdebug('Path empty, not calculating distance')
            return

        distance = self.calc_path_distance(msg)
        rospy.logdebug('Distance to goal: %s', distance)
        
        header = Header()
        header.stamp = rospy.Time.from_sec(time.time())

        dimensions = [MetricDimension(name="robot_id", value="Turtlebot3"),
                      MetricDimension(name="category", value="RobotOperations")]
        metric = MetricData(header=header, metric_name="distance_to_goal",
                            unit=MetricData.UNIT_NONE,
                            value=distance,
                            time_stamp=rospy.Time.from_sec(time.time()),
                            dimensions=dimensions)

        self.metrics_pub.publish(MetricList([metric]))


def main():
    rospy.init_node('monitor_goal_to_distance')
    try:
        monitor = MonitorDistanceToGoal()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass

if __name__ == '__main__':
    main()