# -*- coding: utf-8 -*-
"""Model_Training.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1b7mCdXre5pKHz7Y9cz1_-fDnvZtwTBqz
"""



# Instal versi TensorFlow dan transformers yang kompatibel
!pip install tensorflow==2.12.0
!pip install transformers==4.30.2

import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from transformers import BertTokenizer, TFBertForSequenceClassification

# Load the dataset
data = pd.read_csv("https://raw.githubusercontent.com/adi31891/capstone-C241-PR565/f8a43716e964aa3bc19b1de1d1947aa550dd6bb9/data/capstone_new_dataset.csv")

# Extract text and labels
texts = data['text'].astype(str).values
labels = data['sentiment'].astype(str).values

# Encode labels to integers
label_encoder = LabelEncoder()
integer_encoded_labels = label_encoder.fit_transform(labels)

# One-hot encode the integer labels
onehot_encoder = OneHotEncoder(sparse_output=False)
integer_encoded_labels = integer_encoded_labels.reshape(len(integer_encoded_labels), 1)
onehot_encoded_labels = onehot_encoder.fit_transform(integer_encoded_labels)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(texts, onehot_encoded_labels, test_size=0.2, random_state=42)

# Load BERT tokenizer and model from Hugging Face
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = TFBertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=3)

# Tokenize the input texts
def tokenize_texts(texts, tokenizer, max_length=128):
    return tokenizer(
        texts.tolist(),
        max_length=max_length,
        truncation=True,
        padding=True,
        return_tensors='tf'
    )

X_train_tokens = tokenize_texts(X_train, tokenizer)
X_test_tokens = tokenize_texts(X_test, tokenizer)

# Compile the model
optimizer = tf.keras.optimizers.Adam(learning_rate=0.00001)
loss = tf.keras.losses.CategoricalCrossentropy(from_logits=True)
metrics = ['accuracy']
bert_model.compile(optimizer=optimizer, loss=loss, metrics=metrics)

# Train the model
bert_model.fit(
    [X_train_tokens['input_ids'], X_train_tokens['attention_mask']],
    y_train,
    epochs=5,
    batch_size=16,
    validation_data=([X_test_tokens['input_ids'], X_test_tokens['attention_mask']], y_test)
)

# Simpan bobot model ke file .bin
bert_model.save_weights('bert_model_weights.bin')

# Fungsi untuk memuat bobot model
def load_model_weights(model, weights_path):
    model.load_weights(weights_path)
    return model

# Function to predict sentiment
def predict_sentiment(text):
    tokens = tokenize_texts([text], tokenizer)
    prediction = bert_model.predict([tokens['input_ids'], tokens['attention_mask']])
    sentiment_index = tf.argmax(prediction.logits[0]).numpy()
    sentiment = label_encoder.inverse_transform([sentiment_index])[0]
    return sentiment

# Example usage with Gen AI response
def generate_response(sentiment):
    if sentiment == 'good':
        return "I'm glad to hear that! Keep up the positive vibes."
    elif sentiment == 'bad':
        return "I'm sorry to hear that. Remember, it's okay to feel this way sometimes. Can I help with something?"
    elif sentiment == 'neutral':
        return "Thanks for sharing your feelings."
    else:
        return "Thanks for sharing your feelings."

# Predict sentiment and generate a response
user_message = "I feel so anxious about my exams."
predicted_sentiment = predict_sentiment(user_message)
response = generate_response(predicted_sentiment)

print(f"User message: {user_message}")
print(f"Predicted sentiment: {predicted_sentiment}")
print(f"Response: {response}")

