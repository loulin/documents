# 基于大模型的医疗数据结构化处理指南

## 📋 概述

本指南详细说明如何结合我们的64个内分泌代谢疾病CSV Schema和大语言模型（LLM），对医疗原始数据进行智能结构化处理。支持实时处理和批量处理两种模式，帮助医生快速将非结构化的医疗记录转换为标准化的结构化数据。

## 🎯 处理目标

- **智能解析**：自动识别医疗文本中的关键信息
- **结构化输出**：按照Schema标准输出结构化数据
- **质量保证**：确保数据准确性和完整性
- **效率提升**：大幅减少人工录入工作量
- **标准化**：统一的数据格式便于后续分析

## 🏗️ 系统架构

```
原始医疗数据 → Schema加载器 → 大模型处理器 → 结构化输出 → 质量验证 → 数据存储
     ↓              ↓              ↓             ↓            ↓           ↓
   文本/图像      CSV解析      提示工程+LLM     JSON/CSV     规则检查     数据库
```

## 💻 技术实现方案

### 方案一：实时处理系统

适用于门诊、住院等需要即时处理的场景。

#### 1. 系统组件

```python
# requirements.txt
openai>=1.0.0
pandas>=1.5.0
pydantic>=2.0.0
fastapi>=0.100.0
uvicorn>=0.20.0
redis>=4.5.0
```

#### 2. Schema加载器

```python
import pandas as pd
import json
from typing import Dict, List, Any
from pathlib import Path

class SchemaLoader:
    def __init__(self, schema_dir: str = "./SchemaCSV"):
        self.schema_dir = Path(schema_dir)
        self.schemas = {}
        self.load_all_schemas()

    def load_all_schemas(self):
        """加载所有CSV Schema文件"""
        for csv_file in self.schema_dir.glob("*-schema.csv"):
            schema_name = csv_file.stem.replace("-schema", "")
            try:
                df = pd.read_csv(csv_file)
                self.schemas[schema_name] = {
                    'fields': df.to_dict('records'),
                    'field_names': df['fieldName'].tolist(),
                    'field_descriptions': dict(zip(df['fieldName'], df['description'])),
                    'data_types': dict(zip(df['fieldName'], df['dataType'])),
                    'examples': dict(zip(df['fieldName'], df['examples']))
                }
                print(f"✅ 已加载Schema: {schema_name} ({len(df)}个字段)")
            except Exception as e:
                print(f"❌ 加载Schema失败: {csv_file} - {e}")

    def get_schema(self, schema_name: str) -> Dict:
        """获取指定Schema"""
        return self.schemas.get(schema_name)

    def list_schemas(self) -> List[str]:
        """列出所有可用Schema"""
        return list(self.schemas.keys())

    def generate_prompt_template(self, schema_name: str) -> str:
        """生成用于大模型的提示词模板"""
        schema = self.get_schema(schema_name)
        if not schema:
            return ""

        template = f"""
你是一个专业的医疗数据结构化专家。请根据以下Schema将医疗文本转换为结构化的JSON格式。

Schema名称: {schema_name}

字段定义:
"""
        for field in schema['fields'][:20]:  # 显示前20个字段避免过长
            template += f"- {field['fieldName']} ({field['fieldNameCN']}): {field['description']} [类型: {field['dataType']}]\n"

        if len(schema['fields']) > 20:
            template += f"... 还有{len(schema['fields']) - 20}个字段\n"

        template += """
**严格要求**:
1. **仅提取明确存在的信息**：只从文本中提取明确提到的数据，绝不推测、估算或编造
2. **缺失数据必须标记NULL**：如果某个字段在文本中没有明确信息，必须设置为null
3. **禁止数据推测**：严禁基于其他信息推测缺失字段的可能值
4. **数值精确提取**：数值型数据必须与原文完全一致，不得修改或"优化"
5. **日期格式统一**：日期格式统一为YYYY-MM-DD，无法确定的日期设为null
6. **可信度标记**：为每个提取的字段标记置信度（high/medium/low）
7. **输出标准JSON格式**：包含数据字段和元数据字段

医疗文本:
{medical_text}

请输出结构化JSON:
"""
        return template
```

#### 3. 大模型处理器

```python
import openai
from typing import Dict, Any, Optional
import json
import asyncio

class MedicalDataProcessor:
    def __init__(self, api_key: str, model: str = "gpt-4", schema_loader: SchemaLoader = None):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.schema_loader = schema_loader

    async def process_medical_text(self, text: str, schema_name: str) -> Dict[str, Any]:
        """处理单条医疗文本"""
        try:
            # 生成提示词
            prompt = self.schema_loader.generate_prompt_template(schema_name)
            formatted_prompt = prompt.format(medical_text=text)

            # 调用大模型
            response = await self._call_llm(formatted_prompt)

            # 解析JSON响应
            structured_data = self._parse_llm_response(response, schema_name)

            # 数据验证
            validated_data = self._validate_data(structured_data, schema_name)

            return {
                "success": True,
                "data": validated_data,
                "schema": schema_name,
                "processed_at": pd.Timestamp.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "schema": schema_name,
                "processed_at": pd.Timestamp.now().isoformat()
            }

    async def _call_llm(self, prompt: str) -> str:
        """调用大语言模型"""
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个专业的医疗数据结构化专家，严格按照要求输出JSON格式。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=4000
        )
        return response.choices[0].message.content

    def _parse_llm_response(self, response: str, schema_name: str) -> Dict:
        """解析大模型返回的JSON"""
        try:
            # 提取JSON部分
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                raise ValueError("未找到有效的JSON格式")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析错误: {e}")

    def _validate_data(self, data: Dict, schema_name: str) -> Dict:
        """验证数据格式和类型"""
        schema = self.schema_loader.get_schema(schema_name)
        if not schema:
            return data

        validated = {}
        for field_name, field_type in schema['data_types'].items():
            value = data.get(field_name)
            if value is not None:
                try:
                    if field_type == 'Number':
                        validated[field_name] = float(value) if '.' in str(value) else int(value)
                    elif field_type == 'Boolean':
                        validated[field_name] = bool(value) if isinstance(value, bool) else str(value).lower() in ['true', '1', 'yes', '是']
                    else:  # String
                        validated[field_name] = str(value)
                except (ValueError, TypeError):
                    validated[field_name] = value  # 保持原值
            else:
                validated[field_name] = None

        return validated
```

