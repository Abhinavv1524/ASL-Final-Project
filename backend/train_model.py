from google.colab import files
import os, zipfile
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization, Conv1D, MaxPooling1D, Flatten, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
# !pip install mediapipe
import mediapipe as mp
from tqdm import tqdm
import tensorflow as tf

# --- Step 2: Upload Dataset ---
# print("📤 Please upload your MP_Data.zip file...")
# uploaded = files.upload()

# # --- Step 3: Extract Dataset ---
# with zipfile.ZipFile("MP_Data.zip", 'r') as zip_ref:
#     zip_ref.extractall("MP_Data")

# print("✅ Dataset extracted!")
# print("Folders:", os.listdir("MP_Data"))

base_path = os.path.join(os.getcwd(), 'MP_Data')
if not os.path.exists(base_path):
    raise FileNotFoundError("❌ MP_Data folder not found. Please upload and extract first.")

if not os.listdir(base_path) or 'MP_Data' in os.listdir(base_path):
    base_path = os.path.join(base_path, 'MP_Data')

DATA_PATH = base_path
print(f"✅ Using data path: {DATA_PATH}")


actions = np.array(os.listdir(DATA_PATH))
print(f"🧩 Actions found: {actions}")

sequences, labels = [], []
label_map = {label: num for num, label in enumerate(actions)}

for action in tqdm(actions, desc="📂 Loading data"):
    action_path = os.path.join(DATA_PATH, action)
    for sequence in os.listdir(action_path):
        window = []
        for frame_num in range(30):  # 30 frames per sequence
            res = np.load(os.path.join(action_path, sequence, f"{frame_num}.npy"))
            window.append(res)
        sequences.append(window)
        labels.append(label_map[action])

X = np.array(sequences)
y = to_categorical(labels).astype(int)

print(f"✅ Data loaded: X={X.shape}, y={y.shape}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print("✅ Train-test split complete")

input_shape = (30, 1662)

inputs = Input(shape=input_shape)

x = Conv1D(128, 3, activation='relu', padding='same')(inputs)
x = MaxPooling1D(2)(x)
x = BatchNormalization()(x)
x = Dropout(0.2)(x)

x = Conv1D(256, 3, activation='relu', padding='same')(x)
x = MaxPooling1D(2)(x)
x = BatchNormalization()(x)
x = Dropout(0.3)(x)

x = LSTM(128, return_sequences=True, activation='relu')(x)
x = BatchNormalization()(x)
x = Dropout(0.3)(x)

x = LSTM(64, return_sequences=False, activation='relu')(x)
x = BatchNormalization()(x)
x = Dropout(0.3)(x)

x = Dense(128, activation='relu')(x)
x = Dropout(0.3)(x)
outputs = Dense(actions.shape[0], activation='softmax')(x)

model = Model(inputs, outputs)
model.summary()


model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss='categorical_crossentropy',
    metrics=['categorical_accuracy']
)
print("✅ Model compiled successfully")


checkpoint = ModelCheckpoint(
    'best_finetuned_model.keras', monitor='val_loss', save_best_only=True, verbose=1
)

early_stop = EarlyStopping(
    monitor='val_loss', patience=30, restore_best_weights=True
)

print("🚀 Fine-tuning started... This may take some time ⏳\n")

history = model.fit(
    X_train, y_train,
    epochs=300,
    validation_data=(X_test, y_test),
    callbacks=[checkpoint, early_stop],
    batch_size=16,
    verbose=1
)

os.makedirs('model', exist_ok=True)
model.save('model/fine_tuned_gesture_model.keras')
print("\n✅ Fine-tuning complete! Model saved in /model folder")



loss, accuracy = model.evaluate(X_test, y_test)
print(f"\n🎯 Final Test Accuracy: {accuracy*100:.2f}%")

plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.plot(history.history['categorical_accuracy'], label='Train Acc')
plt.plot(history.history['val_categorical_accuracy'], label='Val Acc')
plt.title('Accuracy')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Val Loss')
plt.title('Loss')
plt.legend()

plt.show()
