#!/usr/bin/env python

import unittest
import catkin_doc.python
import os.path

class TestPython(unittest.TestCase):
    """Test basic functionality of the python doc module"""
    def test_extract_params(self):
        node = catkin_doc.python.PythonParser("setup.py")
        self.assertTrue(
            node.extract_param(
                "self.stop_robot_topic = rospy.get_param('~stop_robot_topic', '/hello')")[0])
        self.assertTrue(
            node.extract_param(
                "self.stop_robot_topic = rospy.get_param('~stop_robot_topic')")[0])
        self.assertTrue(
            node.extract_param(
                'global_name = rospy.get_param("/global_name")')[0])

    def test_extract_params_false(self):
        node = catkin_doc.python.PythonParser("setup.py")
        self.assertFalse(
            node.extract_param( "rospy.loginfo('~stop_robot_topic')")[0])

    def test_extract_subs(self):
        parser = catkin_doc.python.PythonParser("setup.py")
        self.assertTrue(
            parser.extract_sub(
                'rospy.Subscriber("chatter", String, callback)')[0])
        self.assertTrue(
            parser.extract_sub(
                'self.joint_state_sub = rospy.Subscriber("pathloader/reordered_joint_states", JointState, self.joint_status_changed)')[0])

    def test_extract_subs_false(self):
        parser = catkin_doc.python.PythonParser("setup.py")
        self.assertFalse(
            parser.extract_sub( "rospy.loginfo('~stop_robot_topic')")[0])

    def test_extract_pubs(self):
        parser = catkin_doc.python.PythonParser("setup.py")
        self.assertTrue(
            parser.extract_pub(
                "pub = rospy.Publisher('chatter', String, queue_size=10)")[0])
        self.assertTrue(
            parser.extract_pub(
                "pub = rospy.Publisher('chatter', String, queue_size=10, latch=True)")[0])

    def test_extract_pubs_false(self):
        parser = catkin_doc.python.PythonParser("setup.py")
        self.assertFalse(
            parser.extract_pub( "rospy.loginfo('~stop_robot_topic')")[0])

    def test_action_clients(self):
        parser = catkin_doc.python.PythonParser("setup.py")
        self.assertTrue(
            parser.extract_action_client(
                "self.action_client = actionlib.SimpleActionClient('pathloader', PlayTrajectoryAction)")[0])

    def test_action_clients_false(self):
        parser = catkin_doc.python.PythonParser("setup.py")
        self.assertFalse(
            parser.extract_action_client( "rospy.loginfo('~stop_robot_topic')")[0])

    def test_service_clients(self):
        parser = catkin_doc.python.PythonParser("setup.py")
        self.assertTrue(
            parser.extract_service_client(
                "append_points = rospy.ServiceProxy('pathloader/appendPoints', ChangePath)")[0])

    def test_service_clients_false(self):
        parser = catkin_doc.python.PythonParser("setup.py")
        self.assertFalse(
            parser.extract_service_client( "rospy.loginfo('~stop_robot_topic')")[0])

    def test_service(self):
        parser = catkin_doc.python.PythonParser("setup.py")
        self.assertTrue(
            parser.extract_service(
                "s = rospy.Service('add_two_ints', AddTwoInts, handle_add_two_ints)")[0])

    def test_service_false(self):
        parser = catkin_doc.python.PythonParser("setup.py")
        self.assertFalse(
            parser.extract_service( "rospy.loginfo('~stop_robot_topic')")[0])

    def test_action(self):
        parser = catkin_doc.python.PythonParser("setup.py")
        self.assertTrue(
            parser.extract_action(
                "self._as = actionlib.SimpleActionServer(self._action_name, actionlib_tutorials.msg.FibonacciAction, execute_cb=self.execute_cb, auto_start=False)")[0])

    def test_action_false(self):
        parser = catkin_doc.python.PythonParser("setup.py")
        self.assertFalse(
            parser.extract_action( "rospy.loginfo('~stop_robot_topic')")[0])

    def test_comment(self):
        parser = catkin_doc.python.PythonParser("setup.py")
        self.assertTrue(
            parser.extract_comment(
                "#This should be recognized as comment") == "This should be recognized as comment")

