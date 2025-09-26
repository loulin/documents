# 医疗设备综合对接技术方案

## 概述

本文档全面介绍各类医疗监测设备的对接技术方案，涵盖血糖仪、血压计、心电图、体重秤、血氧仪等常见医疗设备的API/SDK集成方法。

## 📊 设备支持总览

| 设备类型 | 主要厂商 | 支持数量 | 技术方案 | 文档状态 |
|----------|----------|----------|----------|----------|
| **血糖仪** | Abbott, Roche, OneTouch, 三诺 | 8+ | Bluetooth GATT + API | ✅ 完整 |
| **血压计** | Omron, iHealth, 九安 | 6+ | Bluetooth + WiFi API | ✅ 完整 |
| **心电图** | 华为, 小米, Polar | 5+ | BLE + 云端API | ✅ 完整 |
| **体成分** | InBody, 欧姆龙, 华为 | 4+ | 专业API + BLE | ✅ 完整 |
| **血氧仪** | 鱼跃, Nonin, 小米 | 4+ | BLE + 医疗级协议 | ✅ 完整 |

**相关文档**:
- [血糖仪技术方案](./BGM.md) - 指尖血糖监测仪详细对接方案
- [本文档] - 综合医疗设备集成指南

## 设备分类和对接方案

### 1. 🩸 血压监测设备

#### 主要厂商和产品
| 厂商 | 产品系列 | 连接方式 | API支持 | 集成难度 |
|------|----------|----------|---------|----------|
| **Omron (欧姆龙)** | HeartGuide, BP7900 | Bluetooth/WiFi | 有限开放 | 中等 |
| **A&D Medical** | UA-767PBT, UA-651SL | Bluetooth | 支持 | 低 |
| **Beurer** | BM系列 | Bluetooth | 开源支持 | 低 |
| **iHealth** | BP系列 | Bluetooth/WiFi | SDK支持 | 低 |

#### 技术实现方案

**Omron血压计对接**
```javascript
// Omron Connect API集成
class OmronBloodPressureAPI {
    constructor(apiKey, deviceId) {
        this.apiKey = apiKey;
        this.deviceId = deviceId;
        this.baseURL = 'https://api.omronhealthcare.com';
    }
    
    async getBloodPressureData(patientId, dateRange) {
        const response = await fetch(`${this.baseURL}/v1/bloodpressure`, {
            headers: {
                'Authorization': `Bearer ${this.apiKey}`,
                'Content-Type': 'application/json'
            },
            method: 'GET',
            params: {
                patient_id: patientId,
                start_date: dateRange.start,
                end_date: dateRange.end
            }
        });
        
        return response.json();
    }
    
    async syncRealTimeData() {
        // 实时数据同步
        const measurement = await this.readBluetoothData();
        return {
            systolic: measurement.systolic,
            diastolic: measurement.diastolic,
            pulse: measurement.pulse,
            timestamp: new Date().toISOString(),
            deviceId: this.deviceId
        };
    }
}
```

**iHealth血压计SDK**
```java
// Android iHealth SDK集成
public class iHealthBPManager {
    private iHealthDevicesManager ihealthManager;
    private Bp5Manager bp5Manager;
    
    public void initializeSDK() {
        ihealthManager = iHealthDevicesManager.getInstance();
        ihealthManager.init(context);
        
        // 设置血压计回调
        bp5Manager = ihealthManager.getBp5Manager();
        bp5Manager.setListener(new Bp5Listener() {
            @Override
            public void onMeasurementResult(int systolic, int diastolic, int pulse) {
                // 处理血压测量结果
                handleBPMeasurement(systolic, diastolic, pulse);
            }
            
            @Override
            public void onDeviceConnected() {
                Log.d("iHealth", "血压计连接成功");
            }
        });
    }
    
    private void handleBPMeasurement(int systolic, int diastolic, int pulse) {
        BloodPressureReading reading = new BloodPressureReading();
        reading.setSystolic(systolic);
        reading.setDiastolic(diastolic);
        reading.setPulse(pulse);
        reading.setTimestamp(new Date());
        
        // 保存到数据库或上传到服务器
        saveToDatabase(reading);
    }
}
```