#### 4. 实时API服务

```python
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import uvicorn
import asyncio
from typing import Optional

app = FastAPI(title="医疗数据结构化API", version="1.0.0")

# 全局组件
schema_loader = SchemaLoader()
processor = MedicalDataProcessor(
    api_key="your-openai-api-key",
    schema_loader=schema_loader
)

class ProcessRequest(BaseModel):
    text: str
    schema_name: str
    patient_id: Optional[str] = None

class ProcessResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    schema: str
    processed_at: str

@app.get("/schemas")
async def get_available_schemas():
    """获取所有可用的Schema"""
    return {
        "schemas": schema_loader.list_schemas(),
        "total": len(schema_loader.schemas)
    }

@app.post("/process", response_model=ProcessResponse)
async def process_medical_data(request: ProcessRequest):
    """处理医疗文本数据"""
    if request.schema_name not in schema_loader.schemas:
        raise HTTPException(status_code=400, detail=f"Schema '{request.schema_name}' 不存在")

    result = await processor.process_medical_text(request.text, request.schema_name)
    return ProcessResponse(**result)

@app.post("/process-file")
async def process_file(file: UploadFile = File(...), schema_name: str = "diabetes-comprehensive"):
    """处理上传的文本文件"""
    if file.content_type not in ["text/plain", "application/pdf"]:
        raise HTTPException(status_code=400, detail="仅支持文本文件和PDF文件")

    content = await file.read()
    text = content.decode('utf-8')

    result = await processor.process_medical_text(text, schema_name)
    return result

@app.get("/health")
async def health_check():
    return {"status": "healthy", "schemas_loaded": len(schema_loader.schemas)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 5. 客户端使用示例

```python
import requests
import json

class MedicalDataClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def get_schemas(self):
        """获取可用Schema列表"""
        response = requests.get(f"{self.base_url}/schemas")
        return response.json()

    def process_text(self, text: str, schema_name: str, patient_id: str = None):
        """处理医疗文本"""
        data = {
            "text": text,
            "schema_name": schema_name,
            "patient_id": patient_id
        }
        response = requests.post(f"{self.base_url}/process", json=data)
        return response.json()

    def process_file(self, file_path: str, schema_name: str):
        """处理文件"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            params = {'schema_name': schema_name}
            response = requests.post(f"{self.base_url}/process-file", files=files, params=params)
        return response.json()

# 使用示例
client = MedicalDataClient()

# 获取Schema列表
schemas = client.get_schemas()
print("可用Schema:", schemas['schemas'])

# 处理医疗文本
medical_text = """
患者张三，男，58岁，确诊2型糖尿病10年。
今日门诊复查：空腹血糖7.8mmol/L，餐后2小时血糖12.3mmol/L，
糖化血红蛋白8.2%。血压145/88mmHg，体重75kg，身高168cm。
患者诉近期多饮、多尿症状加重，乏力明显。
足部检查未见明显异常。
建议调整降糖方案，加强血糖监测。
"""

result = client.process_text(medical_text, "diabetes-comprehensive", "P202401001")
print("处理结果:", json.dumps(result, indent=2, ensure_ascii=False))
```

### 方案二：批量处理系统

适用于历史数据整理、科研数据处理等批量场景。

#### 1. 批量处理器

```python
import pandas as pd
import asyncio
import aiofiles
from concurrent.futures import ThreadPoolExecutor
import logging
from tqdm.asyncio import tqdm
import json
from pathlib import Path

class BatchProcessor:
    def __init__(self, schema_loader: SchemaLoader, processor: MedicalDataProcessor,
                 batch_size: int = 10, max_workers: int = 5):
        self.schema_loader = schema_loader
        self.processor = processor
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.setup_logging()

    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('batch_processing.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def process_csv_file(self, input_file: str, output_dir: str,
                              text_column: str, schema_name: str,
                              patient_id_column: str = None):
        """处理CSV文件中的医疗文本数据"""
        self.logger.info(f"开始处理文件: {input_file}")

        # 读取输入文件
        df = pd.read_csv(input_file)
        total_rows = len(df)
        self.logger.info(f"共{total_rows}条记录需要处理")

        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # 准备结果存储
        results = []
        errors = []

        # 分批处理
        semaphore = asyncio.Semaphore(self.max_workers)

        async def process_batch(batch_df):
            tasks = []
            async with semaphore:
                for idx, row in batch_df.iterrows():
                    text = row[text_column]
                    patient_id = row[patient_id_column] if patient_id_column else f"batch_{idx}"

                    task = self.process_single_record(text, schema_name, patient_id, idx)
                    tasks.append(task)

                return await asyncio.gather(*tasks, return_exceptions=True)

        # 分批执行
        with tqdm(total=total_rows, desc="处理进度") as pbar:
            for i in range(0, total_rows, self.batch_size):
                batch_df = df.iloc[i:i+self.batch_size]
                batch_results = await process_batch(batch_df)

                for result in batch_results:
                    if isinstance(result, Exception):
                        errors.append(str(result))
                    else:
                        results.append(result)

                pbar.update(len(batch_df))

        # 保存结果
        await self.save_results(results, errors, output_path, schema_name)

        self.logger.info(f"处理完成: {len(results)}成功, {len(errors)}失败")
        return {
            "total_processed": len(results) + len(errors),
            "successful": len(results),
            "failed": len(errors),
            "output_dir": str(output_path)
        }

    async def process_single_record(self, text: str, schema_name: str,
                                  patient_id: str, record_index: int):
        """处理单条记录"""
        try:
            result = await self.processor.process_medical_text(text, schema_name)
            result['patient_id'] = patient_id
            result['record_index'] = record_index
            return result
        except Exception as e:
            self.logger.error(f"处理记录{record_index}失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "patient_id": patient_id,
                "record_index": record_index
            }

    async def save_results(self, results: list, errors: list,
                          output_path: Path, schema_name: str):
        """保存处理结果"""
        # 保存成功的结果
        if results:
            successful_data = []
            for result in results:
                if result.get('success'):
                    data = result['data'].copy()
                    data['patient_id'] = result.get('patient_id')
                    data['processed_at'] = result.get('processed_at')
                    successful_data.append(data)

            if successful_data:
                df_results = pd.DataFrame(successful_data)
                output_file = output_path / f"{schema_name}_processed_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df_results.to_csv(output_file, index=False)
                self.logger.info(f"成功结果已保存: {output_file}")

        # 保存错误日志
        if errors:
            error_file = output_path / f"errors_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
            async with aiofiles.open(error_file, 'w') as f:
                await f.write(json.dumps(errors, indent=2, ensure_ascii=False))
            self.logger.info(f"错误日志已保存: {error_file}")

    async def process_directory(self, input_dir: str, output_dir: str,
                               schema_name: str, file_pattern: str = "*.txt"):
        """批量处理目录中的文本文件"""
        input_path = Path(input_dir)
        files = list(input_path.glob(file_pattern))

        self.logger.info(f"找到{len(files)}个文件需要处理")

        all_results = []
        for file_path in tqdm(files, desc="处理文件"):
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()

                result = await self.processor.process_medical_text(content, schema_name)
                result['source_file'] = str(file_path)
                all_results.append(result)

            except Exception as e:
                self.logger.error(f"处理文件{file_path}失败: {e}")
                all_results.append({
                    "success": False,
                    "error": str(e),
                    "source_file": str(file_path)
                })

        # 保存汇总结果
        output_path = Path(output_dir)
        await self.save_directory_results(all_results, output_path, schema_name)

        successful = sum(1 for r in all_results if r.get('success'))
        failed = len(all_results) - successful

        return {
            "total_files": len(files),
            "successful": successful,
            "failed": failed,
            "output_dir": str(output_path)
        }

    async def save_directory_results(self, results: list, output_path: Path, schema_name: str):
        """保存目录处理结果"""
        output_path.mkdir(exist_ok=True)

        successful_data = []
        failed_data = []

        for result in results:
            if result.get('success'):
                data = result['data'].copy()
                data['source_file'] = result.get('source_file')
                data['processed_at'] = result.get('processed_at')
                successful_data.append(data)
            else:
                failed_data.append({
                    'source_file': result.get('source_file'),
                    'error': result.get('error'),
                    'processed_at': result.get('processed_at', pd.Timestamp.now().isoformat())
                })

        # 保存成功结果
        if successful_data:
            df_success = pd.DataFrame(successful_data)
            success_file = output_path / f"{schema_name}_directory_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df_success.to_csv(success_file, index=False)
            self.logger.info(f"目录处理成功结果: {success_file}")

        # 保存失败结果
        if failed_data:
            df_failed = pd.DataFrame(failed_data)
            failed_file = output_path / f"failed_files_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df_failed.to_csv(failed_file, index=False)
            self.logger.info(f"目录处理失败结果: {failed_file}")
```

#### 2. 批量处理脚本

```python
import asyncio
import argparse
from pathlib import Path

async def main():
    parser = argparse.ArgumentParser(description='医疗数据批量结构化处理')
    parser.add_argument('--input', required=True, help='输入文件或目录路径')
    parser.add_argument('--output', required=True, help='输出目录路径')
    parser.add_argument('--schema', required=True, help='使用的Schema名称')
    parser.add_argument('--mode', choices=['csv', 'directory'], default='csv', help='处理模式')
    parser.add_argument('--text-column', default='text', help='CSV文件中的文本列名')
    parser.add_argument('--patient-id-column', help='CSV文件中的患者ID列名')
    parser.add_argument('--batch-size', type=int, default=10, help='批处理大小')
    parser.add_argument('--max-workers', type=int, default=5, help='最大并发数')
    parser.add_argument('--api-key', required=True, help='OpenAI API密钥')

    args = parser.parse_args()

    # 初始化组件
    schema_loader = SchemaLoader()
    processor = MedicalDataProcessor(api_key=args.api_key, schema_loader=schema_loader)
    batch_processor = BatchProcessor(
        schema_loader=schema_loader,
        processor=processor,
        batch_size=args.batch_size,
        max_workers=args.max_workers
    )

    # 验证Schema
    if args.schema not in schema_loader.schemas:
        print(f"错误: Schema '{args.schema}' 不存在")
        print(f"可用Schema: {schema_loader.list_schemas()}")
        return

    # 执行处理
    if args.mode == 'csv':
        result = await batch_processor.process_csv_file(
            input_file=args.input,
            output_dir=args.output,
            text_column=args.text_column,
            schema_name=args.schema,
            patient_id_column=args.patient_id_column
        )
    else:
        result = await batch_processor.process_directory(
            input_dir=args.input,
            output_dir=args.output,
            schema_name=args.schema
        )

    print("批量处理完成:")
    print(f"  总计处理: {result.get('total_processed', result.get('total_files'))}")
    print(f"  成功: {result['successful']}")
    print(f"  失败: {result['failed']}")
    print(f"  输出目录: {result['output_dir']}")

if __name__ == "__main__":
    asyncio.run(main())
```

#### 3. 批量处理使用示例

```bash
# 处理CSV文件
python batch_process.py \
  --input ./data/medical_records.csv \
  --output ./processed_data/ \
  --schema diabetes-comprehensive \
  --mode csv \
  --text-column medical_text \
  --patient-id-column patient_id \
  --batch-size 20 \
  --max-workers 5 \
  --api-key your-openai-api-key

# 处理文本文件目录
python batch_process.py \
  --input ./raw_texts/ \
  --output ./structured_data/ \
  --schema diabetes-nursing-assessment \
  --mode directory \
  --batch-size 10 \
  --api-key your-openai-api-key
```

## 🛡️ 数据完整性和严谨性控制

### 核心原则：医疗数据零容忍策略

医疗数据的准确性直接关系患者安全，因此必须建立严格的数据完整性控制机制，防止大模型产生"幻想"数据。

#### 1. 防幻想数据机制

```python
class AntiHallucinationValidator:
    def __init__(self, schema_loader: SchemaLoader):
        self.schema_loader = schema_loader

    def create_strict_prompt(self, schema_name: str) -> str:
        """创建防幻想的严格提示词"""
        schema = self.schema_loader.get_schema(schema_name)

        strict_prompt = f"""
