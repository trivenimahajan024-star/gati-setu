import os
import sys
import csv
import json
import math
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

import numpy as np

# Ensure backend directory in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


class DecisionTreeNode:
    def __init__(self, feature_idx: int = -1, threshold: float = 0.0, left = None, right = None, value: float = 0.0):
        self.feature_idx = feature_idx
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value

    @property
    def is_leaf(self) -> bool:
        return self.left is None and self.right is None

    def to_dict(self) -> Dict[str, Any]:
        if self.is_leaf:
            return {"leaf_value": float(self.value)}
        return {
            "feature_idx": int(self.feature_idx),
            "threshold": float(self.threshold),
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]):
        if not d:
            return None
        if "leaf_value" in d:
            return cls(value=d["leaf_value"])
        left = cls.from_dict(d.get("left"))
        right = cls.from_dict(d.get("right"))
        return cls(feature_idx=d["feature_idx"], threshold=d["threshold"], left=left, right=right)

    def predict_one(self, x: np.ndarray) -> float:
        if self.is_leaf:
            return self.value
        if x[self.feature_idx] <= self.threshold:
            return self.left.predict_one(x) if self.left else self.value
        else:
            return self.right.predict_one(x) if self.right else self.value


class GBDTRegressor:
    """
    High-Performance Gradient Boosted Decision Tree (XGBoost Algorithm Formulation).
    Optimizes Mean Squared Error with L2 Leaf Weight Regularization and Feature Subsampling.
    """
    def __init__(self, n_estimators: int = 80, learning_rate: float = 0.08, max_depth: int = 5,
                 min_samples_leaf: int = 15, reg_lambda: float = 1.0, subsample: float = 0.85):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.reg_lambda = reg_lambda
        self.subsample = subsample
        self.trees: List[DecisionTreeNode] = []
        self.base_pred = 0.0
        self.feature_names: List[str] = []

    def _fit_tree(self, X: np.ndarray, residuals: np.ndarray, depth: int) -> DecisionTreeNode:
        n_samples, n_features = X.shape
        leaf_val = float(np.sum(residuals) / (n_samples + self.reg_lambda))

        if depth >= self.max_depth or n_samples < self.min_samples_leaf * 2:
            return DecisionTreeNode(value=leaf_val)

        best_gain = 0.0
        best_feat = -1
        best_thresh = 0.0
        best_left_mask = None

        parent_g = np.sum(residuals)
        parent_score = (parent_g ** 2) / (n_samples + self.reg_lambda)

        feat_indices = np.random.choice(n_features, size=max(1, int(n_features * self.subsample)), replace=False)

        for f_idx in feat_indices:
            feat_vals = X[:, f_idx]
            unique_vals = np.unique(feat_vals)
            if len(unique_vals) <= 1:
                continue
            
            thresholds = np.percentile(unique_vals, np.linspace(10, 90, 8))
            for thresh in thresholds:
                left_mask = feat_vals <= thresh
                n_left = np.count_nonzero(left_mask)
                n_right = n_samples - n_left

                if n_left < self.min_samples_leaf or n_right < self.min_samples_leaf:
                    continue

                g_left = np.sum(residuals[left_mask])
                g_right = parent_g - g_left

                score_left = (g_left ** 2) / (n_left + self.reg_lambda)
                score_right = (g_right ** 2) / (n_right + self.reg_lambda)

                gain = 0.5 * (score_left + score_right - parent_score)
                if gain > best_gain:
                    best_gain = gain
                    best_feat = f_idx
                    best_thresh = float(thresh)
                    best_left_mask = left_mask

        if best_gain <= 0.001 or best_left_mask is None:
            return DecisionTreeNode(value=leaf_val)

        left_child = self._fit_tree(X[best_left_mask], residuals[best_left_mask], depth + 1)
        right_child = self._fit_tree(X[~best_left_mask], residuals[~best_left_mask], depth + 1)
        return DecisionTreeNode(feature_idx=best_feat, threshold=best_thresh, left=left_child, right=right_child)

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: List[str] = None):
        self.feature_names = feature_names or [f"f_{i}" for i in range(X.shape[1])]
        self.base_pred = float(np.mean(y))
        y_pred = np.full(len(y), self.base_pred, dtype=np.float32)

        self.trees = []
        for i in range(self.n_estimators):
            residuals = y - y_pred
            if self.subsample < 1.0:
                idx = np.random.choice(len(y), size=int(len(y) * self.subsample), replace=False)
                tree = self._fit_tree(X[idx], residuals[idx], depth=0)
            else:
                tree = self._fit_tree(X, residuals, depth=0)

            step_preds = np.array([tree.predict_one(x) for x in X], dtype=np.float32)
            y_pred += self.learning_rate * step_preds
            self.trees.append(tree)

    def predict(self, X: np.ndarray) -> np.ndarray:
        preds = np.full(len(X), self.base_pred, dtype=np.float32)
        for tree in self.trees:
            step = np.array([tree.predict_one(x) for x in X], dtype=np.float32)
            preds += self.learning_rate * step
        return preds

    def save_model(self, file_path: str):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        data = {
            "model_type": "XGBoost_GBDT_Regressor_v1",
            "n_estimators": len(self.trees),
            "learning_rate": self.learning_rate,
            "max_depth": self.max_depth,
            "base_pred": self.base_pred,
            "feature_names": self.feature_names,
            "trees": [t.to_dict() for t in self.trees]
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_model(self, file_path: str) -> bool:
        if not os.path.exists(file_path):
            return False
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.learning_rate = data.get("learning_rate", 0.08)
            self.max_depth = data.get("max_depth", 5)
            self.base_pred = data.get("base_pred", 0.0)
            self.feature_names = data.get("feature_names", [])
            self.trees = [DecisionTreeNode.from_dict(t) for t in data.get("trees", [])]
            return len(self.trees) > 0
        except Exception:
            return False


def parse_minutes_from_time(t_str: str, day: int = 1) -> int:
    if not t_str or ":" not in t_str:
        return 0
    p = t_str.split(":")
    return (day - 1) * 1440 + int(p[0]) * 60 + int(p[1])


def run_training_pipeline(data_dir: str = "backend/data", model_output_path: str = "backend/app/models/xgboost_eta_regressor.json") -> Dict[str, Any]:
    print("==================================================================", flush=True)
    print("  [GatiSetu] Real Indian Railways Dataset Training Pipeline", flush=True)
    print("==================================================================", flush=True)
    t0 = time.time()

    schedule_path = os.path.join(data_dir, "combined_schedule.csv")
    delay_path = os.path.join(data_dir, "combined_delay.csv")
    train_details_path = os.path.join(data_dir, "train_details.csv")

    for p in [schedule_path, delay_path, train_details_path]:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Required dataset file not found: {p}")

    # 1. Load Train Schedule Dimension
    print("\n[1] Ingesting combined_schedule.csv ...", flush=True)
    schedules = {}
    with open(schedule_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            tno = str(r["train_no"]).strip().lstrip("0") or "0"
            if tno not in schedules:
                schedules[tno] = []
            try:
                dist = float(r["distance_from_origin"]) if r["distance_from_origin"] else 0.0
                stn_no = int(r["station_no"]) if r["station_no"] else 0
            except ValueError:
                continue
            schedules[tno].append({
                "station_no": stn_no,
                "station_name": r["station_name"].strip(),
                "distance": dist,
                "arr_day": int(r["arrival_day"]) if r.get("arrival_day") and r["arrival_day"].isdigit() else 1,
                "dep_day": int(r["departure_day"]) if r.get("departure_day") and r["departure_day"].isdigit() else 1,
                "arr_time": r["arrival_time"].strip() if r["arrival_time"] else "",
                "dep_time": r["departure_time"].strip() if r["departure_time"] else ""
            })

    for tno in schedules:
        schedules[tno].sort(key=lambda x: x["station_no"])

    print(f"  Ingested schedule timelines for {len(schedules):,} unique train routes.", flush=True)

    # 2. Ingest train delay observations
    print("\n[2] Ingesting & indexing delay observations from combined_delay.csv ...", flush=True)
    
    target_train_patterns = {
        '12951', '12860', '22436', '12002', '12259', '12952', '12859', '22435', '12001', '12260',
        '12301', '12302', '12423', '12424', '12953', '12954', '12004', '12005', '12213', '12214',
        '12625', '12626', '12723', '12724', '12431', '12432', '12137', '12138', '12925', '12926',
        '12417', '12418', '12555', '12556', '12779', '12780', '12839', '12840', '12903', '12904',
        '12919', '12920', '12471', '12472', '12481', '12482', '12011', '12012', '12049', '12050',
        '12295', '12296', '12393', '12394', '12617', '12618', '12621', '12622', '12721', '12722',
        '12801', '12802', '12909', '12910', '12957', '12958', '22691', '22692', '22693', '22694',
        '12269', '12270', '12309', '12310', '12425', '12426', '12433', '12434', '12955', '12956'
    }

    delays_by_trip = {}
    with open(delay_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            tno = str(r["train_no"]).strip().lstrip("0") or "0"
            if tno in target_train_patterns:
                dt = r["date"].strip()
                key = (tno, dt)
                if key not in delays_by_trip:
                    delays_by_trip[key] = {}
                d_val = r["delay"].strip()
                if d_val != "":
                    try:
                        d_float = float(d_val)
                        if d_float > 400000:
                            d_float = 525600.0 - d_float
                        delays_by_trip[key][int(r["station_no"])] = d_float
                    except ValueError:
                        pass

    print(f"  Indexed {len(delays_by_trip):,} trip runs across {len(target_train_patterns)} train services.", flush=True)

    # 3. Construct Feature Matrix & Ground-Truth Remaining Time
    print("\n[3] Engineering features and computing ground-truth actual_remaining_minutes ...", flush=True)

    feature_cols = [
        "distance_covered_km", "distance_remaining_km", "total_distance_km",
        "journey_progress_pct", "current_speed_kmh", "current_delay_mins",
        "total_halts_count", "remaining_halts_count", "scheduled_remaining_duration_mins",
        "scheduled_avg_speed_kmh", "current_hour", "day_of_week", "is_weekend",
        "has_active_events", "event_delay_impact_sum"
    ]

    all_samples = []

    for (tno, dt_str), delays in delays_by_trip.items():
        stn_list = schedules.get(tno)
        if not stn_list or len(stn_list) < 3:
            continue

        dest_stn = stn_list[-1]
        dest_stn_no = dest_stn["station_no"]
        dest_delay = delays.get(dest_stn_no)
        
        if dest_delay is None and len(stn_list) >= 2:
            dest_delay = delays.get(stn_list[-2]["station_no"])

        if dest_delay is None:
            continue

        total_dist = dest_stn["distance"]
        if total_dist <= 0:
            continue

        try:
            dt_obj = datetime.strptime(dt_str, "%Y-%m-%d")
        except ValueError:
            continue

        day_of_week = dt_obj.weekday()
        is_weekend = 1 if day_of_week in (5, 6) else 0

        dest_sched_arr_mins = parse_minutes_from_time(dest_stn["arr_time"] or dest_stn["dep_time"], dest_stn["arr_day"])
        total_halts = len(stn_list)

        for idx, stn in enumerate(stn_list[:-1]):
            stn_no = stn["station_no"]
            cur_delay = delays.get(stn_no)
            if cur_delay is None:
                continue

            cur_dist = stn["distance"]
            dist_rem = max(0.0, total_dist - cur_dist)
            prog_pct = round((cur_dist / total_dist) * 100.0, 2)
            rem_halts = total_halts - (idx + 1)

            cur_sched_dep_mins = parse_minutes_from_time(stn["dep_time"] or stn["arr_time"], stn["dep_day"])
            sched_rem_mins = max(1.0, float(dest_sched_arr_mins - cur_sched_dep_mins))

            # Ground-truth continuous target:
            # actual_remaining_minutes = scheduled_remaining_duration + (dest_delay - cur_delay)
            actual_rem_mins = max(0.0, sched_rem_mins + (dest_delay - cur_delay))

            cur_hour = int(stn["dep_time"].split(":")[0]) if ":" in stn["dep_time"] else 12
            sched_avg_speed = round(total_dist / (max(1.0, dest_sched_arr_mins) / 60.0), 1) if dest_sched_arr_mins > 0 else 80.0
            cur_speed = round(max(35.0, min(130.0, sched_avg_speed - (cur_delay * 0.15))), 1)

            has_events = 1 if cur_delay >= 15 else 0
            event_impact = cur_delay if cur_delay >= 15 else 0.0

            all_samples.append({
                "date": dt_str,
                "train_no": tno,
                "features": [
                    cur_dist, dist_rem, total_dist, prog_pct,
                    cur_speed, cur_delay, total_halts, rem_halts,
                    sched_rem_mins, sched_avg_speed, cur_hour,
                    day_of_week, is_weekend, has_events, event_impact
                ],
                "target": actual_rem_mins
            })

    print(f"  Constructed {len(all_samples):,} leak-free training snapshots.", flush=True)

    # 4. Chronological Train / Validation Split (80% / 20%)
    print("\n[4] Performing Chronological Holdout Split (80% Train, 20% Validation) ...", flush=True)
    all_samples.sort(key=lambda s: s["date"])
    split_idx = int(len(all_samples) * 0.80)

    train_samples = all_samples[:split_idx]
    val_samples = all_samples[split_idx:]

    X_train = np.array([s["features"] for s in train_samples], dtype=np.float32)
    y_train = np.array([s["target"] for s in train_samples], dtype=np.float32)

    X_val = np.array([s["features"] for s in val_samples], dtype=np.float32)
    y_val = np.array([s["target"] for s in val_samples], dtype=np.float32)

    print(f"  Training Split   : {len(X_train):,} snapshots ({train_samples[0]['date']} to {train_samples[-1]['date']})", flush=True)
    print(f"  Validation Split : {len(X_val):,} snapshots ({val_samples[0]['date']} to {val_samples[-1]['date']})", flush=True)

    # 5. Train XGBoost Regressor Ensemble
    print("\n[5] Training XGBoost GBDT Regressor (80 Trees, Depth 5, Learning Rate 0.08) ...", flush=True)
    model = GBDTRegressor(n_estimators=80, learning_rate=0.08, max_depth=5, min_samples_leaf=15, reg_lambda=1.5, subsample=0.85)
    model.fit(X_train, y_train, feature_names=feature_cols)

    # 6. Evaluate on Validation Set
    print("\n[6] Evaluating Model Performance on Unseen Holdout Set ...", flush=True)
    val_preds = model.predict(X_val)
    mae = float(np.mean(np.abs(val_preds - y_val)))
    rmse = float(np.sqrt(np.mean((val_preds - y_val) ** 2)))

    sched_rem_idx = feature_cols.index("scheduled_remaining_duration_mins")
    sched_baseline_mae = float(np.mean(np.abs(X_val[:, sched_rem_idx] - y_val)))

    print(f"  Validation MAE   : {mae:.2f} minutes (Baseline Scheduled MAE: {sched_baseline_mae:.2f} min)", flush=True)
    print(f"  Validation RMSE  : {rmse:.2f} minutes", flush=True)
    print(f"  Accuracy Gain    : {((sched_baseline_mae - mae) / sched_baseline_mae * 100):.1f}% reduction in error over static timetable!", flush=True)

    # 7. Save Model
    print(f"\n[7] Saving Model to: {model_output_path} ...", flush=True)
    model.save_model(model_output_path)
    print("  Model serialized successfully.", flush=True)

    total_time = round(time.time() - t0, 2)
    print(f"\n==================================================================", flush=True)
    print(f"  XGBOOST TRAINING COMPLETED SUCCESSFULLY IN {total_time}s!", flush=True)
    print(f"==================================================================\n", flush=True)

    return {
        "status": "SUCCESS",
        "train_rows": len(X_train),
        "val_rows": len(X_val),
        "total_rows": len(all_samples),
        "mae_minutes": round(mae, 2),
        "rmse_minutes": round(rmse, 2),
        "model_path": model_output_path,
        "feature_count": len(feature_cols),
        "feature_columns": feature_cols,
        "train_date_range": f"{train_samples[0]['date']} to {train_samples[-1]['date']}",
        "val_date_range": f"{val_samples[0]['date']} to {val_samples[-1]['date']}"
    }

if __name__ == "__main__":
    res = run_training_pipeline()
