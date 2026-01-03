import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
import joblib

DATA_PATH = "data/events_stockholm.csv"
MODEL_PATH = "scoring_model.pkl"

df = pd.read_csv(DATA_PATH)

# features
FEATURES_NUM = ["days_ahead", "is_weekend", "hour", "span_multiple_days"]
FEATURES_CAT = ["segment"]

# 关键：scoring 目标（连续值），不再用 y_good_hangout
# 最小可解释版本：越近的活动得分越高 + 周末/晚上加分
# 这是“proxy score”，模型学的是这些特征如何组合成分数（用于排序）
df["_date"] = pd.to_datetime(df["localDate"], errors="coerce")
df = df.dropna(subset=["_date"]).sort_values("_date").reset_index(drop=True)

# hour 缺失 -> -1，先补一下
df["hour"] = df["hour"].fillna(-1)

# 构造一个连续 target：base = -days_ahead（越近越高）
# 加一点简单偏好项：周末加 0.5，晚上(18-22)加 0.3
evening = df["hour"].between(18, 22).astype(int)
y = (-df["days_ahead"]).astype(float) + 0.5 * df["is_weekend"] + 0.3 * evening

X = df[FEATURES_NUM + FEATURES_CAT]

preprocess = ColumnTransformer(
    transformers=[
        ("num", "passthrough", FEATURES_NUM),
        ("cat", OneHotEncoder(handle_unknown="ignore"), FEATURES_CAT),
    ]
)

# Ridge：稳定、快，不要求两类样本
pipe = Pipeline(
    steps=[
        ("prep", preprocess),
        ("reg", Ridge(alpha=1.0))
    ]
)

pipe.fit(X, y)

joblib.dump(pipe, MODEL_PATH)
print("Saved scoring model to", MODEL_PATH)
print("Trained on rows:", len(df))
