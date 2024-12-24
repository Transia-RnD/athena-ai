import json
import os
import pickle
from typing import List

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Setup a basic logger
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define the base directory (current directory for simplicity)
basedir = os.getcwd()


class MLChat:
    """
    Machine Learning AI class for a retrieval-based chatbot using RandomForestClassifier.
    """

    def __init__(
        self,
        storage_type: str,
        id: str,
        dir: str,
        name: str,
        version: str = "v1",
        features: List[str] = [],
    ) -> None:
        """
        Initializes the MiniAI chatbot.

        Parameters:
        - storage_type (str): Type of storage ('local' or 'gcs').
        - id (str): Identifier for the chatbot.
        - dir (str): Directory to store model and related files.
        - name (str): Name of the chatbot.
        - version (str): Version of the chatbot.
        - features (List[str]): List of feature names (e.g., ['user_input']).
        """
        self.label_encoder = LabelEncoder()
        self.features = features
        self.storage_type = storage_type
        self.id = id
        self.dir = dir
        self.name = name
        self.version = version
        self.dist_path: str = os.path.join(basedir, "dist")
        self.base_path: str = os.path.join(basedir, dir)
        self.name_path: str = os.path.join(self.base_path, f"{self.name}-ml")
        os.makedirs(self.base_path, exist_ok=True)
        os.makedirs(self.name_path, exist_ok=True)

        # Initialize empty data.json if not present
        data_json_path = os.path.join(self.name_path, "data.json")
        if not os.path.isfile(data_json_path):
            with open(data_json_path, "w") as f:
                f.write("[]")

        # Initialize placeholders
        self.model = None
        self.vectorizer = None
        self.label_encoder_values = {}

    def load_data(self, dataframe: pd.DataFrame):
        """
        Loads the dataset.

        Parameters:
        - dataframe (pd.DataFrame): DataFrame containing 'user_input' and 'intent' columns.

        Returns:
        - pd.DataFrame: Loaded DataFrame.
        """
        required_columns = {"user_input", "intent"}
        if not required_columns.issubset(dataframe.columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
        logger.debug("Data loaded successfully.")
        return dataframe

    def prepare_training(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepares the data for training by encoding intents.

        Parameters:
        - df (pd.DataFrame): DataFrame with user inputs and intents.

        Returns:
        - pd.DataFrame: DataFrame with encoded labels.
        """
        df_copy = df.copy()
        # Encode the intents into numerical labels
        df_copy["label"] = self.label_encoder.fit_transform(df_copy["intent"])
        logger.debug("Intents encoded successfully.")
        return df_copy

    def build(self, data_df: pd.DataFrame):
        """
        Trains the RandomForestClassifier on the provided dataset.

        Parameters:
        - data_df (pd.DataFrame): DataFrame containing 'user_input' and 'intent' columns.
        """
        df = self.prepare_training(data_df)

        # Initialize and fit the CountVectorizer
        self.vectorizer = CountVectorizer()
        X = self.vectorizer.fit_transform(df["user_input"])
        y = df["label"]
        logger.debug(
            f"Vectorizer fitted. Vocabulary size: {len(self.vectorizer.vocabulary_)}"
        )

        # Save the vectorizer to disk for future use
        vectorizer_path = os.path.join(self.name_path, "vectorizer.pkl")
        with open(vectorizer_path, "wb") as f:
            pickle.dump(self.vectorizer, f)
        logger.debug(f"Vectorizer saved at {vectorizer_path}")

        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        logger.debug(f"Training set size: {X_train.shape[0]} samples")
        logger.debug(f"Testing set size: {X_test.shape[0]} samples")

        # Initialize and train the RandomForestClassifier
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        logger.debug("RandomForestClassifier trained successfully.")

        # Evaluate the model (optional)
        y_pred = self.model.predict(X_test)
        from sklearn.metrics import classification_report

        report = classification_report(
            y_test, y_pred, target_names=self.label_encoder.classes_
        )
        logger.debug(f"Classification Report:\n{report}")

        # Save the trained model to disk
        model_path = os.path.join(self.name_path, "model.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(self.model, f)
        logger.debug(f"Model saved at {model_path}")

    def invoke(self, user_input: str) -> str:
        """
        Predicts the intent of the user input and retrieves the corresponding response.

        Parameters:
        - user_input (str): The input string from the user.

        Returns:
        - str: The chatbot's response.
        """
        # Load the vectorizer and model if not already loaded
        if self.vectorizer is None or self.model is None:
            vectorizer_path = os.path.join(self.name_path, "vectorizer.pkl")
            model_path = os.path.join(self.name_path, "model.pkl")
            with open(vectorizer_path, "rb") as f:
                self.vectorizer = pickle.load(f)
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
            logger.debug("Vectorizer and model loaded from disk.")

        # Transform the user input using the loaded vectorizer
        X_input = self.vectorizer.transform([user_input])
        logger.debug(f"User input vectorized: {X_input.toarray()}")

        # Predict the intent
        predicted_label = self.model.predict(X_input)[0]
        intent = self.label_encoder.inverse_transform([predicted_label])[0]
        logger.debug(f"Predicted intent: {intent}")

        # Retrieve the response based on intent
        response = self.get_response(intent)
        return response

    def get_response(self, intent: str) -> str:
        """
        Retrieves a predefined response based on the predicted intent.

        Parameters:
        - intent (str): The predicted intent.

        Returns:
        - str: The chatbot's response.
        """
        responses = {
            "greeting": "Hello! How can I assist you today?",
            "farewell": "Goodbye! Have a great day!",
            "name_query": "I am MiniAI, your assistant.",
            "status_query": "I'm just a bunch of code, but I'm functioning as expected!",
            "joke": "Why did the computer show up at work late? It had a hard drive!",
            "gratitude": "You're welcome! Happy to help!",
            "help_request": "Sure, I'm here to help! What do you need assistance with?",
            "capabilities_query": "I can assist you with information, tell jokes, and answer your questions.",
        }
        return responses.get(intent, "I'm sorry, I didn't understand that.")


def chatbot_interaction(chatbot: MLChat):
    """
    Handles the interaction loop between the user and the chatbot.

    Parameters:
    - chatbot (MiniAI): The trained MiniAI chatbot instance.
    """
    print("Chatbot is ready! Type 'exit' or 'quit' to stop.")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Chatbot: Goodbye! It was nice talking to you.")
            break
        response = chatbot.invoke(user_input)
        print(f"Chatbot: {response}")


def main():
    # Example dataset
    data = {
        "user_input": [
            "Hi there",
            "Hello",
            "Goodbye",
            "See you later",
            "What is your name?",
            "How are you?",
            "Tell me a joke",
            "Thank you",
            "Thanks",
            "Bye",
            "Hey",
            "Who are you?",
            "What's up?",
            "Can you help me?",
            "I need assistance",
            "Farewell",
            "Appreciate it",
            "Later",
            "What can you do?",
            "Assist me",
        ],
        "intent": [
            "greeting",
            "greeting",
            "farewell",
            "farewell",
            "name_query",
            "status_query",
            "joke",
            "gratitude",
            "gratitude",
            "farewell",
            "greeting",
            "name_query",
            "status_query",
            "help_request",
            "help_request",
            "farewell",
            "gratitude",
            "farewell",
            "capabilities_query",
            "help_request",
        ],
    }

    # Create a DataFrame from the dataset
    df = pd.DataFrame(data)

    # Initialize the MiniAI chatbot
    ai_chatbot = MLChat(
        storage_type="local",
        id="chatbot_01",
        dir="chatbot_data",
        name="intent_classifier",
        version="v1",
        features=["user_input"],  # Feature used for classification
    )

    # Load the dataset
    loaded_data = ai_chatbot.load_data(df)

    # Train the model
    ai_chatbot.build(loaded_data)

    # Start the chatbot interaction
    chatbot_interaction(ai_chatbot)


# if __name__ == "__main__":
#     main()
