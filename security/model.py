import pandas as pd
from sklearn.linear_model import LogisticRegression
import os
from datetime import datetime

# ================= LOAD DATA =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "../linux_auth_logs_labeled.csv")

df = pd.read_csv(csv_path)

df['timestamp'] = pd.to_datetime(df['timestamp'])
df['Login_Hour'] = df['timestamp'].dt.hour
df['Failed_Login'] = df['status'].apply(lambda x: 1 if str(x).lower() == 'fail' else 0)

# ================= CREATE LABEL =================
df['Final_Suspicious'] = 0
df.loc[df['attempts'] > 5, 'Final_Suspicious'] = 1
df.loc[(df['Login_Hour'] >= 0) & (df['Login_Hour'] <= 5), 'Final_Suspicious'] = 1
df.loc[df['Failed_Login'] == 1, 'Final_Suspicious'] = 1

features = ['attempts', 'Login_Hour', 'Failed_Login']

X = df[features]
y = df['Final_Suspicious']

model = LogisticRegression()
model.fit(X, y)


# ================= PREDICTION FUNCTION =================
def predict_login(login_attempts):
    input_data = pd.DataFrame([{
        "attempts": login_attempts,
        "Login_Hour": datetime.now().hour,
        "Failed_Login": 1 if login_attempts > 2 else 0
    }])

    prediction = model.predict(input_data)[0]

    return "SUSPICIOUS" if prediction == 1 else "NORMAL"


# ================= DATE RANGE FUNCTION =================
def analyze_date_range(start_date, end_date):
    df_filtered = df[
        (df['timestamp'] >= start_date) &
        (df['timestamp'] <= end_date)
    ].copy()

    if df_filtered.empty:
        return {
            "total": 0,
            "suspicious": 0,
            "normal": 0
        }, None

    predictions = model.predict(df_filtered[features])
    df_filtered['ML_Result'] = predictions

    total = len(df_filtered)
    suspicious = int(df_filtered['ML_Result'].sum())
    normal = total - suspicious

    hidden_data = df_filtered[df_filtered['ML_Result'] == 1][
        ['source_ip', 'timestamp']
    ]

    result = {
        "total": total,
        "suspicious": suspicious,
        "normal": normal
    }

    return result, hidden_data
