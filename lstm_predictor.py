"""
🤖 SWARNE V2.0 - LSTM Predictor
Prédiction de direction du marché avec LSTM
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Optional
from dataclasses import dataclass
import logging

# Import MT5 utilities
try:
    from mt5_utils import load_mt5_data, normalize_symbol
    MT5_UTILS_AVAILABLE = True
except ImportError:
    MT5_UTILS_AVAILABLE = False

# TensorFlow/Keras imports (avec gestion d'erreur)
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models, callbacks
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logging.warning("⚠️ TensorFlow not available. Install with: pip install tensorflow")

logger = logging.getLogger(__name__)


@dataclass
class LSTMConfig:
    """Configuration du modèle LSTM"""
    sequence_length: int = 60        # Longueur des séquences (60 barres)
    features: List[str] = None       # Features à utiliser
    
    # Architecture
    lstm_units: List[int] = None     # [128, 64, 32]
    dropout_rate: float = 0.2
    
    # Training
    epochs: int = 50
    batch_size: int = 32
    validation_split: float = 0.2
    learning_rate: float = 0.001
    
    # Early stopping
    patience: int = 10
    min_delta: float = 0.001
    
    def __post_init__(self):
        if self.features is None:
            self.features = [
                'close', 'volume', 'ema_9', 'ema_21', 
                'adx', 'rsi', 'atr', 'macd'
            ]
        if self.lstm_units is None:
            self.lstm_units = [128, 64, 32]


class FeatureEngineering:
    """Ingénierie des features pour ML"""
    
    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculer tous les indicateurs techniques"""
        df = df.copy()
        
        # EMAs
        df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        
        # RSI
        df['rsi'] = FeatureEngineering._calculate_rsi(df['close'], period=14)
        
        # ADX (simplifié)
        df['adx'] = 25.0  # Placeholder - implémenter le vrai ADX
        
        # ATR
        df['atr'] = FeatureEngineering._calculate_atr(df, period=14)
        
        # MACD
        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands
        sma_20 = df['close'].rolling(window=20).mean()
        std_20 = df['close'].rolling(window=20).std()
        df['bb_upper'] = sma_20 + 2 * std_20
        df['bb_lower'] = sma_20 - 2 * std_20
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / sma_20
        
        # Volume features - gérer tick_volume ou volume
        volume_col = 'volume' if 'volume' in df.columns else 'tick_volume'
        
        if volume_col in df.columns:
            df['volume_sma'] = df[volume_col].rolling(window=20).mean()
            df['volume_ratio'] = df[volume_col] / df['volume_sma']
        else:
            # Si pas de volume du tout, créer des colonnes vides
            logger.warning("⚠️  Aucune colonne volume/tick_volume trouvée, features volume désactivées")
            df['volume_sma'] = 1.0
            df['volume_ratio'] = 1.0
        
        # Price changes
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        # Momentum
        df['momentum'] = df['close'] - df['close'].shift(10)
        df['roc'] = ((df['close'] - df['close'].shift(10)) / 
                     df['close'].shift(10)) * 100
        
        return df
    
    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculer RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def _calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculer ATR"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr


class LSTMPredictor:
    """Prédicteur LSTM pour direction du marché"""
    
    def __init__(self, config: LSTMConfig):
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is required. Install with: pip install tensorflow")
        
        self.config = config
        self.model = None
        self.scaler = None
        self.feature_engineer = FeatureEngineering()
        
        # Historique d'entraînement
        self.history = None
        
    def build_model(self, input_shape: Tuple[int, int]):
        """Construire l'architecture LSTM"""
        model = models.Sequential()
        
        # Input layer
        model.add(layers.Input(shape=input_shape))
        
        # LSTM layers
        for i, units in enumerate(self.config.lstm_units):
            return_sequences = (i < len(self.config.lstm_units) - 1)
            
            model.add(layers.LSTM(
                units=units,
                return_sequences=return_sequences,
                dropout=self.config.dropout_rate
            ))
            
            if return_sequences:
                model.add(layers.BatchNormalization())
        
        # Dense layers
        model.add(layers.Dense(32, activation='relu'))
        model.add(layers.Dropout(self.config.dropout_rate))
        model.add(layers.Dense(16, activation='relu'))
        
        # Output layer (3 classes: BUY, SELL, HOLD)
        model.add(layers.Dense(3, activation='softmax'))
        
        # Compiler
        optimizer = keras.optimizers.Adam(learning_rate=self.config.learning_rate)
        model.compile(
            optimizer=optimizer,
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        logger.info(f"🧠 LSTM model built: {model.count_params():,} parameters")
        
        return model
    
    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Préparer les données pour l'entraînement"""
        # Calculer les indicateurs
        df = self.feature_engineer.calculate_indicators(df)
        
        # Supprimer les NaN
        df = df.dropna()
        
        # Créer le target (direction future)
        # 1 = UP (price increases), 0 = DOWN, 2 = NEUTRAL
        future_returns = df['close'].shift(-1) - df['close']
        threshold = df['atr'] * 0.3  # Mouvement significatif = 30% de l'ATR
        
        target = np.where(future_returns > threshold, 1,  # UP
                         np.where(future_returns < -threshold, 0,  # DOWN
                                 2))  # NEUTRAL
        
        # Supprimer la dernière ligne (pas de target)
        df = df.iloc[:-1]
        target = target[:-1]
        
        # Sélectionner les features
        feature_columns = [col for col in self.config.features if col in df.columns]
        X = df[feature_columns].values
        
        # Normaliser
        from sklearn.preprocessing import StandardScaler
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Créer les séquences
        X_seq, y_seq = self._create_sequences(X_scaled, target)
        
        # One-hot encode le target
        y_onehot = keras.utils.to_categorical(y_seq, num_classes=3)
        
        logger.info(f"📊 Data prepared: {X_seq.shape[0]} sequences")
        logger.info(f"   Sequence length: {X_seq.shape[1]}")
        logger.info(f"   Features: {X_seq.shape[2]}")
        
        return X_seq, y_onehot
    
    def _create_sequences(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Créer des séquences pour LSTM"""
        X_seq = []
        y_seq = []
        
        seq_len = self.config.sequence_length
        
        for i in range(seq_len, len(X)):
            X_seq.append(X[i-seq_len:i])
            y_seq.append(y[i])
        
        return np.array(X_seq), np.array(y_seq)
    
    def train(self, df: pd.DataFrame) -> dict:
        """Entraîner le modèle"""
        logger.info("🚀 Starting LSTM training...")
        
        # Préparer les données
        X, y = self.prepare_data(df)
        
        # Construire le modèle si pas encore fait
        if self.model is None:
            input_shape = (X.shape[1], X.shape[2])
            self.build_model(input_shape)
        
        # Callbacks
        early_stop = callbacks.EarlyStopping(
            monitor='val_loss',
            patience=self.config.patience,
            min_delta=self.config.min_delta,
            restore_best_weights=True
        )
        
        reduce_lr = callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7
        )
        
        # Entraîner
        self.history = self.model.fit(
            X, y,
            epochs=self.config.epochs,
            batch_size=self.config.batch_size,
            validation_split=self.config.validation_split,
            callbacks=[early_stop, reduce_lr],
            verbose=1
        )
        
        # Résultats
        final_loss = self.history.history['loss'][-1]
        final_accuracy = self.history.history['accuracy'][-1]
        val_loss = self.history.history['val_loss'][-1]
        val_accuracy = self.history.history['val_accuracy'][-1]
        
        logger.info(f"✅ Training completed!")
        logger.info(f"   Final loss: {final_loss:.4f}")
        logger.info(f"   Final accuracy: {final_accuracy:.2%}")
        logger.info(f"   Val loss: {val_loss:.4f}")
        logger.info(f"   Val accuracy: {val_accuracy:.2%}")
        
        return {
            'loss': final_loss,
            'accuracy': final_accuracy,
            'val_loss': val_loss,
            'val_accuracy': val_accuracy
        }
    
    def predict(self, df: pd.DataFrame) -> Tuple[str, float]:
        """Prédire la direction du marché"""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        # Calculer les indicateurs
        df = self.feature_engineer.calculate_indicators(df)
        df = df.dropna()
        
        # Prendre les dernières barres
        seq_len = self.config.sequence_length
        if len(df) < seq_len:
            return "HOLD", 0.33
        
        # Préparer les features
        feature_columns = [col for col in self.config.features if col in df.columns]
        X = df[feature_columns].iloc[-seq_len:].values
        
        # Normaliser
        X_scaled = self.scaler.transform(X)
        
        # Reshape pour le modèle
        X_seq = X_scaled.reshape(1, seq_len, -1)
        
        # Prédiction
        prediction = self.model.predict(X_seq, verbose=0)[0]
        
        # Interpréter
        class_idx = np.argmax(prediction)
        confidence = float(prediction[class_idx])
        
        direction = ["SELL", "BUY", "HOLD"][class_idx]
        
        return direction, confidence
    
    def save_model(self, filepath: str):
        """Sauvegarder le modèle"""
        if self.model is None:
            raise ValueError("No model to save!")
        
        self.model.save(filepath)
        logger.info(f"💾 Model saved: {filepath}")
    
    def load_model(self, filepath: str):
        """Charger un modèle sauvegardé"""
        self.model = keras.models.load_model(filepath)
        logger.info(f"📂 Model loaded: {filepath}")


# ================================================================
# ENSEMBLE DE MODÈLES
# ================================================================

class EnsemblePredictor:
    """Ensemble de plusieurs modèles pour prédiction robuste"""
    
    def __init__(self):
        self.models = []
        self.weights = []
        
    def add_model(self, model, weight: float = 1.0):
        """Ajouter un modèle à l'ensemble"""
        self.models.append(model)
        self.weights.append(weight)
        
    def predict(self, df: pd.DataFrame) -> Tuple[str, float]:
        """Prédiction par ensemble"""
        if not self.models:
            return "HOLD", 0.33
        
        # Collecter les prédictions
        predictions = []
        confidences = []
        
        for model, weight in zip(self.models, self.weights):
            direction, confidence = model.predict(df)
            predictions.append(direction)
            confidences.append(confidence * weight)
        
        # Vote pondéré
        direction_scores = {
            "BUY": 0.0,
            "SELL": 0.0,
            "HOLD": 0.0
        }
        
        for pred, conf in zip(predictions, confidences):
            direction_scores[pred] += conf
        
        # Direction finale
        final_direction = max(direction_scores, key=direction_scores.get)
        final_confidence = direction_scores[final_direction] / sum(self.weights)
        
        return final_direction, final_confidence
