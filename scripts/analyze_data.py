from pyspark.sql import SparkSession
from pyspark.sql.functions import mean
import matplotlib.pyplot as plt

# Spark 세션 생성
spark = SparkSession.builder \
    .appName("EEG Data Analysis") \
    .getOrCreate()

# PostgreSQL에서 데이터 로드
jdbc_url = "jdbc:postgresql://<your_postgres_host>:<your_postgres_port>/<your_database>"
properties = {
    "user": "<your_username>",
    "password": "<your_password>",
    "driver": "org.postgresql.Driver"
}

# 데이터프레임으로 데이터 읽기
combined_df = spark.read.jdbc(url=jdbc_url, table="your_table_name", properties=properties)

# 필요한 변수 추출
# 특정 이벤트에 해당하는 데이터 필터링 (예: event_code가 1인 경우)
event_data = combined_df.filter(combined_df['event_code'] == 1)

# 평균 전압 계산
average_voltage = event_data.select(mean("voltage")).collect()[0][0]

# 시각화 준비
time_values = event_data.select("onset").toPandas()  # 시간 데이터 가져오기
voltage_values = event_data.select("voltage").toPandas()  # 전압 데이터 가져오기

# 시각화
plt.figure(figsize=(10, 6))
plt.plot(time_values, voltage_values, label='Voltage over Time')
plt.axhline(y=average_voltage, color='r', linestyle='--', label='Average Voltage')
plt.title('EEG Voltage Over Time for Specific Event')
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (µV)')
plt.legend()
plt.show()
