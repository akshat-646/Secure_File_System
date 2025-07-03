import cv2
import face_recognition
import os
import numpy as np
from PIL import Image

FACE_DIR = "face_data"

def ensure_face_directory():
    """Ensure face data directory exists"""
    if not os.path.exists(FACE_DIR):
        os.makedirs(FACE_DIR)
        print(f"✅ Created face data directory: {FACE_DIR}")

def capture_face(username):
    """Capture and save user's face image"""
    ensure_face_directory()
    
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("❌ Failed to open camera.")
        return False
    
    print("✅ Camera opened. Position your face in the frame and press 's' to save...")
    face_captured = False
    
    while True:
        ret, frame = cam.read()
        if not ret:
            print("❌ Failed to read from camera.")
            break
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Detect faces in the frame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        
        # Draw rectangles around detected faces
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        
        # Display instructions
        cv2.putText(frame, "Press 's' to save face, 'q' to quit", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        if len(face_locations) > 0:
            cv2.putText(frame, f"Face detected! ({len(face_locations)} face(s))", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No face detected", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.imshow("Face Capture - Position your face clearly", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            if len(face_locations) > 0:
                filepath = os.path.join(FACE_DIR, f"{username}.jpg")
                cv2.imwrite(filepath, frame)
                print(f"✅ Face saved as {filepath}")
                face_captured = True
                break
            else:
                print("❌ No face detected! Please position your face clearly and try again.")
        elif key == ord('q'):
            print("❌ Face capture cancelled by user.")
            break
    
    cam.release()
    cv2.destroyAllWindows()
    return face_captured

def verify_face(username):
    """Verify user's face against stored image"""
    filepath = os.path.join(FACE_DIR, f"{username}.jpg")
    
    if not os.path.exists(filepath):
        print(f"❌ No face data found for user: {username}")
        return False
    
    try:
        # Load the known face
        known_image = face_recognition.load_image_file(filepath)
        known_encodings = face_recognition.face_encodings(known_image)
        
        if len(known_encodings) == 0:
            print("❌ No face found in registered image.")
            return False
        
        known_encoding = known_encodings[0]
        
    except Exception as e:
        print(f"❌ Error loading registered face: {e}")
        return False
    
    # Start camera for verification
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("❌ Failed to open camera for verification.")
        return False
    
    print("🔍 Face verification in progress. Look at the camera...")
    verification_attempts = 0
    max_attempts = 100  # Increased attempts for better verification
    verification_threshold = 0.6  # Face recognition confidence threshold
    
    # Add a small delay to ensure camera is ready
    cv2.waitKey(1000)
    
    while verification_attempts < max_attempts:
        ret, frame = cam.read()
        if not ret:
            print("❌ Failed to read frame from camera.")
            verification_attempts += 1
            continue
        
        # Flip frame for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find faces and encodings in current frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        # Draw rectangles around faces
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        
        # Display status
        cv2.putText(frame, f"Verifying... {verification_attempts}/{max_attempts}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        if len(face_encodings) > 0:
            cv2.putText(frame, "Face detected - Checking...", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No face detected", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Add instruction text
        cv2.putText(frame, "Press 'q' to cancel", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        cv2.imshow("Face Verification - Look at the camera", frame)
        
        # Check each detected face
        for face_encoding in face_encodings:
            # Compare with known face
            matches = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=verification_threshold)
            face_distances = face_recognition.face_distance([known_encoding], face_encoding)
            
            if matches[0]:
                confidence = 1 - face_distances[0]
                print(f"✅ Face verified! Confidence: {confidence:.2f}")
                cam.release()
                cv2.destroyAllWindows()
                return True
        
        verification_attempts += 1
        
        # Allow manual exit
        key = cv2.waitKey(30) & 0xFF  # Reduced wait time for more responsive UI
        if key == ord('q'):
            print("❌ Face verification cancelled by user.")
            break
    
    cam.release()
    cv2.destroyAllWindows()
    print("❌ Face verification failed. No matching face found.")
    return False

def delete_face_data(username):
    """Delete face data for a user (for admin purposes)"""
    filepath = os.path.join(FACE_DIR, f"{username}.jpg")
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            print(f"✅ Face data deleted for user: {username}")
            return True
        except Exception as e:
            print(f"❌ Error deleting face data: {e}")
            return False
    else:
        print(f"❌ No face data found for user: {username}")
        return False

def list_face_data():
    """List all users with face data"""
    ensure_face_directory()
    face_files = [f for f in os.listdir(FACE_DIR) if f.endswith('.jpg')]
    usernames = [f.replace('.jpg', '') for f in face_files]
    return usernames

def test_camera():
    """Test camera functionality"""
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("❌ Camera not accessible")
        return False
    
    print("✅ Camera test - Press any key to exit")
    while True:
        ret, frame = cam.read()
        if not ret:
            print("❌ Failed to read from camera")
            break
        
        frame = cv2.flip(frame, 1)
        cv2.putText(frame, "Camera Test - Press any key to exit", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Camera Test", frame)
        
        if cv2.waitKey(1) != -1:
            break
    
    cam.release()
    cv2.destroyAllWindows()
    print("✅ Camera test completed")
    return True

# Debug function to check if face data exists
def check_face_data_exists(username):
    """Check if face data exists for a user"""
    filepath = os.path.join(FACE_DIR, f"{username}.jpg")
    exists = os.path.exists(filepath)
    print(f"Face data for {username}: {'EXISTS' if exists else 'NOT FOUND'} at {filepath}")
    return exists

if __name__ == "__main__":
    # Test the camera
    test_camera()