### 2. ❤️ 心电图/心率设备

#### 主要集成平台
| 平台 | 支持设备 | 特点 | 成本 |
|------|----------|------|------|
| **Vitalera SDK** | 700+设备 | 全面支持 | 商业授权 |
| **MedM SDK** | 500+设备 | RPM专用 | 按设备付费 |
| **Shen AI** | 摄像头心率 | 无需硬件 | 按API调用 |
| **Apple HealthKit** | 兼容设备 | iOS原生 | 免费 |

#### 技术实现方案

**Vitalera多设备集成**
```python
# Vitalera SDK Python集成
import vitalera_sdk

class VitaleraHealthMonitor:
    def __init__(self, api_key):
        self.client = vitalera_sdk.Client(api_key)
        
    def connect_ecg_device(self, device_type, device_id):
        """连接心电图设备"""
        device = self.client.connect_device(
            device_type=device_type,  # 'ecg', 'heart_rate', 'blood_pressure'
            device_id=device_id
        )
        
        # 设置数据回调
        device.on_data_received(self.handle_ecg_data)
        return device
    
    def handle_ecg_data(self, data):
        """处理心电图数据"""
        ecg_reading = {
            'heart_rate': data.heart_rate,
            'rr_intervals': data.rr_intervals,
            'hrv': self.calculate_hrv(data.rr_intervals),
            'timestamp': data.timestamp,
            'device_id': data.device_id
        }
        
        # 异常检测
        if self.detect_arrhythmia(data.ecg_signal):
            ecg_reading['alert'] = 'possible_arrhythmia'
        
        return ecg_reading
    
    def calculate_hrv(self, rr_intervals):
        """计算心率变异性"""
        if len(rr_intervals) < 2:
            return None
            
        # RMSSD计算
        diff_rr = [abs(rr_intervals[i+1] - rr_intervals[i]) 
                   for i in range(len(rr_intervals)-1)]
        rmssd = (sum(x**2 for x in diff_rr) / len(diff_rr)) ** 0.5
        
        return {
            'rmssd': rmssd,
            'avg_rr': sum(rr_intervals) / len(rr_intervals),
            'sdnn': self.calculate_sdnn(rr_intervals)
        }
```

**Shen AI摄像头心率监测**
```javascript
// Shen AI 摄像头心率检测
class ShenAIHeartRate {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.sdk = new ShenAI.SDK(apiKey);
    }
    
    async startCameraMonitoring(videoElement) {
        try {
            // 初始化摄像头监测
            const session = await this.sdk.createSession({
                videoElement: videoElement,
                metrics: ['heart_rate', 'hrv', 'stress_level'],
                duration: 30 // 30秒扫描
            });
            
            // 实时数据回调
            session.onData((data) => {
                this.handleHeartRateData(data);
            });
            
            // 开始监测
            await session.start();
            
        } catch (error) {
            console.error('心率监测启动失败:', error);
        }
    }
    
    handleHeartRateData(data) {
        const heartRateData = {
            heart_rate: data.heart_rate,
            hrv_score: data.hrv,
            stress_level: data.stress,
            confidence: data.confidence,
            timestamp: new Date().toISOString()
        };
        
        // 发送到服务器
        this.sendToServer(heartRateData);
    }
    
    async sendToServer(data) {
        await fetch('/api/health/heart-rate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    }
}
```

### 3. ⚖️ 体重秤/体成分分析

#### 主要厂商方案
| 厂商 | API支持 | 数据类型 | 集成方式 |
|------|---------|----------|----------|
| **InBody** | 完整API+SDK | 20+项专业体成分 | Web API/蓝牙SDK |
| **Withings** | 完整API | 13项体成分 | OAuth 2.0 |
| **Fitbit Aria** | Web API | 基础体重+体脂 | Fitbit API |
| **Tuya平台** | 开放API | 自定义 | 云端API |
| **RENPHO** | 第三方集成 | 8项指标 | HealthKit/Google Fit |

#### 技术实现方案

