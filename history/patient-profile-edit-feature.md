# 患者资料编辑功能需求文档

## 功能概述
在 `client/src/pages/Doctor/Patient/Profile.tsx` 组件中添加编辑功能，允许医生直接在患者资料页面编辑患者信息。

## 需求分析

### 第一性原理分析

从用户体验角度出发：
1. **就地编辑原则**：用户在查看患者信息时，应能直接进入编辑模式，而不需要跳转到新页面
2. **状态清晰原则**：编辑状态和查看状态应有明确区分
3. **操作可逆原则**：用户应能随时取消编辑，回到原始状态
4. **数据一致性原则**：编辑后的数据应立即更新显示

### 功能要求

#### 1. 界面状态管理
- **查看模式**（默认）：
  - 显示只读的患者信息列表
  - 底部显示"编辑"按钮
  
- **编辑模式**：
  - 将只读信息转换为可编辑表单
  - 底部显示"取消"和"保存"按钮

#### 2. 表单字段对应关系
基于 Profile.tsx 当前显示的字段：

| 显示标签 | 字段路径 | 组件类型 | 备注 |
|---------|---------|---------|------|
| 姓名 | `patient.name` | Input | |
| 性别 | `patient.sex` | Radio/Select | 使用 sexMap 映射 |
| 年龄 | `patient.age` | Number | 只读计算字段？ |
| 床号 | `patient.bed.number` | Select | 需要床位列表 |
| 住院号 | `patient.treatment.number` | Input | |
| 院内ID | `patient.innerId` | Input | |
| 临床诊断 | `patient.diagnoses` | Tags/MultiSelect | 数组类型 |
| 病程 | `patient.course` | **自定义组件** | 月为单位，需用Mobile组件重写 |
| 血糖控制目标 | `target.range` | 只读 | 基于goals.type计算 |
| HbA1c控制目标 | `patient.goals.HBA1C` | Range Input | 数组类型 |
| 治疗方案 | `patient.cure` | Tags/MultiSelect | 数组类型 |
| 并发症 | `patient.complication` | Input | |

#### 3. 技术实现要点

##### 病程组件改造
- 当前 `InputCourse.tsx` 使用 Ant Design 的 Select 组件
- 需要使用 Ant Design Mobile 的对应组件重新实现
- 保持相同的数据格式：以月为单位的数字

##### API集成
- 参考 `Editor.tsx` 中的保存逻辑
- 使用 `api.patient.update` 接口
- 实现增量更新（只提交变更的字段）

##### 移动端适配
- 使用 Ant Design Mobile 组件库
- 确保在移动设备上的良好体验

## 已确认信息

✅ **技术栈**：移动端组件，使用 Ant Design Mobile  
✅ **编辑范围**：仅编辑 Profile.tsx 中当前显示的字段  
✅ **HbA1c字段**：暂时忽略类型问题  

## 技术调研结果

### 1. 可用的数据源和API
✅ **诊断选项**：`DIAGNOSIS_TYPES` 已定义在 `client/src/pages/Patient/utils.ts`
```javascript
const DIAGNOSIS_TYPES = ['2型糖尿病', '1型糖尿病', '妊娠期糖尿病', '特殊类型糖尿病', '空腹血糖受损', '糖耐量受损', '糖尿病足', '糖尿病前期', '正常血糖'];
```

✅ **治疗方案选项**：`CURE_TYPES` 已定义在同一文件
```javascript  
const CURE_TYPES = ['健康教育', '营养治疗', '运动治疗', '戒烟', '口服降糖药', 'GLP-1受体激动剂', '胰岛素', '减重手术治疗'];
```

✅ **床位查询API**：`api.bed.query({ departmentId })`

✅ **患者更新API**：`api.patient.update({ id }, updateData)`

✅ **疾病类型选项**：`TIR_OPTIONS` 已定义在 `client/src/pages/Patient/utils.ts`
```javascript
const TIR_OPTIONS = (['3', '4', '9', '2', '5', '6', '1', '8', '7', '10']).map((key) => ({
  label: target.tag,
  value: Number(key),
  goals: { RANGE: target.range, TIR: target.tir.reference * 100 }
}));
```

