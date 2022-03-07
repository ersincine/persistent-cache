"""
import cv2 as cv
import copyreg


def pickle_keypoints(kp):
    return cv.KeyPoint, (*kp.pt, kp.size, kp.angle, kp.response, kp.octave, kp.class_id)


def pickle_dmatches(dmatch):
    return cv.DMatch, (dmatch.queryIdx, dmatch.trainIdx, dmatch.imgIdx, dmatch.distance)


copyreg.pickle(cv.KeyPoint().__class__, pickle_keypoints)
copyreg.pickle(cv.DMatch().__class__, pickle_dmatches)

# Uncomment these if needed.
# Add more if needed.

"""