**InBody专业体成分分析仪集成**

**方案1：Web API云端集成（推荐）**
```python
# InBody LookinBody Web API集成
import requests
from datetime import datetime
import json

class InBodyWebAPI:
    def __init__(self, region='usa', api_key=None, username=None, password=None):
        """
        初始化InBody Web API
        region: 'usa', 'eur', 'asia', 'uk'
        """
        self.base_urls = {
            'usa': 'https://apiusa.lookinbody.com',
            'eur': 'https://apieur.lookinbody.com', 
            'asia': 'https://inbodyasia.com',
            'uk': 'https://uk.lookinbody.com'
        }
        self.base_url = self.base_urls.get(region, self.base_urls['usa'])
        self.api_key = api_key
        self.username = username
        self.password = password
        self.access_token = None
    
    async def authenticate(self):
        """认证获取访问令牌"""
        auth_url = f"{self.base_url}/api/auth/login"
        
        auth_data = {
            'username': self.username,
            'password': self.password,
            'api_key': self.api_key
        }
        
        response = requests.post(auth_url, json=auth_data)
        
        if response.status_code == 200:
            result = response.json()
            self.access_token = result.get('access_token')
            return True
        else:
            print(f"认证失败: {response.status_code}")
            return False
    
    async def get_user_measurements(self, user_id, start_date=None, end_date=None):
        """获取用户体成分测量数据"""
        if not self.access_token:
            await self.authenticate()
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-API-KEY': self.api_key
        }
        
        params = {'user_id': user_id}
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()
        
        response = requests.get(
            f"{self.base_url}/api/measurements",
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            return self.parse_inbody_data(response.json())
        else:
            print(f"获取数据失败: {response.status_code}")
            return None
    
    def parse_inbody_data(self, raw_data):
        """解析InBody体成分数据"""
        measurements = []
        
        for measurement in raw_data.get('data', []):
            parsed_measurement = {
                # 基础信息
                'measurement_id': measurement.get('id'),
                'user_id': measurement.get('user_id'),
                'test_date': measurement.get('test_date'),
                'device_model': measurement.get('device_model'),
                
                # 基础体成分
                'weight': measurement.get('weight'),  # 体重 (kg)
                'height': measurement.get('height'),  # 身高 (cm)
                'bmi': measurement.get('bmi'),        # BMI
                
                # 体成分分析
                'body_fat_mass': measurement.get('body_fat_mass'),      # 体脂肪量 (kg)
                'body_fat_percentage': measurement.get('body_fat_percentage'),  # 体脂率 (%)
                'skeletal_muscle_mass': measurement.get('skeletal_muscle_mass'), # 骨骼肌量 (kg)
                'muscle_mass': measurement.get('muscle_mass'),          # 肌肉量 (kg)
                'total_body_water': measurement.get('total_body_water'), # 体水分 (L)
                'protein': measurement.get('protein'),                  # 蛋白质 (kg)
                'mineral': measurement.get('mineral'),                  # 无机盐 (kg)
                
                # 节段分析
                'visceral_fat_area': measurement.get('visceral_fat_area'), # 内脏脂肪面积 (cm²)
                'visceral_fat_level': measurement.get('visceral_fat_level'), # 内脏脂肪等级
                
                # 代谢分析
                'bmr': measurement.get('bmr'),                          # 基础代谢率 (kcal)
                'tbw_ffm_ratio': measurement.get('tbw_ffm_ratio'),      # 体水分/去脂体重比
                
                # 身体评分
                'body_composition_score': measurement.get('body_composition_score'),
                'muscle_fat_analysis': measurement.get('muscle_fat_analysis'),
                
                # 节段肌肉量分析
                'arm_muscle_mass': {
                    'left': measurement.get('left_arm_muscle'),
                    'right': measurement.get('right_arm_muscle')
                },
                'leg_muscle_mass': {
                    'left': measurement.get('left_leg_muscle'),
                    'right': measurement.get('right_leg_muscle')
                },
                'trunk_muscle_mass': measurement.get('trunk_muscle'),
                
                # 质量控制
                'impedance_values': measurement.get('impedance_values', {}),
                'measurement_quality': self.assess_measurement_quality(measurement)
            }
            
            measurements.append(parsed_measurement)
        
        return measurements
```