### 2. Ant Design Mobile 组件选择方案
- **病程输入**：使用 `Picker` 组件，年份+月份选择
- **出生日期**：使用 `DatePicker` 组件或自定义移动端日期选择器
- **年龄输入**：使用 `Input` 组件（数字输入）
- **性别选择**：使用 `Radio` 组件  
- **多选标签**（诊断、治疗方案）：使用 `Selector` 组件
- **床位选择**：使用 `Picker` 或 `Selector` 组件
- **文本输入**：使用 `Input` 组件

### 3. 编辑字段映射
| 字段 | 数据路径 | 编辑组件 | 数据源 |
|------|---------|---------|--------|
| 姓名 | `patient.name` | Input | 用户输入 |
| 性别 | `patient.sex` | Radio | `sexMap` (0,1,2) |
| **出生日期** | `patient.birthday` | DatePicker | 二选一输入，编辑后会自动计算age |
| **年龄** | `patient.years` | InputNumber | 二选一输入，显示使用age字段 |
| 床号 | `patient.bed.number` | Selector | `api.bed.query` |
| 住院号 | `patient.treatment.number` | Input | 用户输入 |
| 院内ID | `patient.innerId` | Input | 用户输入 |
| 临床诊断 | `patient.diagnoses` | Selector (多选) | `DIAGNOSIS_TYPES` |
| 病程 | `patient.course` | 自定义Picker | 年+月组合 |
| **疾病类型** | `patient.goals.type` | Selector | `TIR_OPTIONS` |
| 治疗方案 | `patient.cure` | Selector (多选) | `CURE_TYPES` |
| 并发症 | `patient.complication` | Input | 用户输入 |

### 4. 动态只读字段（基于疾病类型计算）
- **血糖控制目标**：`tirTargets[goalType].range` → `${range[0]}~${range[1]} mmol/L`
- **HbA1c控制目标**：`tirTargets[goalType].tir.reference` → `≥${reference * 100}%`

### 5. 疾病类型联动逻辑
参考 `Editor.tsx` 中的实现：
```javascript
const [goalType, setGoalType] = useState(patient?.goals?.type);
const target = useMemo(() => tirTargets[goalType as GoalType || 1] || tirTargets[1], [goalType]);
```
当用户选择疾病类型时，血糖控制目标和HbA1c控制目标会自动更新显示。

### 6. 数据处理方案
- **增量更新**：参考 `Editor.tsx` 的 `getChanges` 函数
- **数据校验**：
  - 出生日期和年龄二选一必填（参考 `Editor.tsx` 的验证逻辑）
  - 基本的必填和格式校验
- **错误处理**：显示Toast提示

### 7. 特殊验证逻辑
**出生日期vs年龄**：参考 `Editor.tsx` 第356-369行的实现
```javascript
rules={[({ getFieldValue }) => ({
  validator(_, value?: string) {
    const age = getFieldValue('years');
    const v = isNil(age) ? value : age;
    return (!isNil(v)) 
      ? Promise.resolve() 
      : Promise.reject(new Error('出生日期或年龄必须填写一项'));
  },
})]}
```

## 实现计划

### 第一阶段：基础框架 🏗️
1. **状态管理**：添加编辑模式的状态切换
2. **UI结构**：编辑表单和按钮组的布局
3. **数据绑定**：初始值设置和双向绑定

### 第二阶段：组件实现 🧩  
1. **病程组件**：创建移动端的年月选择器
2. **表单字段**：逐个实现各编辑字段的组件
3. **数据验证**：基本的必填和格式校验

### 第三阶段：API集成 🔌
1. **保存逻辑**：集成患者更新API
2. **床位数据**：集成床位查询API  
3. **错误处理**：网络异常和业务错误的处理

### 第四阶段：优化完善 ✨
1. **用户体验**：加载状态、成功提示
2. **数据同步**：保存后更新显示
3. **代码优化**：性能和可维护性优化

## 需要创建的文件
- `client/src/components/MobileCourseInput.tsx` - 移动端病程输入组件
- 可能需要的工具函数和类型定义

## 实现优先级

1. **P0（核心功能）**：基本的编辑/保存/取消功能
2. **P1（重要功能）**：数据校验、错误处理  
3. **P2（优化功能）**：用户体验优化、性能优化

---

✅ **需求分析完成**，技术方案明确，可以开始实现了！🚀 