你是医疗数据提取专家。请严格按照以下规则提取信息：

🚫 **绝对禁止的行为**：
- 推测、估算或编造任何数据
- 基于常识或经验填补缺失信息
- 将相似概念的数据用于其他字段
- 进行任何形式的数据"优化"或"标准化"

✅ **必须遵循的规则**：
- 只提取文本中明确存在的信息
- 缺失的字段必须标记为 null
- 数值必须与原文完全一致
- 不确定的信息标记低置信度

Schema字段定义：
{self._format_schema_for_strict_extraction(schema)}

输出格式要求：
```json
{{
  "extracted_data": {{
    // 仅包含从文本中明确提取的字段
  }},
  "metadata": {{
    "extraction_confidence": "high|medium|low",
    "null_fields": ["field1", "field2"],  // 明确标记缺失字段
    "uncertain_fields": [{{
      "field": "fieldName",
      "reason": "原因描述",
      "confidence": "low"
    }}],
    "source_references": {{
      "field": "原文引用片段"
    }}
  }}
}}
```

医疗文本：
{{medical_text}}
"""
        return strict_prompt

    def _format_schema_for_strict_extraction(self, schema: Dict) -> str:
        """格式化Schema以强调严格提取"""
        formatted = ""
        for field in schema['fields'][:15]:  # 限制显示数量
            formatted += f"- {field['fieldName']} ({field['fieldNameCN']}): {field['description']}\n"
            formatted += f"  类型: {field['dataType']} | 示例: {field['examples']}\n"
            formatted += f"  ⚠️ 仅在文本明确提及时填写，否则设为 null\n\n"
        return formatted

    def validate_against_source(self, extracted_data: Dict, source_text: str,
                               schema_name: str) -> Dict:
        """验证提取数据与原文的一致性"""
        validation_result = {
            "is_valid": True,
            "concerns": [],
            "null_fields": [],
            "confidence_issues": []
        }

        # 检查null字段
        for field_name, value in extracted_data.get('extracted_data', {}).items():
            if value is None:
                validation_result["null_fields"].append(field_name)

        # 检查数值一致性
        numeric_fields = self._extract_numbers_from_text(source_text)
        for field_name, value in extracted_data.get('extracted_data', {}).items():
            if isinstance(value, (int, float)):
                if not self._number_exists_in_source(value, numeric_fields):
                    validation_result["concerns"].append({
                        "field": field_name,
                        "issue": f"数值 {value} 在原文中未找到对应",
                        "severity": "high"
                    })
                    validation_result["is_valid"] = False

        return validation_result

    def _extract_numbers_from_text(self, text: str) -> List[float]:
        """从文本中提取所有数字"""
        import re
        numbers = re.findall(r'\d+\.?\d*', text)
        return [float(n) for n in numbers]

    def _number_exists_in_source(self, value: float, source_numbers: List[float]) -> bool:
        """检查数值是否存在于原文中"""
        tolerance = 0.001  # 浮点数误差容忍
        return any(abs(value - num) < tolerance for num in source_numbers)
```

#### 2. 强制NULL标记系统

```python
class NullFieldController:
    def __init__(self, schema_loader: SchemaLoader):
        self.schema_loader = schema_loader

    def enforce_null_completeness(self, data: Dict, schema_name: str) -> Dict:
        """强制确保所有Schema字段都有值（包括null）"""
        schema = self.schema_loader.get_schema(schema_name)
        if not schema:
            return data

        complete_data = {}
        null_fields = []

        # 确保每个Schema字段都存在
        for field_name in schema['field_names']:
            if field_name in data:
                complete_data[field_name] = data[field_name]
            else:
                complete_data[field_name] = None
                null_fields.append(field_name)

        # 移除Schema中不存在的字段（防止幻想字段）
        extra_fields = set(data.keys()) - set(schema['field_names'])
        if extra_fields:
            print(f"⚠️ 警告：发现Schema外字段，已移除: {extra_fields}")

        return {
            "data": complete_data,
            "metadata": {
                "null_fields": null_fields,
                "null_percentage": len(null_fields) / len(schema['field_names']) * 100,
                "extra_fields_removed": list(extra_fields)
            }
        }

    def create_null_audit_report(self, processed_data: List[Dict],
                                schema_name: str) -> Dict:
        """创建NULL字段审计报告"""
        schema = self.schema_loader.get_schema(schema_name)
        field_null_counts = {field: 0 for field in schema['field_names']}
        total_records = len(processed_data)

        for record in processed_data:
            for field_name, value in record.get('data', {}).items():
                if value is None:
                    field_null_counts[field_name] += 1

        # 计算缺失率
        null_rates = {
            field: (count / total_records * 100)
            for field, count in field_null_counts.items()
        }

        # 识别高缺失率字段
        high_null_fields = [
            field for field, rate in null_rates.items()
            if rate > 80  # 超过80%缺失
        ]

        return {
            "total_records": total_records,
            "field_null_rates": null_rates,
            "high_null_fields": high_null_fields,
            "average_null_rate": sum(null_rates.values()) / len(null_rates),
            "data_completeness_score": 100 - (sum(null_rates.values()) / len(null_rates))
        }
```

#### 3. 可信度评估机制

```python
class ConfidenceAssessor:
    def __init__(self):
        self.confidence_rules = {
            'high': {
                'numeric_exact_match': True,
                'clear_terminology': True,
                'complete_context': True
            },
            'medium': {
                'numeric_approximate': True,
                'partial_context': True,
                'standard_terminology': True
            },
            'low': {
                'ambiguous_wording': True,
                'incomplete_information': True,
                'requires_inference': True
            }
        }

    def assess_field_confidence(self, field_name: str, extracted_value: Any,
                              source_text: str, context: str) -> Dict:
        """评估单个字段的提取置信度"""
        confidence_factors = {
            'source_clarity': self._assess_source_clarity(extracted_value, source_text),
            'context_completeness': self._assess_context_completeness(context),
            'terminology_precision': self._assess_terminology_precision(field_name, source_text),
            'numeric_precision': self._assess_numeric_precision(extracted_value, source_text)
        }

        # 综合计算置信度
        overall_confidence = self._calculate_overall_confidence(confidence_factors)

        return {
            "field": field_name,
            "confidence_level": overall_confidence,
            "confidence_score": self._get_confidence_score(confidence_factors),
            "factors": confidence_factors,
            "recommendation": self._get_confidence_recommendation(overall_confidence)
        }

    def _assess_source_clarity(self, value: Any, source_text: str) -> float:
        """评估原文表述的清晰度"""
        if value is None:
            return 1.0  # NULL值是明确的

        # 检查数值是否在原文中明确存在
        if isinstance(value, (int, float)):
            if str(value) in source_text:
                return 1.0
            else:
                return 0.3  # 数值不匹配，低置信度

        # 检查文本是否直接来源于原文
        if isinstance(value, str) and value.lower() in source_text.lower():
            return 0.9

        return 0.5

    def _get_confidence_recommendation(self, confidence: str) -> str:
        """获取置信度建议"""
        recommendations = {
            'high': "数据可直接使用",
            'medium': "建议人工复核",
            'low': "需要人工验证或重新提取"
        }
        return recommendations.get(confidence, "未知置信度")
```

#### 4. 人工审核接口

```python
class HumanReviewInterface:
    def __init__(self, confidence_assessor: ConfidenceAssessor):
        self.confidence_assessor = confidence_assessor

    def generate_review_queue(self, processed_data: List[Dict],
                            min_confidence: str = 'medium') -> List[Dict]:
        """生成需要人工审核的数据队列"""
        confidence_order = {'low': 0, 'medium': 1, 'high': 2}
        min_level = confidence_order[min_confidence]

        review_queue = []
        for record in processed_data:
            metadata = record.get('metadata', {})

            # 检查是否有低置信度字段
            uncertain_fields = metadata.get('uncertain_fields', [])
            needs_review = any(
                confidence_order.get(field.get('confidence', 'low'), 0) <= min_level
                for field in uncertain_fields
            )

            if needs_review or len(metadata.get('null_fields', [])) > 0.5 * len(record.get('data', {})):
                review_item = {
                    "record_id": record.get('patient_id', 'unknown'),
                    "review_priority": self._calculate_review_priority(metadata),
                    "issues": self._summarize_issues(metadata),
                    "data": record['data'],
                    "source_text": record.get('source_text', ''),
                    "metadata": metadata
                }
                review_queue.append(review_item)

        # 按优先级排序
        review_queue.sort(key=lambda x: x['review_priority'], reverse=True)
        return review_queue

    def _calculate_review_priority(self, metadata: Dict) -> int:
        """计算审核优先级（1-10，10最高）"""
        priority = 5  # 基础优先级

        # 高缺失率增加优先级
        null_percentage = metadata.get('null_percentage', 0)
        if null_percentage > 70:
            priority += 3
        elif null_percentage > 50:
            priority += 2

        # 低置信度字段增加优先级
        uncertain_fields = metadata.get('uncertain_fields', [])
        low_confidence_count = sum(1 for f in uncertain_fields if f.get('confidence') == 'low')
        priority += min(low_confidence_count, 3)

        return min(priority, 10)

    def create_review_form(self, review_item: Dict) -> str:
        """创建人工审核表单（HTML格式）"""
        html_form = f"""
        <div class="review-form">
            <h3>数据审核 - 记录ID: {review_item['record_id']}</h3>
            <div class="priority">审核优先级: {review_item['review_priority']}/10</div>

            <div class="source-text">
                <h4>原始文本:</h4>
                <pre>{review_item['source_text']}</pre>
            </div>

            <div class="extracted-data">
                <h4>提取的数据:</h4>
                <table border="1">
                    <tr><th>字段</th><th>提取值</th><th>置信度</th><th>审核结果</th></tr>
        """

        for field, value in review_item['data'].items():
            confidence = self._get_field_confidence(field, review_item['metadata'])
            html_form += f"""
                    <tr>
                        <td>{field}</td>
                        <td>{value if value is not None else 'NULL'}</td>
                        <td>{confidence}</td>
                        <td>
                            <select name="review_{field}">
                                <option value="approve">批准</option>
                                <option value="modify">修改</option>
                                <option value="reject">拒绝</option>
                            </select>
                            <input type="text" name="modify_{field}" placeholder="修改值">
                        </td>
                    </tr>
            """

        html_form += """
                </table>
            </div>

            <div class="issues">
                <h4>识别的问题:</h4>
                <ul>
        """

        for issue in review_item['issues']:
            html_form += f"<li>{issue}</li>"

        html_form += """
                </ul>
            </div>

            <div class="actions">
                <button onclick="submitReview()">提交审核</button>
                <button onclick="requestReprocessing()">重新处理</button>
            </div>
        </div>
        """

        return html_form
```

#### 5. 数据溯源和审计

```python
class DataLineageTracker:
    def __init__(self):
        self.lineage_db = {}  # 在生产环境中应使用数据库

    def track_extraction(self, record_id: str, source_text: str,
                        extracted_data: Dict, metadata: Dict) -> str:
        """跟踪数据提取过程"""
        lineage_id = f"lineage_{record_id}_{int(time.time())}"

        lineage_record = {
            "lineage_id": lineage_id,
            "record_id": record_id,
            "timestamp": pd.Timestamp.now().isoformat(),
            "source_text_hash": hashlib.md5(source_text.encode()).hexdigest(),
            "source_text_length": len(source_text),
            "extracted_fields": list(extracted_data.keys()),
            "null_fields": [k for k, v in extracted_data.items() if v is None],
            "processing_metadata": metadata,
            "extraction_method": "llm_with_schema",
            "schema_version": "v4.0"
        }

        self.lineage_db[lineage_id] = lineage_record
        return lineage_id

    def create_audit_trail(self, lineage_id: str) -> Dict:
        """创建审计跟踪记录"""
        if lineage_id not in self.lineage_db:
            return {"error": "Lineage record not found"}

        lineage = self.lineage_db[lineage_id]

        audit_trail = {
            "extraction_summary": {
                "total_fields": len(lineage["extracted_fields"]),
                "null_fields": len(lineage["null_fields"]),
                "data_completeness": 1 - (len(lineage["null_fields"]) / len(lineage["extracted_fields"])),
                "processing_timestamp": lineage["timestamp"]
            },
            "data_quality_flags": self._generate_quality_flags(lineage),
            "compliance_status": self._check_compliance(lineage),
            "recommendation": self._generate_audit_recommendation(lineage)
        }

        return audit_trail

    def _generate_quality_flags(self, lineage: Dict) -> List[str]:
        """生成数据质量标记"""
        flags = []

        null_ratio = len(lineage["null_fields"]) / len(lineage["extracted_fields"])
        if null_ratio > 0.7:
            flags.append("HIGH_NULL_RATIO")

        if len(lineage["source_text"]) < 100:
            flags.append("SHORT_SOURCE_TEXT")

        return flags

    def _check_compliance(self, lineage: Dict) -> str:
        """检查合规性"""
        flags = self._generate_quality_flags(lineage)

        if "HIGH_NULL_RATIO" in flags:
            return "NEEDS_REVIEW"
        elif len(flags) > 0:
            return "CAUTION"
        else:
            return "COMPLIANT"
```

#### 6. 配置严格模式

```python
class StrictModeConfig:
    """严格模式配置，确保医疗数据准确性"""

    STRICT_MODE_SETTINGS = {
        "allow_inference": False,  # 禁止推测
        "allow_approximation": False,  # 禁止近似
        "require_source_reference": True,  # 要求源文本引用
        "mandatory_null_marking": True,  # 强制NULL标记
        "confidence_threshold": 0.8,  # 置信度阈值
        "auto_reject_low_confidence": True,  # 自动拒绝低置信度
        "human_review_required": ["low", "medium"],  # 需要人工审核的置信度
        "audit_trail_enabled": True,  # 启用审计跟踪
    }

    @classmethod
    def get_strict_prompt_prefix(cls) -> str:
        return """