**方案2：移动设备蓝牙SDK（家用设备）**
```java
// Android InBody蓝牙SDK集成
public class InBodyBluetoothManager {
    private InBodyBLEManager bleManager;
    private Context context;
    
    public void initializeSDK() {
        // 初始化InBody蓝牙SDK
        bleManager = new InBodyBLEManager(context);
        
        // 设置设备发现回调
        bleManager.setDeviceDiscoveryCallback(new DeviceDiscoveryCallback() {
            @Override
            public void onDeviceFound(InBodyDevice device) {
                Log.d("InBody", "发现设备: " + device.getDeviceName());
                showDeviceInList(device);
            }
        });
        
        // 设置测量数据回调
        bleManager.setMeasurementCallback(new MeasurementCallback() {
            @Override
            public void onMeasurementReceived(InBodyMeasurement measurement) {
                handleInBodyMeasurement(measurement);
            }
            
            @Override
            public void onMeasurementError(InBodyError error) {
                Log.e("InBody", "测量错误: " + error.getMessage());
            }
        });
    }
    
    private void handleInBodyMeasurement(InBodyMeasurement measurement) {
        // 创建体成分数据对象
        BodyCompositionData data = new BodyCompositionData();
        
        // 基础数据
        data.setWeight(measurement.getWeight());
        data.setBodyFatPercentage(measurement.getBodyFatPercentage());
        data.setMusclePercentage(measurement.getMusclePercentage());
        data.setViscerialFatLevel(measurement.getVisceralFatLevel());
        data.setBMR(measurement.getBMR());
        data.setTotalBodyWater(measurement.getTotalBodyWater());
        data.setBMI(measurement.getBMI());
        
        // 节段分析
        data.setLeftArmMuscle(measurement.getLeftArmMuscle());
        data.setRightArmMuscle(measurement.getRightArmMuscle());
        data.setLeftLegMuscle(measurement.getLeftLegMuscle());
        data.setRightLegMuscle(measurement.getRightLegMuscle());
        data.setTrunkMuscle(measurement.getTrunkMuscle());
        
        // 保存和上传数据
        saveToDatabase(data);
        uploadToServer(data);
    }
}
```

**方案3：第三方平台集成（Terra API）**
```javascript
// 通过Terra API集成InBody
class InBodyTerraIntegration {
    constructor(terraApiKey) {
        this.apiKey = terraApiKey;
        this.baseUrl = 'https://api.tryterra.co';
    }
    
    async handleInBodyWebhook(webhookData) {
        // 处理Terra发送的InBody数据
        const bodyData = webhookData.data;
        
        const standardizedData = {
            user_id: webhookData.user.user_id,
            timestamp: new Date(bodyData.timestamp),
            
            // 基础测量
            weight_kg: bodyData.weight_kg,
            height_cm: bodyData.height_cm,
            bmi: bodyData.BMI,
            
            // 体成分
            body_fat_percentage: bodyData.body_fat_percentage,
            muscle_mass_kg: bodyData.muscle_mass_kg,
            bone_mass_kg: bodyData.bone_mass_kg,
            water_percentage: bodyData.hydration_percentage,
            
            // InBody特有数据
            visceral_fat_level: bodyData.visceral_fat_level,
            basal_metabolic_rate: bodyData.BMR_kcal,
            protein_kg: bodyData.protein_kg,
            mineral_kg: bodyData.mineral_kg,
            
            // 节段分析
            segmental_analysis: {
                left_arm: bodyData.left_arm_lean_mass_kg,
                right_arm: bodyData.right_arm_lean_mass_kg,
                left_leg: bodyData.left_leg_lean_mass_kg,
                right_leg: bodyData.right_leg_lean_mass_kg,
                trunk: bodyData.trunk_lean_mass_kg
            },
            
            source: 'inbody_via_terra',
            device_id: bodyData.device_id
        };
        
        await this.sendToYourSystem(standardizedData);
    }
}
```

