import cv2
import math

url = "http://192.168.43.1:8080/video"
cap = cv2.VideoCapture(url)

points = []
distance = 0
measurements = [] 

def draw_circle(event, x, y, flags, params):
    global points, measurements
    if event == cv2.EVENT_LBUTTONDOWN:         
        if len(points) == 2:
            if len(points) == 2:
                p1 = points[0]
                p2 = points[1]
                dist = math.hypot(p1[0] - p2[0], p1[1] - p2[1])
                measurements.append((points.copy(), int(dist)))
            points = []
        points.append((x,y))
         
cv2.namedWindow('Frame')
cv2.setMouseCallback('Frame', draw_circle)

# Calibration variables
calibrated = True
pixel_to_cm_ratio =  14 # Default 1 pixel = 1 cm (will be calibrated)
reference_length_cm = 10.0  # Default reference length for calibration
calibration_points = []

print("Instructions:")
print("1. LEFT CLICK: Select points for measurement")
print("2. Press 'c': Clear current points")
print("3. Press 'r': Clear ALL measurements")
print("4. Press 'k': Calibration mode - measure known object")
print("5. Press 't': Toggle between pixels and cm display")
print("6. Press ESC: Exit program")

display_in_cm = True  # Toggle between pixels and cm

while True:
    _, frame = cap.read()
    if frame is None:
        break
    
    # Draw all previous measurements
    for i, (pts, dist) in enumerate(measurements):
        # Draw line
        cv2.line(frame, pts[0], pts[1], (0, 255, 0), 2)
        
        # Draw circles at endpoints
        cv2.circle(frame, pts[0], 5, (0, 255, 0), -1)
        cv2.circle(frame, pts[1], 5, (0, 255, 0), -1)
        
        # Calculate midpoint for text
        mid_x = (pts[0][0] + pts[1][0]) // 2
        mid_y = (pts[0][1] + pts[1][1]) // 2
        
        # Display measurement
        if display_in_cm and calibrated:
            display_value = dist / pixel_to_cm_ratio
            unit = "cm"
        else:
            display_value = dist
            unit = "px"
        
        text = f"{display_value:.1f} {unit}"
        cv2.putText(frame, text, (mid_x, mid_y - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
    
    # Draw current active points
    for i, point in enumerate(points):
        cv2.circle(frame, point, 5, (0, 0, 255), -1)
        
        # Draw temporary line if we have 2 points
        if len(points) == 2:
            cv2.line(frame, points[0], points[1], (0, 0, 255), 2)
            
            # Calculate and display distance
            p1 = points[0]
            p2 = points[1]
            distance = math.hypot(p1[0] - p2[0], p1[1] - p2[1])
            
            # Calculate midpoint
            mid_x = (p1[0] + p2[0]) // 2
            mid_y = (p1[1] + p2[1]) // 2
            
            if display_in_cm and calibrated:
                display_value = distance / pixel_to_cm_ratio
                unit = "cm"
            else:
                display_value = distance
                unit = "px"
            
            text = f"{display_value:.1f} {unit}"
            cv2.putText(frame, text, (mid_x, mid_y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    # Draw calibration points and line
    for point in calibration_points:
        cv2.circle(frame, point, 6, (255, 0, 255), -1)
    if len(calibration_points) == 2:
        cv2.line(frame, calibration_points[0], calibration_points[1], (255, 0, 255), 2)
    
    # Display info panel
    info_y = 30
    cv2.putText(frame, f"Measurements: {len(measurements)}", (10, info_y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    info_y += 25
    
    if display_in_cm and calibrated:
        cv2.putText(frame, f"Display: CM (1px = {1/pixel_to_cm_ratio:.3f}cm)", 
                   (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    elif display_in_cm and not calibrated:
        cv2.putText(frame, "Display: CM (Not calibrated!)", (10, info_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    else:
        cv2.putText(frame, "Display: Pixels", (10, info_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Calibration instructions
    if len(calibration_points) == 1:
        cv2.putText(frame, "Calibration: Click second point", (10, frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
    elif len(calibration_points) == 2:
        cal_dist = math.hypot(calibration_points[1][0] - calibration_points[0][0], 
                             calibration_points[1][1] - calibration_points[0][1])
        cv2.putText(frame, f"Press 'Enter' to set calibration ({cal_dist:.1f}px = {reference_length_cm}cm)", 
                   (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
    
    cv2.imshow('Frame', frame)
    
    # FIXED LINE: Removed the & 0xFF part that was causing issues
    key = cv2.waitKey(1)
    
    if key == 27 or key == ord('q'):  # ESC or 'q' key
        break
    elif key == ord('c'):  # Clear current points
        points = []
    elif key == ord('r'):  # Reset all measurements
        points = []
        measurements = []
    elif key == ord('k'):  # Enter calibration mode
        calibration_points = []
        calibrated = False
        print(f"\n=== CALIBRATION MODE ===")
        print(f"Place an object of known length ({reference_length_cm}cm) in view")
        print("Click two points at the ends of the object")
        print("Press Enter to confirm or ESC to cancel")
    elif key == ord('t'):  # Toggle display units
        display_in_cm = not display_in_cm
        print(f"Display units: {'Centimeters' if display_in_cm else 'Pixels'}")
    elif key == 13 and len(calibration_points) == 2:  # Enter key for calibration
        # Calculate pixel distance between calibration points
        pixel_dist = math.hypot(calibration_points[1][0] - calibration_points[0][0], 
                               calibration_points[1][1] - calibration_points[0][1])
        
        if pixel_dist > 0:
            pixel_to_cm_ratio = pixel_dist / reference_length_cm
            calibrated = True
            print(f"\n=== CALIBRATION COMPLETE ===")
            print(f"{pixel_dist:.1f} pixels = {reference_length_cm} cm")
            print(f"1 pixel = {1/pixel_to_cm_ratio:.3f} cm")
            print(f"1 cm = {pixel_to_cm_ratio:.1f} pixels")
        calibration_points = []
    elif key == ord('+'):  # Increase reference length
        reference_length_cm += 0.5
        print(f"Reference length: {reference_length_cm} cm")
    elif key == ord('-'):  # Decrease reference length
        if reference_length_cm > 0.5:
            reference_length_cm -= 0.5
            print(f"Reference length: {reference_length_cm} cm")
    
cap.release()
cv2.destroyAllWindows()