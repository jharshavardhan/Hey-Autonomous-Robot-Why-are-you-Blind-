# 🤖 Hey Autonomous Vacuum Cleaner! Why Are You Blind?
### AI-Powered Visual Dirt Detection for Robot Vacuums

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![YOLOv8](https://img.shields.io/badge/YOLOv8s-mAP50%3A90%25-green)
![License](https://img.shields.io/badge/License-MIT-yellow)


> A real-time computer vision system that gives robot vacuums the ability to **see and understand** floor-level dirt — enabling zone-targeted, adaptive cleaning instead of blind scheduled sweeps.

---

## 📌 Overview

Modern autonomous vacuum cleaners excel at navigation, but they are fundamentally **blind** — they clean on a schedule, not on demand. They cannot detect what they're cleaning, distinguish dirt types, or adapt their behavior accordingly.

This project solves that by training and comparing three deep learning models (MobileNetV2, ResNet50, and YOLOv8s) on real floor images to detect 4 dirt classes in real time, and integrating the winning model into a full robotic pipeline on NVIDIA Jetson Nano with ROS2.

---

## 🧠 The Problem

| Limitation | Impact |
|---|---|
| Fixed Schedule | Wastes energy cleaning already-clean floors |
| No Dirt Detection | Cannot adapt cleaning mode to dirt type |
| No Localization | Cleans entire floor instead of dirty zones only |
| Liquid Blindness | Risks vacuuming liquid — permanently damages motor |
| No Adaptive Suction | Full power even on clean floors (20–40% battery wasted) |
| No Learning | Repeats the same path every session |

---

## ✅ Solution

**YOLOv8s object detection** trained on real floor images to detect dirt with bounding boxes, enabling:
- Precise **zone-targeted cleaning**
- **Adaptive suction control** based on dirt class
- **Real-time inference** (<100ms per frame on Jetson Nano)

---

## 📊 Dataset

- **Source:** [Kaggle — alyyan/trash-detection](https://www.kaggle.com/datasets/alyyan/trash-detection)
- Real floor images captured from a vacuum camera perspective
- **4 dirt classes:** Dirt, Liquid, Marks, Trash
- **1 clean class:** Nothing detected
- Varied surfaces: tiles, wood, carpet
- Varied lighting conditions and camera angles
- Used for YOLOv8s bounding box training AND ResNet50/MobileNetV2 classification comparison

---

## 🏗️ Model Comparison

| Metric | MobileNetV2 | ResNet50 | YOLOv8s |
|---|---|---|---|
| Stability | ⚠️ Dip at Phase 2 | ❌ Catastrophic crash | ✅ Smooth throughout |
| Final Accuracy | ✅ 93% val | ⚠️ ~90% but erratic | ✅ 95% mAP50 |
| Overfitting | ✅ None | ❌ Unstable | ✅ None |
| Detects Location | ❌ | ❌ | ✅ |
| Deployment Ready | ⚠️ Maybe | ❌ No | ✅ Yes |

### Key Findings

**MobileNetV2** — ~35% accuracy overall. Significant overfitting; minority classes (liquid, marks) near 0% recall. Transfer learning from ImageNet doesn't generalize to floor dirt.

**ResNet50** — ~29% accuracy. Class collapse observed — model converges to predicting the dominant class only. Too heavy for embedded real-time inference on Jetson Nano.

**YOLOv8s** — mAP50: ~90%. Detects all 4 dirt classes with bounding boxes. Each class achieves F1 ≈ 0.90. Real-time capable and selected as the final deployment model.

---
<p float="left">
  
  <img alt="mobilenetV2 confusion mtx" src="https://github.com/user-attachments/assets/3deba0af-cc0e-4adc-8c39-6ca79374d502" width = "33%" />
  <img alt="YOLOv8 confusion mtx" src="https://github.com/user-attachments/assets/09d6493c-c8fa-47f0-918b-4b96784b38d2" width = "33%"  />
  <img alt="resnet50 confusion mtx" src="https://github.com/user-attachments/assets/9cc19646-3804-4f76-999c-3699ae1831ae" width = "33%"  />
</p>

---

### dirt prediction
<p float ="left">
  

  <img alt="download" src="https://github.com/user-attachments/assets/5f8d28f5-b7e4-4286-8122-650142628501" width = "50%"/>

  <img alt="yolov8 image predic 2" src="https://github.com/user-attachments/assets/bc414b12-8f90-4168-9497-0ba910898e17" width = "50%" />

</p>

---

## Simulation of Vacuum Cleaner

<img width="1919" height="910" alt="Screenshot 2026-04-25 195554" src="https://github.com/user-attachments/assets/312474c4-802b-4b4f-9a48-545fbc583e0c" />