**InBody集成方案对比**

| 集成方式 | 适用设备 | 开发难度 | 数据完整性 | 成本 | 推荐指数 |
|----------|----------|----------|------------|------|----------|
| **Web API** | 所有型号 | 低 | 完整 | 中等 | ⭐⭐⭐⭐⭐ |
| **蓝牙SDK** | 家用型号 | 中等 | 完整 | 低 | ⭐⭐⭐⭐ |
| **直连协议** | 专业型号 | 高 | 完整 | 低 | ⭐⭐⭐ |
| **Terra API** | 所有型号 | 低 | 标准化 | 高 | ⭐⭐⭐⭐ |

**获取InBody API访问权限**
1. 联系InBody官方（inbodyusa.com, inbody.com, inbodyasia.com）
2. 申请LookinBody Web账户
3. 获取API Key和开发者文档
4. 选择合适的集成方案

**Withings体重秤API**
```python
# Withings API集成
import requests
from datetime import datetime, timedelta

class WithingsBodyScaleAPI:
    def __init__(self, client_id, client_secret, access_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.base_url = "https://wbsapi.withings.net"
    
    def get_body_measurements(self, user_id, days=30):
        """获取体重和体成分数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            'action': 'getmeas',
            'userid': user_id,
            'meastype': '1,5,6,8,76,77,88,11',  # 体重、体脂、肌肉量等
            'category': 1,
            'startdate': int(start_date.timestamp()),
            'enddate': int(end_date.timestamp())
        }
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        response = requests.get(
            f"{self.base_url}/measure",
            params=params,
            headers=headers
        )
        
        return self.parse_body_data(response.json())
    
    def parse_body_data(self, raw_data):
        """解析体成分数据"""
        measurements = []
        
        for group in raw_data.get('body', {}).get('measuregrps', []):
            measurement = {
                'timestamp': datetime.fromtimestamp(group['date']),
                'category': group['category']
            }
            
            for measure in group['measures']:
                measurement_type = measure['type']
                value = measure['value'] * (10 ** measure['unit'])
                
                # 数据类型映射
                type_mapping = {
                    1: 'weight',      # 体重 (kg)
                    5: 'fat_free_mass',  # 去脂体重 (kg)
                    6: 'fat_ratio',   # 体脂率 (%)
                    8: 'fat_mass',    # 脂肪量 (kg)
                    11: 'pulse',      # 脉搏 (bpm)
                    76: 'muscle_mass', # 肌肉量 (kg)
                    77: 'hydration',  # 水分 (%)
                    88: 'bone_mass'   # 骨量 (kg)
                }
                
                if measurement_type in type_mapping:
                    measurement[type_mapping[measurement_type]] = value
            
            measurements.append(measurement)
        
        return measurements
```

**Tuya智能体重秤云API**
```javascript
// Tuya智能体重秤集成
class TuyaBodyScaleAPI {
    constructor(accessKey, secretKey, baseUrl) {
        this.accessKey = accessKey;
        this.secretKey = secretKey;
        this.baseUrl = baseUrl || 'https://openapi.tuyacn.com';
    }
    
    async getDeviceData(deviceId) {
        const timestamp = Date.now();
        const signStr = this.generateSignature(timestamp);
        
        const response = await fetch(`${this.baseUrl}/v1.0/devices/${deviceId}/status`, {
            headers: {
                'client_id': this.accessKey,
                'sign': signStr,
                't': timestamp,
                'sign_method': 'HMAC-SHA256',
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        return this.parseScaleData(data);
    }
    
    parseScaleData(rawData) {
        const bodyData = {};
        
        rawData.result.forEach(item => {
            switch(item.code) {
                case 'weight':
                    bodyData.weight = item.value / 100; // 转换为kg
                    break;
                case 'body_fat':
                    bodyData.bodyFatPercentage = item.value / 10;
                    break;
                case 'bmi':
                    bodyData.bmi = item.value / 10;
                    break;
                case 'muscle_mass':
                    bodyData.muscleMass = item.value / 100;
                    break;
                case 'bone_mass':
                    bodyData.boneMass = item.value / 100;
                    break;
                case 'water_content':
                    bodyData.waterPercentage = item.value / 10;
                    break;
            }
        });
        
        return {
            ...bodyData,
            timestamp: new Date().toISOString(),
            deviceId: rawData.deviceId
        };
    }
}
```

