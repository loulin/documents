#!/usr/bin/env python3
"""
添加国际标准药物标识符字段
替换自编的unique_product_id为标准字段
"""

import csv

# 国际标准药物标识符说明
STANDARD_IDENTIFIERS = {
    'NDC': 'National Drug Code (美国FDA)',
    'GTIN': 'Global Trade Item Number (全球贸易项目代码)', 
    'ATC': 'Anatomical Therapeutic Chemical Classification (WHO)',
    'RxNorm': 'RxNorm Concept Unique Identifier (美国NLM)',
    'UNII': 'Unique Ingredient Identifier (FDA)',
    'ChEMBL': 'ChEMBL ID (欧洲生物信息学研究所)',
    'PubChem': 'PubChem Compound ID',
    'DrugBank': 'DrugBank Accession Number',
    'KEGG': 'KEGG Drug ID',
}

def add_standard_identifier_fields(input_file, output_file):
    """添加标准药物标识符字段"""
    
    print("🏛️ 添加国际标准药物标识符字段...")
    print("\n📋 支持的标准标识符:")
    for code, desc in STANDARD_IDENTIFIERS.items():
        print(f"   • {code}: {desc}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        all_rows = list(reader)
    
    updated_rows = []
    header_updated = False
    
    for i, row in enumerate(all_rows):
        if not row:
            updated_rows.append(row)
            continue
            
        # 更新表头
        if not header_updated and 'drug_id' in row[0]:
            # 替换unique_product_id为标准字段
            new_header = [
                'drug_id',           # 内部分类编号
                'ca_number',         # CAS号
                'ndc_code',          # NDC编号 (美国标准)
                'gtin_code',         # GTIN编号 (全球标准)
                'atc_code',          # ATC编号 (WHO分类)
                'rxnorm_cui',        # RxNorm编号
                'unii_code',         # UNII编号 (FDA成分标识)
                'english_name',
                'chinese_acronym', 
                'drug_name',
                'brand_name',
                'category',
                'therapeutic_class',
                'specifications',
                'common_dosage',
                'frequency',
                'route',
                'indications',
                'contraindications', 
                'side_effects',
                'drug_interactions',
                'special_instructions',
                'pregnancy_category',
                'renal_adjustment',
                'hepatic_adjustment',
                'unit',
                'method',
                'frequency_std',
                'notes'  # 备注字段，记录标识符来源
            ]
            updated_rows.append(new_header)
            header_updated = True
            print(f"✅ 更新表头，现在有 {len(new_header)} 个字段")
            continue
        
        # 更新药物行
        if row[0].startswith('D') and row[0][1:].isdigit():
            if len(row) >= 24:
                # 移除自编的unique_product_id，添加标准字段
                new_row = [
                    row[0],    # drug_id
                    row[1],    # ca_number
                    '',        # ndc_code - 待填入
                    '',        # gtin_code - 待填入  
                    '',        # atc_code - 待填入
                    '',        # rxnorm_cui - 待填入
                    '',        # unii_code - 待填入
                    row[3],    # english_name (跳过原unique_product_id)
                    row[4],    # chinese_acronym
                    row[5],    # drug_name
                    row[6],    # brand_name
                    row[7],    # category
                    row[8],    # therapeutic_class
                    row[9],    # specifications
                    row[10],   # common_dosage
                    row[11],   # frequency
                    row[12],   # route
                    row[13],   # indications
                    row[14],   # contraindications
                    row[15],   # side_effects
                    row[16],   # drug_interactions
                    row[17],   # special_instructions
                    row[18],   # pregnancy_category
                    row[19],   # renal_adjustment
                    row[20],   # hepatic_adjustment
                    row[21],   # unit
                    row[22],   # method
                    row[23],   # frequency_std
                    '标准标识符待填入'  # notes
                ]
                updated_rows.append(new_row)
            else:
                print(f"⚠️  {row[0]} 字段数不足")
        else:
            # 非药物行
            updated_rows.append(row)
    
    # 写入更新后的文件
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(updated_rows)
    
    print(f"✅ 标准字段已添加到数据库")

def create_identifier_mapping_guide(output_file):
    """创建标识符映射指南"""
    
    guide_content = """# 药物标识符映射指南

## 国际标准药物标识符说明

### 1. NDC (National Drug Code)
- **管理机构**: 美国FDA
- **格式**: 10位数字，格式为 XXXXX-XXX-XX
- **用途**: 美国市场药物的官方标识
- **获取方式**: FDA Orange Book, DailyMed
- **示例**: 0002-7510-01 (Humalog)

### 2. GTIN (Global Trade Item Number)
- **管理机构**: GS1国际组织
- **格式**: 8, 12, 13, 或 14位数字
- **用途**: 全球贸易中产品的唯一标识
- **获取方式**: 药品包装条码、GS1数据库
- **示例**: 03006480001751

### 3. ATC Code (WHO分类)
- **管理机构**: 世界卫生组织WHO
- **格式**: 7位字母数字码
- **用途**: 按治疗用途分类药物
- **获取方式**: WHO官方ATC/DDD Index
- **示例**: A10AB01 (人胰岛素)

### 4. RxNorm CUI
- **管理机构**: 美国国家医学图书馆NLM  
- **格式**: 数字编码
- **用途**: 标准化临床药物名称
- **获取方式**: RxNorm数据库
- **示例**: 253182 (Insulin Human)

### 5. UNII (Unique Ingredient Identifier)
- **管理机构**: 美国FDA
- **格式**: 10位字符码
- **用途**: 标识药物活性成分
- **获取方式**: FDA UNII数据库
- **示例**: 3X7931PO74 (Insulin Human)

## 推荐的标识符优先级

### 对于中国药品数据库：
1. **ATC Code** - WHO国际标准，广泛认可
2. **UNII** - FDA标准，识别活性成分
3. **DrugBank ID** - 学术研究常用
4. **ChEMBL ID** - 欧洲标准，化学结构相关

### 对于国际对接：
1. **GTIN** - 全球贸易标准
2. **ATC Code** - WHO分类标准
3. **RxNorm CUI** - 美国临床标准
4. **UNII** - FDA成分标准

## 获取标识符的数据源

### 免费公开数据源：
- **WHO ATC/DDD**: https://www.whocc.no/atc_ddd_index/
- **FDA UNII**: https://fdasis.nlm.nih.gov/srs/
- **RxNorm**: https://www.nlm.nih.gov/research/umls/rxnorm/
- **DrugBank**: https://go.drugbank.com/
- **ChEMBL**: https://www.ebi.ac.uk/chembl/

### 商业数据源：
- **First Databank (FDB)**
- **Wolters Kluwer (Medi-Span)**
- **IQVIA (formerly IMS Health)**

## 实施建议

### 阶段1: 添加ATC代码
优先为所有药物添加WHO ATC代码，这是最重要的国际标准。

### 阶段2: 添加UNII代码
为活性成分添加FDA UNII标识符。

### 阶段3: 添加其他标识符
根据对接需求添加GTIN、RxNorm等标识符。

### 注意事项：
1. 不同标识符有不同的颗粒度（成分级别 vs 产品级别）
2. 需要定期更新标识符数据库
3. 复方制剂可能需要多个UNII编码
4. 中国特有品种可能缺乏国际标识符

## 数据对接策略

### 与国际数据库对接：
- 优先使用ATC Code进行药物分类匹配
- 使用UNII进行活性成分匹配
- 使用DrugBank ID进行详细信息匹配

### 与商业系统对接：
- 使用GTIN进行产品级别匹配
- 使用NDC进行美国市场匹配
- 保持内部drug_id用于系统内部管理

### 映射维护：
- 建立标识符映射表
- 定期验证标识符有效性
- 记录标识符来源和更新时间
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"✅ 创建了标识符映射指南: {output_file}")

def show_next_steps():
    """显示后续步骤建议"""
    
    print(f"\n📋 后续实施步骤建议:")
    print(f"")
    print(f"1. **选择标识符优先级**")
    print(f"   推荐: ATC Code > UNII > DrugBank ID")
    print(f"")
    print(f"2. **获取标识符数据**") 
    print(f"   • 从WHO网站获取ATC代码")
    print(f"   • 从FDA数据库获取UNII代码")
    print(f"   • 从DrugBank获取DrugBank ID")
    print(f"")
    print(f"3. **逐步填入标识符**")
    print(f"   • 先处理常用药物")
    print(f"   • 建立验证机制")
    print(f"   • 记录数据来源")
    print(f"")
    print(f"4. **建立对接策略**")
    print(f"   • 制定标识符匹配规则") 
    print(f"   • 处理映射冲突")
    print(f"   • 定期同步更新")

if __name__ == "__main__":
    input_file = "/Users/williamsun/Documents/gplus/docs/Medicines/medication_database.csv"
    output_file = input_file
    guide_file = "/Users/williamsun/Documents/gplus/docs/Medicines/药物标识符映射指南.md"
    
    print("🔄 将自编标识符替换为国际标准字段...")
    
    # 替换为标准字段
    add_standard_identifier_fields(input_file, output_file)
    
    # 创建映射指南
    create_identifier_mapping_guide(guide_file)
    
    # 显示后续步骤
    show_next_steps()
    
    print(f"\n💡 总结:")
    print(f"   ❌ 移除了自编的unique_product_id")
    print(f"   ✅ 添加了5个国际标准标识符字段")
    print(f"   📖 创建了详细的实施指南")
    print(f"   🔗 这些标准字段便于与其他数据库对接")