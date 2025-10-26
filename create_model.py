import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from sklearn.model_selection import train_test_split
import os

def create_dummy_gesture_data():
    """Create dummy gesture data for demonstration purposes"""
    # This would normally be replaced with actual training data
    # Each gesture has 63 features (21 landmarks * 3 coordinates)
    num_samples_per_gesture = 100
    num_features = 63  # 21 landmarks * 3 (x, y, z)

    gestures = [
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        'hello', 'thank you', 'please',
        'namaste', 'sorry', 'good', 'bad', 'eat', 'drink'
    ]

    num_classes = len(gestures)

    # Generate dummy data with some variation for each gesture
    X = []
    y = []

    for gesture_idx, gesture in enumerate(gestures):
        # Create base pattern for each gesture
        base_pattern = np.random.rand(num_features)

        for _ in range(num_samples_per_gesture):
            # Add some noise to create variation
            pattern = base_pattern + np.random.normal(0, 0.1, num_features)
            X.append(pattern)
            y.append(gesture_idx)

    X = np.array(X)
    y = np.array(y)

    return X, y, gestures

def create_model(input_shape, num_classes):
    """Create a neural network model for gesture recognition"""
    model = Sequential([
        Dense(128, activation='relu', input_shape=(input_shape,)),
        Dropout(0.2),
        Dense(64, activation='relu'),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])

    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    return model

def train_and_save_model():
    """Train the model and save it"""
    print("Creating dummy gesture data...")
    X, y, gestures = create_dummy_gesture_data()

    print(f"Dataset shape: {X.shape}")
    print(f"Number of classes: {len(gestures)}")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Create model
    model = create_model(X.shape[1], len(gestures))

    print("Training model...")
    history = model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_data=(X_test, y_test),
        verbose=1
    )

    # Evaluate model
    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(".2f")

    # Save model
    model_path = 'gesture_model.h5'
    model.save(model_path)
    print(f"Model saved to {model_path}")

    # Save gesture labels
    with open('gesture_labels.txt', 'w') as f:
        for gesture in gestures:
            f.write(gesture + '\n')
    print("Gesture labels saved to gesture_labels.txt")

    return model_path

if __name__ == "__main__":
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)

    # Train and save model
    model_path = train_and_save_model()

    print("\nModel training complete!")
    print(f"Model saved at: {model_path}")
    print("You can now run main.py to use the gesture recognition system")
    print("\nNote: This model uses dummy data for demonstration.")
    print("For real gesture recognition, you would need to:")
    print("1. Collect actual hand landmark data for each gesture")
    print("2. Train the model with real data")
    print("3. Fine-tune the model architecture if needed")