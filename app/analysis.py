import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import io

def generate_session_plots(session, data_points):
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