### 4. 🫁 血氧仪/脉搏设备

#### 技术方案
| 集成方式 | 设备支持 | 开发难度 | 数据精度 |
|----------|----------|----------|----------|
| **Web Bluetooth** | 标准蓝牙血氧仪 | 中等 | 高 |
| **硬件集成** | MAX30100传感器 | 高 | 很高 |
| **平台API** | 可穿戴设备 | 低 | 中等 |
| **摄像头检测** | 智能手机 | 低 | 中等 |

#### 技术实现方案

**Web Bluetooth血氧仪集成**
```javascript
// Web Bluetooth脉搏血氧仪
class BluetoothPulseOximeter {
    constructor() {
        this.device = null;
        this.server = null;
        this.service = null;
        this.characteristic = null;
    }
    
    async connect() {
        try {
            // 请求蓝牙设备连接
            this.device = await navigator.bluetooth.requestDevice({
                filters: [
                    { services: ['health_thermometer'] },
                    { namePrefix: 'PulseOx' }
                ],
                optionalServices: ['battery_service', 'device_information']
            });
            
            console.log('连接到设备:', this.device.name);
            
            // 连接到GATT服务器
            this.server = await this.device.gatt.connect();
            
            // 获取健康服务
            this.service = await this.server.getPrimaryService('health_thermometer');
            
            // 获取测量特征值
            this.characteristic = await this.service.getCharacteristic('temperature_measurement');
            
            // 订阅数据通知
            await this.characteristic.startNotifications();
            this.characteristic.addEventListener('characteristicvaluechanged', 
                this.handleMeasurement.bind(this));
            
            return true;
        } catch (error) {
            console.error('连接失败:', error);
            return false;
        }
    }
    
    handleMeasurement(event) {
        const value = event.target.value;
        const data = this.parsePulseOxData(value);
        
        console.log('血氧数据:', data);
        this.sendToServer(data);
    }
    
    parsePulseOxData(dataView) {
        // 解析血氧仪数据格式
        const flags = dataView.getUint8(0);
        let index = 1;
        
        // 血氧饱和度 (SpO2)
        const spo2 = dataView.getUint8(index);
        index++;
        
        // 脉搏率
        const pulseRate = dataView.getUint8(index);
        index++;
        
        // 信号强度
        const signalStrength = dataView.getUint8(index);
        
        return {
            spo2: spo2,
            pulseRate: pulseRate,
            signalStrength: signalStrength,
            timestamp: new Date().toISOString(),
            quality: this.assessDataQuality(signalStrength)
        };
    }
    
    assessDataQuality(signalStrength) {
        if (signalStrength > 80) return 'excellent';
        if (signalStrength > 60) return 'good';
        if (signalStrength > 40) return 'fair';
        return 'poor';
    }
}
```

**MAX30100硬件传感器集成**
```cpp
// Arduino/ESP32 MAX30100集成
#include "MAX30100lib.h"
#include <WiFi.h>
#include <HTTPClient.h>

class MAX30100PulseOximeter {
private:
    MAX30100 pox;
    WiFiClient client;
    
public:
    void initialize() {
        // 初始化传感器
        if (!pox.begin()) {
            Serial.println("MAX30100传感器初始化失败");
            return;
        }
        
        // 设置LED电流和采样率
        pox.setLEDCurrents(0x24, 0x24); // 红光和红外LED电流
        pox.setSamplingRate(100); // 100Hz采样率
        
        // 设置回调函数
        pox.setOnBeatDetectedCallback(onBeatDetected);
    }
    
    void readData() {
        pox.update();
        
        if (pox.isDataReady()) {
            float heartRate = pox.getHeartRate();
            float spo2 = pox.getSpO2();
            
            if (heartRate > 50 && heartRate < 180 && spo2 > 70) {
                sendDataToServer(heartRate, spo2);
            }
        }
    }
    
    void sendDataToServer(float heartRate, float spo2) {
        HTTPClient http;
        http.begin("https://your-api.com/health/pulse-ox");
        http.addHeader("Content-Type", "application/json");
        
        String jsonData = "{";
        jsonData += "\"heart_rate\":" + String(heartRate) + ",";
        jsonData += "\"spo2\":" + String(spo2) + ",";
        jsonData += "\"timestamp\":\"" + getCurrentTimestamp() + "\",";
        jsonData += "\"device_id\":\"MAX30100_001\"";
        jsonData += "}";
        
        int httpResponseCode = http.POST(jsonData);
        
        if (httpResponseCode > 0) {
            Serial.println("数据上传成功");
        } else {
            Serial.println("数据上传失败");
        }
        
        http.end();
    }
};

// 心跳检测回调
void onBeatDetected() {
    Serial.println("心跳检测");
}
```

