import os
import cv2
import dlib
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, LeakyReLU
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pickle
from scipy.spatial import distance

class DrowsinessDetector:
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        self.scaler = StandardScaler()
        
    def calculate_ear(self, eye_points):
        A = distance.euclidean(eye_points[1], eye_points[5])
        B = distance.euclidean(eye_points[2], eye_points[4])
        C = distance.euclidean(eye_points[0], eye_points[3])
        ear = (A + B) / (2.0 * C)
        return ear
    
    def calculate_mouth_aspect_ratio(self, mouth_points):
        A = distance.euclidean(mouth_points[2], mouth_points[10])
        B = distance.euclidean(mouth_points[4], mouth_points[8])
        C = distance.euclidean(mouth_points[0], mouth_points[6])
        mar = (A + B) / (2.0 * C)
        return mar
    
    def extract_features(self, image_path):
        try:
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.detector(gray)
            
            if len(faces) == 0:
                return None
                
            face = faces[0]
            landmarks = self.predictor(gray, face)
            points = np.array([[p.x, p.y] for p in landmarks.parts()])
            
            # Extract facial features
            left_eye = points[36:42]
            right_eye = points[42:48]
            mouth = points[48:68]
            
            # Calculate ratios
            left_ear = self.calculate_ear(left_eye)
            right_ear = self.calculate_ear(right_eye)
            mar = self.calculate_mouth_aspect_ratio(mouth)
            
            # Calculate eye aspect ratio variance
            ear_var = np.var([left_ear, right_ear])
            
            # Extract head pose features
            nose_bridge = points[27:31]
            nose_tip = points[31:36]
            
            # Calculate angles
            nose_angle = np.arctan2(nose_tip[-1][1] - nose_bridge[0][1],
                                  nose_tip[-1][0] - nose_bridge[0][0])
            
            features = []
            features.extend([left_ear, right_ear, mar, ear_var, nose_angle])
            
            # Add normalized landmark positions
            for point in points:
                features.extend([point[0]/img.shape[1], point[1]/img.shape[0]])
            
            # Add histogram features
            eye_region = gray[min(left_eye[:,1]):max(left_eye[:,1]),
                            min(left_eye[:,0]):max(left_eye[:,0])]
            if eye_region.size > 0:
                hist = cv2.calcHist([eye_region], [0], None, [8], [0, 256])
                features.extend(hist.flatten())
                
            return np.array(features)
            
        except Exception as e:
            print(f"Error processing {image_path}: {str(e)}")
            return None
    
    def prepare_dataset(self):
        dataset_dir = '/Users/nekonyo/ai_project/Driver_Drowsy_Master/server/dataset'
        X = []
        y = []
        
        # Process images with data augmentation
        for class_name, label in [('Drowsy', 1), ('Non Drowsy', 0)]:
            class_dir = os.path.join(dataset_dir, class_name)
            for img_name in os.listdir(class_dir):
                if img_name.endswith(('.jpg', '.jpeg', '.png')):
                    img_path = os.path.join(class_dir, img_name)
                    features = self.extract_features(img_path)
                    if features is not None:
                        X.append(features)
                        y.append(label)
                        
                        # Add augmented samples for minority class
                        if label == 1:  # Drowsy class
                            features_aug = features + np.random.normal(0, 0.01, features.shape)
                            X.append(features_aug)
                            y.append(label)
        
        X = np.array(X)
        y = np.array(y)
        
        # Normalize features
        X = self.scaler.fit_transform(X)
        
        return X, y
    
    def create_model(self, input_shape):
        model = Sequential([
            Dense(512, input_shape=(input_shape,)),
            LeakyReLU(alpha=0.1),
            BatchNormalization(),
            Dropout(0.4),
            
            Dense(256),
            LeakyReLU(alpha=0.1),
            BatchNormalization(),
            Dropout(0.4),
            
            Dense(128),
            LeakyReLU(alpha=0.1),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(64),
            LeakyReLU(alpha=0.1),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train_model(self):
        X, y = self.prepare_dataset()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
        
        model = self.create_model(X_train.shape[1])
        
        if not os.path.exists('models'):
            os.makedirs('models')
            
        callbacks = [
            ModelCheckpoint(
                'models/best_model.dat',
                monitor='val_accuracy',
                save_best_only=True,
                mode='max'
            ),
            EarlyStopping(
                monitor='val_accuracy',
                patience=15,
                restore_best_weights=True,
                mode='max'
            ),
            ReduceLROnPlateau(
                monitor='val_accuracy',
                factor=0.1,
                patience=5,
                min_lr=0.000001,
                mode='max'
            )
        ]
        
        history = model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=100,
            batch_size=32,
            callbacks=callbacks,
            class_weight={0: 1.0, 1: 1.5}  # Give more weight to drowsy class
        )
        
        model_data = {
            'model': model,
            'history': history.history,
            'feature_shape': X_train.shape[1],
            'scaler': self.scaler
        }
        
        with open('models/drowsiness_detector.keras', 'wb') as f:
            pickle.dump(model_data, f)
        
        return model, history

if __name__ == "__main__":
    detector = DrowsinessDetector()
    model, history = detector.train_model()
    
    print(f"Final training accuracy: {history.history['accuracy'][-1]:.2f}")
    print(f"Final validation accuracy: {history.history['val_accuracy'][-1]:.2f}")
