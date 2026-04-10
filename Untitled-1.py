# ============================
# 1. IMPORT LIBRARIES
# ============================
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

np.random.seed(42)

# ============================
# 2. CREATE SYNTHETIC DATA
# ============================
n = 1000

data = pd.DataFrame({
    "GSTIN": range(n),
    "turnover": np.random.uniform(1e5, 1e7, n),
    "electricity": np.random.uniform(1000, 50000, n),
    "freight": np.random.uniform(5000, 1e6, n),
    "employees": np.random.randint(1, 100, n)
})

# Simulate evaders (under-reporting)
evaders = np.random.choice(n, 80, replace=False)
data.loc[evaders, "turnover"] *= 0.3

# ============================
# 3. FEATURE ENGINEERING
# ============================
data["elec_ratio"] = data["electricity"] / data["turnover"]
data["freight_ratio"] = data["freight"] / data["turnover"]
data["emp_ratio"] = data["employees"] / data["turnover"]

features = ["elec_ratio", "freight_ratio", "emp_ratio"]

# Scale features
scaler = StandardScaler()
X = scaler.fit_transform(data[features])

# ============================
# 4. ANOMALY DETECTION
# ============================
model = IsolationForest(contamination=0.08, random_state=42)
data["anomaly_score"] = -model.fit_predict(X)  # higher = more anomalous

# ============================
# 5. RL: MULTI-ARMED BANDIT
# ============================

class Bandit:
    def __init__(self, n_arms):
        self.n_arms = n_arms
        self.values = np.zeros(n_arms)
        self.counts = np.zeros(n_arms)

    def select_arm(self):
        # epsilon-greedy
        epsilon = 0.1
        if np.random.rand() < epsilon:
            return np.random.randint(self.n_arms)
        return np.argmax(self.values)

    def update(self, arm, reward):
        self.counts[arm] += 1
        n = self.counts[arm]
        value = self.values[arm]
        self.values[arm] = ((n - 1) / n) * value + (1 / n) * reward


# ============================
# 6. GROUP BUSINESSES INTO ARMS
# ============================
# Example: group by anomaly score buckets
data["bucket"] = pd.qcut(data["anomaly_score"], q=5, labels=False)

bandit = Bandit(n_arms=5)

# ============================
# 7. SIMULATE AUDITS
# ============================
rewards = []

for _ in range(200):  # 200 audit rounds
    arm = bandit.select_arm()

    # pick random business from that bucket
    candidates = data[data["bucket"] == arm]
    sample = candidates.sample(1)

    idx = sample.index[0]

    # reward: 1 if evader, 0 otherwise
    reward = 1 if idx in evaders else 0

    bandit.update(arm, reward)
    rewards.append(reward)

# ============================
# 8. RESULTS
# ============================
print("Learned values (expected reward per bucket):")
print(bandit.values)

print("\nTotal reward (evaders caught):", sum(rewards))

# ============================
# 9. FINAL AUDIT PRIORITY
# ============================
top_businesses = data.sort_values("anomaly_score", ascending=False).head(10)

print("\nTop 10 Businesses for Audit:")
print(top_businesses[["GSTIN", "anomaly_score", "turnover"]])