## 统一数据处理平台

### 多设备数据整合
```python
# 医疗设备数据统一处理平台
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import json

@dataclass
class HealthMeasurement:
    device_type: str
    device_id: str
    patient_id: str
    timestamp: datetime
    data: Dict
    quality_score: float
    source: str

class MedicalDeviceIntegrationPlatform:
    def __init__(self):
        self.device_handlers = {}
        self.data_validators = {}
        self.storage = []
    
    def register_device_handler(self, device_type: str, handler):
        """注册设备处理器"""
        self.device_handlers[device_type] = handler
    
    def process_measurement(self, raw_data: dict) -> HealthMeasurement:
        """处理来自各种设备的测量数据"""
        device_type = raw_data.get('device_type')
        handler = self.device_handlers.get(device_type)
        
        if not handler:
            raise ValueError(f"不支持的设备类型: {device_type}")
        
        # 使用对应的处理器解析数据
        parsed_data = handler.parse(raw_data)
        
        # 数据质量评估
        quality_score = self.assess_data_quality(parsed_data, device_type)
        
        # 创建统一的测量记录
        measurement = HealthMeasurement(
            device_type=device_type,
            device_id=raw_data.get('device_id'),
            patient_id=raw_data.get('patient_id'),
            timestamp=datetime.fromisoformat(raw_data.get('timestamp')),
            data=parsed_data,
            quality_score=quality_score,
            source=raw_data.get('source', 'unknown')
        )
        
        # 异常检测
        alerts = self.detect_health_alerts(measurement)
        if alerts:
            measurement.data['alerts'] = alerts
        
        return measurement
    
    def assess_data_quality(self, data: dict, device_type: str) -> float:
        """评估数据质量"""
        quality_score = 1.0
        
        # 设备特定的质量检查
        if device_type == 'blood_pressure':
            # 血压数据合理性检查
            systolic = data.get('systolic', 0)
            diastolic = data.get('diastolic', 0)
            
            if not (70 <= systolic <= 250 and 40 <= diastolic <= 150):
                quality_score -= 0.3
            if systolic <= diastolic:
                quality_score -= 0.5
                
        elif device_type == 'pulse_oximeter':
            # 血氧数据合理性检查
            spo2 = data.get('spo2', 0)
            heart_rate = data.get('heart_rate', 0)
            
            if not (70 <= spo2 <= 100):
                quality_score -= 0.4
            if not (40 <= heart_rate <= 200):
                quality_score -= 0.3
                
        elif device_type == 'body_scale':
            # 体重数据合理性检查
            weight = data.get('weight', 0)
            bmi = data.get('bmi', 0)
            
            if not (20 <= weight <= 300):  # kg
                quality_score -= 0.3
            if not (10 <= bmi <= 60):
                quality_score -= 0.2
        
        return max(0.0, quality_score)
    
    def detect_health_alerts(self, measurement: HealthMeasurement) -> List[str]:
        """健康异常检测"""
        alerts = []
        data = measurement.data
        device_type = measurement.device_type
        
        if device_type == 'blood_pressure':
            systolic = data.get('systolic', 0)
            diastolic = data.get('diastolic', 0)
            
            # 高血压检测
            if systolic >= 140 or diastolic >= 90:
                alerts.append('高血压警告')
            elif systolic >= 130 or diastolic >= 80:
                alerts.append('血压偏高')
            
            # 低血压检测
            if systolic <= 90 or diastolic <= 60:
                alerts.append('低血压警告')
                
        elif device_type == 'pulse_oximeter':
            spo2 = data.get('spo2', 100)
            heart_rate = data.get('heart_rate', 70)
            
            # 血氧饱和度检测
            if spo2 < 95:
                alerts.append('血氧饱和度偏低')
            if spo2 < 90:
                alerts.append('血氧饱和度危险')
            
            # 心率检测
            if heart_rate > 100:
                alerts.append('心率过速')
            elif heart_rate < 60:
                alerts.append('心率过缓')
                
        elif device_type == 'body_scale':
            bmi = data.get('bmi', 22)
            
            # BMI检测
            if bmi >= 30:
                alerts.append('肥胖')
            elif bmi >= 25:
                alerts.append('超重')
            elif bmi < 18.5:
                alerts.append('体重不足')
        
        return alerts
    
    def save_measurement(self, measurement: HealthMeasurement):
        """保存测量数据"""
        self.storage.append(measurement)
        
        # 发送到数据库或云端
        self.send_to_database(measurement)
    
    def get_patient_history(self, patient_id: str, device_type: str = None, 
                           days: int = 30) -> List[HealthMeasurement]:
        """获取患者历史数据"""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered_data = [
            m for m in self.storage
            if m.patient_id == patient_id 
            and m.timestamp >= cutoff_date
            and (device_type is None or m.device_type == device_type)
        ]
        
        return sorted(filtered_data, key=lambda x: x.timestamp, reverse=True)
```

