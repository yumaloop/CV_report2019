import cv2

input_file  = "./car2_kcf_opencv/car2_kcf_opencv.m4v"
output_file_prefix = "./car2_kcf_opencv/car2_kcf_opencv"
cap = cv2.VideoCapture(input_file)

def getFrame(cap, sec, count):
    # cv2.CAP_PROP_POS_MSEC : フィルム中の現在位置ミリ秒
    cap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
    ret, frame = cap.read()

    if ret:
        # Display frame number on frame
        cv2.putText(frame, "Frame No. "+str(int(count)), (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,255), 2)
        # Save frame as JPG file
        cv2.imwrite(output_file_prefix+str(count)+".jpg", frame)     # save frame as JPG file

    return ret

sec = 0
frameRate = 0.5 #//it will capture image in each 0.5 second
count = 1
success = getFrame(cap, sec, count)

while success:
    count = count + 1
    sec = sec + frameRate
    sec = round(sec, 2)
    success = getFrame(cap, sec, count)
