import cv2

# Replace the IP below with the one shown in your DroidCam app
cap = cv2.VideoCapture("http://192.168.29.123:4747/video")

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Unable to grab frame. Check connection or IP address.")
        break

    # Optional: Flip horizontally (like a selfie view)
    frame = cv2.flip(frame, 1)

    cv2.imshow("📱 Mobile Camera Feed", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
