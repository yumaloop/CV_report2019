import numpy as np 
import cv2
import sys
from time import time

import kcftracker

if __name__ == '__main__':
    # set I/O files
    input_file  = "./input/car1.mp4"
    output_file = "./output/car1_kcf_impl/car1_kcf_impl.m4v"

    # cap: captured images from the video
    cap = cv2.VideoCapture(input_file)
    cap_width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
     
    # out: result video (m4v)
    # see also https://gist.github.com/takuma7/44f9ecb028ff00e2132e
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    out = cv2.VideoWriter(output_file,fourcc, 20.0, (cap_width, cap_height))

    # KCF Tracker
    tracker_type="KCF Tracker (Implemented)"
    tracker = kcftracker.KCFTracker(True, True, True)  # hog, fixed_window, multiscale

    # Exit if video not opened.
    if not cap.isOpened():
        print("Could not open video")
        sys.exit()

    # Read first frame.
    ret, frame = cap.read()
    if not ret:
        print('Cannot read video file')
        sys.exit()

    # Define an initial bounding box
    # bbox = (418, 127, 164, 556) # for ./input/chaplin.mp4
    bbox = (587, 306, 624, 275) # for ./input/car1.mp4
    # bbox = (338, 245, 694, 256) # for ./input/car2.mp4
    # bbox = (269, 230, 535, 190) # for ./input/bus1.mp4

    # Uncomment the line below to select a different bounding box
    # bbox = cv2.selectROI(frame, False)
    # print("bbox :", bbox)

    # Initialize tracker with first frame and bounding box
    tracker.init(frame, bbox) # <---------- tracker init

    frame_counter = 0

    while True:
        frame_counter += 1
        ret, frame = cap.read()
        if not ret:
            break

        # Start timer
        timer = cv2.getTickCount()

        # Update tracker
        bbox = tracker.update(frame) # <----------- tracker processing
        bbox = list(map(int, bbox))

        # Calculate Frame per second (FPS)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);

        # Draw bounding box
        if ret:
            # Tracking success
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))

            # Draw ROI
            cv2.rectangle(frame, p1, p2, (0,0,255), 2, 1)
        else :
            # Tracking failure
            cv2.putText(frame, "Tracking failure detected", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,255) ,2)

        # Display tracker type on frame
        cv2.putText(frame, tracker_type, (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,255), 2);
     
        # Display FPS on frame
        cv2.putText(frame, "FPS : " + str(int(fps)),  (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,255), 2);

        # Display result
        cv2.imshow("Tracking", frame)

        # Save result as mp4 file
        out.write(frame) 

        # Exit if ESC pressed
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
