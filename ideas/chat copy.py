import os
import pickle
import json
import logging
from typing import List, Dict

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

# Setup a basic logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define the base directory (current directory for simplicity)
basedir = os.getcwd()


class ChatAI:
    """
    ChatAI class for a retrieval-based chatbot using RandomForestClassifier.
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
        Initializes the ChatAI chatbot.

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
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=1000)
        self.label_encoder_values = {}

    def load_data(self, qa_pairs: List[Dict[str, str]]) -> pd.DataFrame:
        """
        Loads the dataset from a list of question-answer pairs.

        Parameters:
        - qa_pairs (List[Dict[str, str]]): List of dictionaries with 'question' and 'answer' keys.

        Returns:
        - pd.DataFrame: Loaded DataFrame.
        """
        df = pd.DataFrame(qa_pairs)
        required_columns = {"question", "answer"}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"Each QA pair must contain columns: {required_columns}")
        logger.debug("Data loaded successfully.")
        return df

    def prepare_training(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepares the data for training by encoding answers.

        Parameters:
        - df (pd.DataFrame): DataFrame with 'question' and 'answer' columns.

        Returns:
        - pd.DataFrame: DataFrame with encoded labels.
        """
        df_copy = df.copy()
        # Encode the answers into numerical labels
        df_copy["label"] = self.label_encoder.fit_transform(df_copy["answer"])
        logger.debug("Answers encoded successfully.")
        return df_copy

    def build(self, data_df: pd.DataFrame):
        """
        Trains the RandomForestClassifier on the provided dataset.

        Parameters:
        - data_df (pd.DataFrame): DataFrame containing 'question' and 'answer' columns.
        """
        df = self.prepare_training(data_df)

        # Initialize and fit the CountVectorizer (or TfidfVectorizer)
        # self.vectorizer = CountVectorizer(ngram_range=(1, 2), max_features=1000)
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=1000)
        # Alternatively, use TfidfVectorizer for better performance
        # self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=1000)

        X = self.vectorizer.fit_transform(df["question"])
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
        classes = np.arange(len(self.label_encoder.classes_))
        y_pred = self.model.predict(X_test)
        report = classification_report(
            y_test,
            y_pred,
            labels=classes,
            target_names=self.label_encoder.classes_,
            zero_division=0,
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

        # Predict the answer label
        predicted_label = self.model.predict(X_input)[0]
        intent = self.label_encoder.inverse_transform([predicted_label])[0]
        logger.debug(f"Predicted intent (answer): {intent}")

        # Retrieve the response based on intent
        response = self.get_response(intent)
        return response

    def get_response(self, intent: str) -> str:
        """
        Retrieves a predefined response based on the predicted intent.

        Parameters:
        - intent (str): The predicted intent (answer).

        Returns:
        - str: The chatbot's response.
        """
        return intent  # Since 'intent' now directly refers to the answer


def chatbot_interaction(chatbot: ChatAI):
    """
    Handles the interaction loop between the user and the chatbot.

    Parameters:
    - chatbot (ChatAI): The trained ChatAI chatbot instance.
    """
    print("Chatbot is ready! Type 'exit' or 'quit' to stop.")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nChatbot: Goodbye! It was nice talking to you.")
            break

        if user_input.lower() in ["exit", "quit"]:
            print("Chatbot: Goodbye! It was nice talking to you.")
            break
        response = chatbot.invoke(user_input)
        print(f"Chatbot: {response}")


def main():
    # Example dataset: list of question-answer pairs
    qa_pairs = [
        {"question": "Hi there", "answer": "Hello! How can I assist you today?"},
        {"question": "Hello", "answer": "Hello! How can I assist you today?"},
        {"question": "Goodbye", "answer": "Goodbye! Have a great day!"},
        {"question": "See you later", "answer": "Goodbye! Have a great day!"},
        {"question": "What is your name?", "answer": "I am ChatAI, your assistant."},
        {
            "question": "How are you?",
            "answer": "I'm just a bunch of code, but I'm functioning as expected!",
        },
        {
            "question": "Tell me a joke",
            "answer": "Why did the computer show up at work late? It had a hard drive!",
        },
        {"question": "Thank you", "answer": "You're welcome! Happy to help!"},
        {"question": "Thanks", "answer": "You're welcome! Happy to help!"},
        {"question": "Bye", "answer": "Goodbye! Have a great day!"},
        {"question": "Hey", "answer": "Hello! How can I assist you today?"},
        {"question": "Who are you?", "answer": "I am ChatAI, your assistant."},
        {
            "question": "What's up?",
            "answer": "I'm here to help you with any questions or information you need.",
        },
        {
            "question": "Can you help me?",
            "answer": "Sure, I'm here to help! What do you need assistance with?",
        },
        {
            "question": "I need assistance",
            "answer": "Sure, I'm here to help! What do you need assistance with?",
        },
        {"question": "Farewell", "answer": "Goodbye! Have a great day!"},
        {"question": "Appreciate it", "answer": "You're welcome! Happy to help!"},
        {"question": "Later", "answer": "Goodbye! Have a great day!"},
        {
            "question": "What can you do?",
            "answer": "I can assist you with information, tell jokes, and answer your questions.",
        },
        {
            "question": "Assist me",
            "answer": "Sure, I'm here to help! What do you need assistance with?",
        },
        # Add more question-answer pairs as needed
    ]

    # Create a DataFrame from the dataset
    df = pd.DataFrame(qa_pairs)

    # Initialize the ChatAI chatbot
    ai_chatbot = ChatAI(
        storage_type="local",
        id="chatbot_01",
        dir="chatbot_data",
        name="qa_bot",
        version="v1",
        features=["question"],  # Feature used for classification
    )

    # Load the dataset
    loaded_data = ai_chatbot.load_data(qa_pairs)

    # Train the model
    ai_chatbot.build(loaded_data)

    # Start the chatbot interaction
    chatbot_interaction(ai_chatbot)


# if __name__ == "__main__":
#     main()
