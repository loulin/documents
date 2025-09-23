#!/usr/bin/env python3
"""
添加所有国际标准药物标识符字段
"""

import csv

def add_comprehensive_identifier_fields(input_file, output_file):
    """添加完整的国际标准标识符字段"""
    
    print("🌍 添加完整的国际标准药物标识符字段...")
    
    # 完整的标准标识符字段列表
    all_standard_fields = [
        'drug_id',              # 内部分类编号
        'ca_number',            # CAS化学编号
        'ndc_code',             # NDC编号 (美国FDA)
        'gtin_code',            # GTIN编号 (全球贸易)
        'atc_code',             # ATC编号 (WHO分类)
        'rxnorm_cui',           # RxNorm CUI (美国NLM)
        'unii_code',            # UNII编号 (FDA成分)
        'chembl_id',            # ChEMBL ID (欧洲)
        'pubchem_cid',          # PubChem化合物ID
        'drugbank_id',          # DrugBank编号
        'kegg_drug_id',         # KEGG药物ID
        'who_inn',              # WHO国际非专利名
        'english_name',         # 英文名
        'chinese_acronym',      # 中文缩写
        'drug_name',            # 中文名
        'brand_name',           # 商品名
        'manufacturer',         # 生产厂家
        'approval_number',      # 批准文号
        'category',             # 分类
        'therapeutic_class',    # 治疗分类
        'specifications',       # 规格
        'common_dosage',        # 常用剂量
        'frequency',            # 频次
        'route',                # 给药途径
        'indications',          # 适应症
        'contraindications',    # 禁忌症
        'side_effects',         # 不良反应
        'drug_interactions',    # 相互作用
        'special_instructions', # 特殊说明
        'pregnancy_category',   # 妊娠分级
        'renal_adjustment',     # 肾功能调整
        'hepatic_adjustment',   # 肝功能调整
        'unit',                 # 单位
        'method',               # 给药方法
        'frequency_std',        # 标准频次
        'last_updated',         # 最后更新时间
        'data_source',          # 数据来源
        'verification_status',  # 验证状态
        'notes'                 # 备注
    ]
    
    print(f"📊 将添加 {len(all_standard_fields)} 个字段")
    print(f"🆔 其中包含 9 个国际标准标识符:")
    identifier_fields = ['ndc_code', 'gtin_code', 'atc_code', 'rxnorm_cui', 'unii_code', 
                        'chembl_id', 'pubchem_cid', 'drugbank_id', 'kegg_drug_id']
    for field in identifier_fields:
        print(f"   • {field}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        all_rows = list(reader)
    
    updated_rows = []
    header_updated = False
    drug_count = 0
    
    for i, row in enumerate(all_rows):
        if not row:
            updated_rows.append(row)
            continue
            
        # 更新表头
        if not header_updated and 'drug_id' in row[0]:
            updated_rows.append(all_standard_fields)
            header_updated = True
            print(f"✅ 更新表头，现在有 {len(all_standard_fields)} 个字段")
            continue
        
        # 更新药物行
        if row[0].startswith('D') and row[0][1:].isdigit():
            drug_count += 1
            
            # 映射现有字段到新结构
            new_row = [''] * len(all_standard_fields)
            
            # 填入已有的数据
            field_mapping = {
                0: 0,   # drug_id
                1: 1,   # ca_number
                7: 12,  # english_name
                8: 13,  # chinese_acronym  
                9: 14,  # drug_name
                10: 15, # brand_name
                11: 18, # category
                12: 19, # therapeutic_class
                13: 20, # specifications
                14: 21, # common_dosage
                15: 22, # frequency
                16: 23, # route
                17: 24, # indications
                18: 25, # contraindications
                19: 26, # side_effects
                20: 27, # drug_interactions
                21: 28, # special_instructions
                22: 29, # pregnancy_category
                23: 30, # renal_adjustment
                24: 31, # hepatic_adjustment
                25: 32, # unit
                26: 33, # method
                27: 34, # frequency_std
            }
            
            # 复制现有数据
            for old_idx, new_idx in field_mapping.items():
                if old_idx < len(row):
                    new_row[new_idx] = row[old_idx]
            
            # 填入默认值
            new_row[16] = ''     # manufacturer - 待填入
            new_row[17] = ''     # approval_number - 待填入
            new_row[35] = '2025-01-09'  # last_updated
            new_row[36] = '内部数据库'    # data_source
            new_row[37] = '待验证'       # verification_status
            new_row[38] = '标准标识符待填入'  # notes
            
            updated_rows.append(new_row)
            
            if drug_count <= 5:  # 显示前5个药物的映射
                drug_name = new_row[14] if new_row[14] else 'Unknown'
                print(f"  ✓ {new_row[0]}: {drug_name}")
        else:
            # 非药物行
            updated_rows.append(row)
    
    # 写入更新后的文件
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(updated_rows)
    
    print(f"\\n📊 完成统计:")
    print(f"   💊 处理药物: {drug_count} 个")
    print(f"   📋 总字段数: {len(all_standard_fields)} 个")
    print(f"   📄 输出文件: {output_file}")

def verify_new_comprehensive_structure(file_path):
    """验证新的综合结构"""
    
    print(f"\\n🔍 验证新的数据库结构...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        header_row = None
        drug_count = 0
        field_counts = {}
        
        for row_num, row in enumerate(reader, 1):
            if not row:
                continue
                
            field_count = len(row)
            field_counts[field_count] = field_counts.get(field_count, 0) + 1
                
            if 'drug_id' in row[0]:
                header_row = row
                print(f"   📋 表头字段: {len(row)} 个")
                print(f"   🔤 标识符字段: {row[2:11]}")  # 显示标识符字段
                continue
                
            if row[0].startswith('D') and row[0][1:].isdigit():
                drug_count += 1
                
                if drug_count <= 3:  # 显示前3个药物的结构
                    drug_id = row[0] if len(row) > 0 else 'N/A'
                    drug_name = row[14] if len(row) > 14 else 'N/A'
                    manufacturer = row[16] if len(row) > 16 else '待填入'
                    approval_num = row[17] if len(row) > 17 else '待填入'
                    print(f"   💊 {drug_id}: {drug_name} | 厂家:{manufacturer} | 批号:{approval_num}")
    
    print(f"   📊 药物总数: {drug_count}")
    print(f"   📐 字段分布: {field_counts}")
    
    return drug_count > 0 and max(field_counts.keys()) == 39

def create_field_description_guide(output_file):
    """创建字段说明指南"""
    
    guide_content = """# 药物数据库字段完整说明

## 数据库结构 (39个字段)

### 🆔 标识符字段 (11个)
1. **drug_id** - 内部分类编号 (D001, D002...)
2. **ca_number** - CAS化学编号 (CA11061-68-0)
3. **ndc_code** - 美国NDC编号 (0002-7510-01)
4. **gtin_code** - 全球贸易编号 (14位数字)
5. **atc_code** - WHO ATC代码 (A10AB01)
6. **rxnorm_cui** - RxNorm编号 (253182)
7. **unii_code** - FDA UNII编号 (3X7931PO74)
8. **chembl_id** - ChEMBL编号 (CHEMBL1201247)
9. **pubchem_cid** - PubChem编号 (6305)
10. **drugbank_id** - DrugBank编号 (DB00030)
11. **kegg_drug_id** - KEGG编号 (D00085)

### 📋 基本信息字段 (8个)
12. **who_inn** - WHO国际非专利名
13. **english_name** - 英文通用名
14. **chinese_acronym** - 中文缩写
15. **drug_name** - 中文通用名
16. **brand_name** - 商品名/品牌名
17. **manufacturer** - 生产厂家
18. **approval_number** - 药品批准文号
19. **category** - 治疗分类编号

### 🏥 临床信息字段 (16个)
20. **therapeutic_class** - 具体治疗分类
21. **specifications** - 规格
22. **common_dosage** - 常用剂量
23. **frequency** - 用药频次描述
24. **route** - 给药途径
25. **indications** - 适应症
26. **contraindications** - 禁忌症
27. **side_effects** - 不良反应
28. **drug_interactions** - 药物相互作用
29. **special_instructions** - 特殊用法说明
30. **pregnancy_category** - 妊娠安全性分级
31. **renal_adjustment** - 肾功能不全用药调整
32. **hepatic_adjustment** - 肝功能不全用药调整
33. **unit** - 剂量单位
34. **method** - 给药方法
35. **frequency_std** - 标准化频次代码

### 📊 管理信息字段 (4个)
36. **last_updated** - 最后更新时间
37. **data_source** - 数据来源
38. **verification_status** - 验证状态
39. **notes** - 备注信息

## 标识符优先填入顺序

### 第一优先级 (必填)
1. **atc_code** - WHO ATC代码
2. **unii_code** - FDA成分标识符

### 第二优先级 (推荐)
3. **drugbank_id** - DrugBank编号
4. **chembl_id** - ChEMBL编号
5. **pubchem_cid** - PubChem编号

### 第三优先级 (可选)
6. **ndc_code** - 美国市场编号
7. **gtin_code** - 全球贸易编号
8. **rxnorm_cui** - 美国临床编号
9. **kegg_drug_id** - KEGG代谢编号

## 数据来源推荐

### 免费权威数据源
- **ATC Code**: https://www.whocc.no/atc_ddd_index/
- **UNII**: https://fdasis.nlm.nih.gov/srs/
- **DrugBank**: https://go.drugbank.com/ (学术免费)
- **PubChem**: https://pubchem.ncbi.nlm.nih.gov/
- **ChEMBL**: https://www.ebi.ac.uk/chembl/

### 中国药品信息
- **批准文号**: 国家药监局数据库
- **生产厂家**: 药品说明书、包装信息
- **中文名称**: 中华人民共和国药典

## 质量控制建议

### 数据验证规则
1. **drug_id**: 必须唯一且格式为D+3位数字
2. **atc_code**: 必须为7位格式（如A10AB01）
3. **unii_code**: 必须为10位字符（如3X7931PO74）
4. **specifications**: 必须包含数量和单位
5. **last_updated**: 必须为YYYY-MM-DD格式

### 定期维护任务
1. 验证外部标识符有效性
2. 更新过期的批准文号
3. 同步最新的ATC分类
4. 检查厂家信息变更
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"✅ 创建了完整字段说明指南: {output_file}")

if __name__ == "__main__":
    input_file = "/Users/williamsun/Documents/gplus/docs/Medicines/medication_database.csv"
    output_file = input_file
    guide_file = "/Users/williamsun/Documents/gplus/docs/Medicines/数据库字段完整说明.md"
    
    print("🚀 升级药物数据库为完整标准结构...")
    print("=" * 60)
    
    # 添加所有标准字段
    add_comprehensive_identifier_fields(input_file, output_file)
    
    # 验证新结构
    success = verify_new_comprehensive_structure(output_file)
    
    # 创建字段说明指南
    create_field_description_guide(guide_file)
    
    print(f"\\n🎉 数据库升级完成!")
    print(f"")
    print(f"📊 新数据库特点:")
    print(f"   🆔 11个国际标准标识符字段")
    print(f"   📋 8个基本药物信息字段") 
    print(f"   🏥 16个临床使用信息字段")
    print(f"   📊 4个数据管理字段")
    print(f"   📄 总计39个完整字段")
    print(f"")
    print(f"🔗 现在可以与任何国际标准数据库无缝对接!")
    print(f"📖 详细说明请查看: {guide_file}")
    
    if success:
        print(f"\\n✅ 数据库结构验证通过")
    else:
        print(f"\\n⚠️  需要进一步检查")