🔒 **医疗数据严格模式已启用**

核心原则：
- 准确性优于完整性
- NULL优于猜测
- 可验证性优于可读性
- 审慎优于效率

在此模式下，任何不确定的信息都必须标记为NULL或低置信度。
        """

    @classmethod
    def validate_strict_compliance(cls, result: Dict) -> Dict:
        """验证严格模式合规性"""
        compliance_issues = []

        # 检查是否有推测数据
        metadata = result.get('metadata', {})
        if metadata.get('contains_inference', False):
            compliance_issues.append("包含推测数据，违反严格模式")

        # 检查置信度
        uncertain_fields = metadata.get('uncertain_fields', [])
        low_confidence_fields = [f for f in uncertain_fields if f.get('confidence') == 'low']
        if low_confidence_fields and cls.STRICT_MODE_SETTINGS['auto_reject_low_confidence']:
            compliance_issues.append(f"存在低置信度字段: {[f['field'] for f in low_confidence_fields]}")

        return {
            "compliant": len(compliance_issues) == 0,
            "issues": compliance_issues,
            "compliance_score": max(0, 1 - len(compliance_issues) * 0.2)
        }
```

### 使用示例：启用严格模式

```python
# 初始化严格模式组件
anti_hallucination = AntiHallucinationValidator(schema_loader)
null_controller = NullFieldController(schema_loader)
confidence_assessor = ConfidenceAssessor()
lineage_tracker = DataLineageTracker()

# 使用严格模式处理
async def process_with_strict_mode(text: str, schema_name: str, patient_id: str):
    # 1. 使用防幻想提示词
    strict_prompt = anti_hallucination.create_strict_prompt(schema_name)

    # 2. 调用大模型（使用更保守的参数）
    response = await processor._call_llm(strict_prompt.format(medical_text=text))

    # 3. 解析并验证
    parsed_result = processor._parse_llm_response(response, schema_name)

    # 4. 强制NULL完整性
    complete_result = null_controller.enforce_null_completeness(
        parsed_result.get('extracted_data', {}), schema_name
    )

    # 5. 验证与原文一致性
    validation = anti_hallucination.validate_against_source(
        parsed_result, text, schema_name
    )

    # 6. 评估置信度
    confidence_assessment = confidence_assessor.assess_field_confidence(
        "overall", complete_result['data'], text, ""
    )

    # 7. 检查严格模式合规性
    compliance = StrictModeConfig.validate_strict_compliance({
        'data': complete_result['data'],
        'metadata': {**complete_result['metadata'], **parsed_result.get('metadata', {})}
    })

    # 8. 记录数据溯源
    lineage_id = lineage_tracker.track_extraction(
        patient_id, text, complete_result['data'], complete_result['metadata']
    )

    return {
        "success": compliance['compliant'],
        "data": complete_result['data'] if compliance['compliant'] else None,
        "metadata": {
            **complete_result['metadata'],
            "confidence_assessment": confidence_assessment,
            "validation_result": validation,
            "compliance_check": compliance,
            "lineage_id": lineage_id,
            "strict_mode": True
        },
        "requires_human_review": not compliance['compliant'] or
                                confidence_assessment['confidence_level'] in ['low', 'medium']
    }
```

这套严格的数据完整性控制机制确保：
1. **零容忍幻想数据**：任何不在原文中的信息都不会被填入
2. **强制NULL标记**：缺失的字段明确标记为NULL
3. **可信度评估**：每个字段都有置信度评分
4. **人工审核机制**：低置信度数据必须人工验证
5. **完整审计跟踪**：所有提取过程可追溯
6. **合规性检查**：严格模式合规性验证

## 🔍 质量控制和验证

### 1. 数据质量检查器

```python
class QualityController:
    def __init__(self, schema_loader: SchemaLoader):
        self.schema_loader = schema_loader

    def validate_completeness(self, data: Dict, schema_name: str,
                            required_fields: List[str] = None) -> Dict:
        """检查数据完整性"""
        schema = self.schema_loader.get_schema(schema_name)
        if not schema:
            return {"valid": False, "error": "Schema not found"}

        # 默认必填字段
        if not required_fields:
            required_fields = ['examDate', 'patientID', 'patientName']

        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                missing_fields.append(field)

        return {
            "valid": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "completeness_score": 1 - (len(missing_fields) / len(required_fields))
        }

    def validate_data_types(self, data: Dict, schema_name: str) -> Dict:
        """验证数据类型"""
        schema = self.schema_loader.get_schema(schema_name)
        if not schema:
            return {"valid": False, "error": "Schema not found"}

        type_errors = []
        for field_name, expected_type in schema['data_types'].items():
            if field_name in data and data[field_name] is not None:
                value = data[field_name]
                if expected_type == 'Number':
                    if not isinstance(value, (int, float)):
                        try:
                            float(value)
                        except ValueError:
                            type_errors.append(f"{field_name}: 期望数值型，实际为 {type(value).__name__}")
                elif expected_type == 'Boolean':
                    if not isinstance(value, bool) and str(value).lower() not in ['true', 'false', '0', '1']:
                        type_errors.append(f"{field_name}: 期望布尔型，实际为 {type(value).__name__}")

        return {
            "valid": len(type_errors) == 0,
            "type_errors": type_errors,
            "type_accuracy": 1 - (len(type_errors) / len(schema['data_types']))
        }

    def validate_value_ranges(self, data: Dict, schema_name: str) -> Dict:
        """验证数值范围（基于医学常识）"""
        range_errors = []

        # 定义常见医学指标的合理范围
        medical_ranges = {
            'systolicBP': (50, 250),
            'diastolicBP': (30, 150),
            'heartRate': (30, 200),
            'bodyTemperature': (30, 45),
            'hbA1cLevel': (3, 20),
            'fastingGlucose': (1, 50),
            'age': (0, 150),
            'weight': (0.5, 300),
            'height': (30, 250)
        }

        for field, (min_val, max_val) in medical_ranges.items():
            if field in data and data[field] is not None:
                try:
                    value = float(data[field])
                    if not (min_val <= value <= max_val):
                        range_errors.append(f"{field}: 值{value}超出合理范围[{min_val}, {max_val}]")
                except (ValueError, TypeError):
                    continue

        return {
            "valid": len(range_errors) == 0,
            "range_errors": range_errors
        }
```

### 2. 结果验证和修正

```python
class ResultValidator:
    def __init__(self, quality_controller: QualityController):
        self.qc = quality_controller

    def comprehensive_validation(self, data: Dict, schema_name: str) -> Dict:
        """综合验证"""
        results = {
            "completeness": self.qc.validate_completeness(data, schema_name),
            "data_types": self.qc.validate_data_types(data, schema_name),
            "value_ranges": self.qc.validate_value_ranges(data, schema_name)
        }

        # 计算总体质量分数
        total_score = (
            results["completeness"]["completeness_score"] * 0.4 +
            results["data_types"]["type_accuracy"] * 0.3 +
            (1.0 if results["value_ranges"]["valid"] else 0.5) * 0.3
        )

        return {
            "overall_quality_score": total_score,
            "quality_grade": self._get_quality_grade(total_score),
            "validation_details": results,
            "recommendations": self._generate_recommendations(results)
        }

    def _get_quality_grade(self, score: float) -> str:
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"

    def _generate_recommendations(self, results: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []

        if not results["completeness"]["valid"]:
            recommendations.append(f"补充缺失字段: {', '.join(results['completeness']['missing_fields'])}")

        if not results["data_types"]["valid"]:
            recommendations.append("检查并修正数据类型错误")

        if not results["value_ranges"]["valid"]:
            recommendations.append("检查异常数值，可能需要重新提取信息")

        if not recommendations:
            recommendations.append("数据质量良好，可直接使用")

        return recommendations
```

## 📊 性能监控和优化

### 1. 性能监控

```python
import time
from functools import wraps
import psutil
import asyncio

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'processing_times': [],
            'memory_usage': [],
            'api_calls': 0,
            'success_rate': 0
        }

    def performance_tracker(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = psutil.virtual_memory().used

            try:
                result = await func(*args, **kwargs)
                self.metrics['api_calls'] += 1

                # 记录成功率
                if result.get('success'):
                    self.metrics['success_rate'] += 1

                # 记录处理时间
                processing_time = time.time() - start_time
                self.metrics['processing_times'].append(processing_time)

                # 记录内存使用
                memory_used = psutil.virtual_memory().used - start_memory
                self.metrics['memory_usage'].append(memory_used)

                return result
            except Exception as e:
                self.metrics['api_calls'] += 1
                raise e

        return wrapper

    def get_performance_report(self) -> Dict:
        if not self.metrics['processing_times']:
            return {"status": "No data available"}

        return {
            "avg_processing_time": sum(self.metrics['processing_times']) / len(self.metrics['processing_times']),
            "max_processing_time": max(self.metrics['processing_times']),
            "min_processing_time": min(self.metrics['processing_times']),
            "success_rate": (self.metrics['success_rate'] / self.metrics['api_calls']) * 100,
            "total_api_calls": self.metrics['api_calls'],
            "avg_memory_usage": sum(self.metrics['memory_usage']) / len(self.metrics['memory_usage'])
        }
```

### 2. 缓存策略

```python
import redis
import hashlib
import json

class CacheManager:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.cache_ttl = 3600  # 1小时过期

    def _generate_cache_key(self, text: str, schema_name: str) -> str:
        """生成缓存键"""
        content = f"{text}:{schema_name}"
        return f"medical_data:{hashlib.md5(content.encode()).hexdigest()}"

    async def get_cached_result(self, text: str, schema_name: str) -> Optional[Dict]:
        """获取缓存结果"""
        cache_key = self._generate_cache_key(text, schema_name)
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            print(f"缓存读取失败: {e}")
        return None

    async def cache_result(self, text: str, schema_name: str, result: Dict):
        """缓存处理结果"""
        cache_key = self._generate_cache_key(text, schema_name)
        try:
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(result, ensure_ascii=False)
            )
        except Exception as e:
            print(f"缓存写入失败: {e}")
```

## 🚀 部署和使用指南

### 1. 环境配置

```yaml
# docker-compose.yml
version: '3.8'
services:
  medical-processor:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    volumes:
      - ./SchemaCSV:/app/SchemaCSV
      - ./data:/app/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=medical_data
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 2. 快速开始

```bash
# 1. 克隆项目并安装依赖
git clone <repository-url>
cd medical-data-processor
pip install -r requirements.txt

# 2. 设置环境变量
export OPENAI_API_KEY="your-api-key"

# 3. 启动Redis（如果使用缓存）
docker run -d -p 6379:6379 redis:alpine

# 4. 启动API服务
python api_server.py

# 5. 测试API
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{"text": "患者血糖8.5mmol/L", "schema_name": "diabetes-comprehensive"}'
```

### 3. 生产环境优化建议

1. **负载均衡**: 使用nginx或AWS ALB分发请求
2. **缓存策略**: Redis集群提高缓存性能
3. **数据库**: PostgreSQL存储结构化数据
4. **监控**: Prometheus + Grafana监控系统性能
5. **安全**: API认证和数据加密
6. **备份**: 定期备份处理结果和配置

## 📝 最佳实践

### 1. 提示词优化
- 根据不同Schema类型调整提示词
- 添加医学专业术语和上下文
- 使用少样本学习提升准确率

### 2. 错误处理
- 实现重试机制
- 记录详细错误日志
- 提供人工审核接口

### 3. 质量保证
- 多层验证机制
- 专家标注数据集验证
- 持续模型性能评估

### 4. 成本控制
- 智能缓存减少API调用
- 批量处理提高效率
- 使用不同模型处理不同复杂度任务

通过以上方案，可以高效地将非结构化医疗数据转换为符合64个Schema标准的结构化数据，大幅提升医疗数据处理效率和质量。

## 🔗 相关资源

- [OpenAI API 文档](https://platform.openai.com/docs)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Pandas 数据处理](https://pandas.pydata.org/docs/)
- [Redis 缓存使用](https://redis.io/documentation)

---
**维护团队**: 内分泌代谢疾病数据标准化项目组
**最后更新**: 2024年12月01日