import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import io
import base64
from scipy import signal
from sklearn.decomposition import PCA
from typing import List, Tuple
from .models import BCISession, BCIData

def generate_session_plots(session: BCISession, data_points: List[BCIData]) -> Tuple[io.BytesIO, io.BytesIO]:
    df = pd.DataFrame([
        {
            "timestamp": d.timestamp,
            "channel_1": d.channel_1,
            "channel_2": d.channel_2,
            "channel_3": d.channel_3,
            "channel_4": d.channel_4
        } for d in data_points
    ])
    
    if df.empty:
        return None, None

    # 시계열 플롯
    plt.figure(figsize=(10, 6))
    for channel in ['channel_1', 'channel_2', 'channel_3', 'channel_4']:
        plt.plot(df['timestamp'], df[channel], label=channel)
    plt.legend()
    plt.title('Channel Data Over Time')
    plt.xlabel('Timestamp')
    plt.ylabel('Channel Value')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    timeseries_plot = io.BytesIO()
    plt.savefig(timeseries_plot, format='png')
    timeseries_plot.seek(0)
    plt.close()

    # 채널 상관관계 히트맵
    plt.figure(figsize=(8, 6))
    correlation = df[['channel_1', 'channel_2', 'channel_3', 'channel_4']].corr()
    plt.imshow(correlation, cmap='coolwarm', aspect='auto')
    plt.colorbar()
    plt.xticks(range(4), ['Ch 1', 'Ch 2', 'Ch 3', 'Ch 4'])
    plt.yticks(range(4), ['Ch 1', 'Ch 2', 'Ch 3', 'Ch 4'])
    plt.title('Channel Correlation Heatmap')
    for i in range(4):
        for j in range(4):
            plt.text(j, i, f'{correlation.iloc[i, j]:.2f}', ha='center', va='center')
    plt.tight_layout()
    
    heatmap_plot = io.BytesIO()
    plt.savefig(heatmap_plot, format='png')
    heatmap_plot.seek(0)
    plt.close()

    return timeseries_plot, heatmap_plot

def preprocess_eeg_data(data: np.ndarray, sampling_rate: float) -> np.ndarray:
    # Apply a bandpass filter (1-50 Hz)
    b, a = signal.butter(4, [1, 50], btype='bandpass', fs=sampling_rate)
    filtered_data = signal.filtfilt(b, a, data, axis=0)
    
    # Apply a notch filter to remove 60 Hz noise
    notch_freq = 60.0
    quality_factor = 30.0
    b_notch, a_notch = signal.iirnotch(notch_freq, quality_factor, sampling_rate)
    notched_data = signal.filtfilt(b_notch, a_notch, filtered_data, axis=0)
    
    return notched_data

def extract_features(data: np.ndarray) -> np.ndarray:
    # Extract basic statistical features
    mean = np.mean(data, axis=0)
    std = np.std(data, axis=0)
    max_val = np.max(data, axis=0)
    min_val = np.min(data, axis=0)
    
    # Perform PCA
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(data)
    
    # Combine all features
    features = np.concatenate([mean, std, max_val, min_val, pca_result.flatten()])
    
    return features

def analyze_session_data(session: BCISession, data_points: List[BCIData]) -> dict:
    df = pd.DataFrame([
        {
            "timestamp": d.timestamp,
            "channel_1": d.channel_1,
            "channel_2": d.channel_2,
            "channel_3": d.channel_3,
            "channel_4": d.channel_4
        } for d in data_points
    ])
    
    data = df[['channel_1', 'channel_2', 'channel_3', 'channel_4']].values
    
    # Preprocess the data
    sampling_rate = 250  # Assume 250 Hz sampling rate, adjust as needed
    preprocessed_data = preprocess_eeg_data(data, sampling_rate)
    
    # Extract features
    features = extract_features(preprocessed_data)
    
    # Perform basic analysis
    channel_means = np.mean(preprocessed_data, axis=0)
    channel_stds = np.std(preprocessed_data, axis=0)
    
    return {
        "session_id": session.id,
        "num_data_points": len(data_points),
        "channel_means": channel_means.tolist(),
        "channel_stds": channel_stds.tolist(),
        "extracted_features": features.tolist()
    }