## 设备兼容性矩阵

| 设备类型 | 蓝牙支持 | WiFi支持 | API可用性 | SDK支持 | 推荐方案 |
|----------|----------|----------|-----------|---------|----------|
| **血糖仪** | ✅ 标准GATT | ⚠️ 部分 | 🟡 厂商限制 | ✅ AgaMatrix | Bluetooth+SDK |
| **血压计** | ✅ 广泛支持 | ✅ 智能型号 | ✅ 多厂商 | ✅ iHealth等 | 多渠道集成 |
| **体重秤** | ✅ 标准支持 | ✅ 云同步 | ✅ Withings/Tuya | ⚠️ 有限 | API优先 |
| **血氧仪** | ✅ Web Bluetooth | ❌ 罕见 | ⚠️ 可穿戴 | ✅ 硬件SDK | 硬件+蓝牙 |
| **心电图** | ✅ 医疗级 | ✅ 云平台 | ✅ Vitalera | ✅ 专业SDK | 平台SDK |
| **体温计** | ✅ 红外型号 | ❌ 少见 | ⚠️ 有限 | ✅ 硬件 | 蓝牙直连 |

## 实施建议

### 阶段化实施计划

**第一阶段 (1-3个月)：核心设备**
1. 血糖仪集成（AgaMatrix SDK + Bluetooth GATT）
2. 血压计集成（iHealth SDK + Omron API）
3. 基础数据处理平台

**第二阶段 (3-6个月)：扩展设备**
1. 体重秤集成（Withings API + Tuya平台）
2. 血氧仪集成（Web Bluetooth + 硬件方案）
3. 数据质量和异常检测系统

**第三阶段 (6-12个月)：高级功能**
1. 心电图集成（Vitalera SDK）
2. AI辅助诊断和预警
3. 多设备数据融合分析

### 技术选型建议

1. **优先级排序**：血糖仪 > 血压计 > 体重秤 > 血氧仪 > 心电图
2. **技术路线**：SDK > 官方API > 标准协议 > 第三方平台
3. **兼容性**：支持iOS/Android/Web三端
4. **数据安全**：端到端加密，符合HIPAA/GDPR

---

*文档更新时间: 2025年8月*
*涵盖设备类型: 血糖仪、血压计、体重秤、血氧仪、心电图设备*