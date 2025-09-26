/**
 * 三诺CGM数据推送接口测试脚本
 * 使用方法：node test-sinocare-api.js
 */

const axios = require('axios');

// 配置项
const config = {
  // 测试服务器地址（需要根据实际部署地址修改）
  // baseURL: 'http://localhost:8000',
  baseURL: 'https://gplus.imedpower.com',
  
  // 机构映射配置（需要在数据库中预先配置）
  customerName: '测试医院', // 需要在 sinocare_org_mapping 表中配置
  organizationId: 11, // 对应的机构ID
};

// 测试数据
const testData = {
  "data": {
    "testId": `test-${Date.now()}`,
    "deviceSn": "SINOCARE001",
    "testResult": "6.5",
    "serialNo": 1,
    "testTime": "2024-01-16 12:33:33",
    "idCard": "110101199001011234",
    "visitId": "V20240115001",
    "patientName": "张三",
    "customerName": config.customerName,
    "patientId": "P20240115001",
    "inSerialId": "S20240115001",
    "status": "0", // 0=有效数据，1=无效数据
    "cgmDay": 14,
    "increMinute": 3,
    "low": 70,
    "high": 180,
    "cgmStatus": "2"
  },
  "reservedCode": "01"
};

// 发送测试请求
async function testSinocareCallback() {
  try {
    console.log('🚀 开始测试三诺CGM数据推送接口...');
    console.log('📡 目标地址:', `${config.baseURL}/api/open/sinocare/callback`);
    console.log('📊 测试数据:', JSON.stringify(testData, null, 2));
    
    const response = await axios.post(
      `${config.baseURL}/api/open/sinocare/callback`,
      testData,
      {
        headers: {
          'Content-Type': 'application/json',
          'X-Forwarded-For': '127.0.0.1', // 模拟真实IP
        },
        timeout: 10000, // 10秒超时
      }
    );

    console.log('\n✅ 请求成功!');
    console.log('📋 响应状态:', response.status);
    console.log('📄 响应数据:', JSON.stringify(response.data, null, 2));

    // 检查响应格式
    if (response.data.code === '00000') {
      console.log('\n🎉 接口返回成功状态!');
    } else {
      console.log('\n⚠️ 接口返回错误状态:', response.data.desc);
    }

  } catch (error) {
    console.error('\n❌ 请求失败:');
    
    if (error.response) {
      console.error('📄 响应状态:', error.response.status);
      console.error('📄 响应数据:', JSON.stringify(error.response.data, null, 2));
    } else if (error.request) {
      console.error('🌐 网络错误:', error.message);
    } else {
      console.error('🔧 配置错误:', error.message);
    }
  }
}

// 生成多条测试数据
async function testMultipleData() {
  console.log('\n🔄 开始批量测试...');
  
  // 循环生成1800条数据，时间间隔3分钟，testResult每次随机±0.5%，范围2.2~25
  const testCases = [];
  const startTime = new Date("2024-01-19 08:00:00");
  let lastResult = 5.0; // 初始血糖值
  for (let i = 0; i < 1800; i++) {
    // 随机决定增加或减少
    const changePercent = (Math.random() < 0.5 ? -1 : 1) * 0.005;
    let newResult = lastResult * (1 + changePercent);
    // 限制在2.2~25之间
    newResult = Math.max(2.2, Math.min(25, newResult));
    // 生成时间
    const testTime = new Date(startTime.getTime() + i * 3 * 60 * 1000);
    // 格式化时间为"YYYY-MM-DD HH:mm:ss"
    const pad = n => n.toString().padStart(2, '0');
    const formatTime = d =>
      `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
    testCases.push({
      ...testData.data,
      testResult: newResult.toFixed(1),
      serialNo: i + 1,
      testTime: formatTime(testTime),
    });
    lastResult = newResult;
  }

  for (let i = 0; i < testCases.length; i++) {
    const data = {
      data: { ...testCases[i], testId: `batch-test-${Date.now()}-${i}` },
      reservedCode: "01"
    };

    console.log(`\n📡 发送第 ${i + 1}/${testCases.length} 条数据...`);
    console.log(`   血糖值: ${data.data.testResult}, 状态: ${data.data.status}`);

    try {
      const response = await axios.post(
        `${config.baseURL}/api/open/sinocare/callback`,
        data,
        {
          headers: { 'Content-Type': 'application/json' },
          timeout: 5000,
        }
      );

      if (response.data.code === 0) {
        console.log(`   ✅ 第 ${i + 1} 条数据发送成功`);
      } else {
        console.log(`   ⚠️ 第 ${i + 1} 条数据返回错误: ${response.data.desc}`);
      }
    } catch (error) {
      console.error(`   ❌ 第 ${i + 1} 条数据发送失败:`, error.message);
    }

    // 间隔1秒发送下一条
    // await new Promise(resolve => setTimeout(resolve, 1000));
  }
}

// 测试错误情况
async function testErrorCases() {
  console.log('\n🧪 开始错误情况测试...');

  const errorCases = [
    {
      name: '错误的reservedCode',
      data: { ...testData, reservedCode: "99" }
    },
    {
      name: '缺少必需字段',
      data: { 
        data: { ...testData.data, testResult: undefined },
        reservedCode: "01"
      }
    },
    {
      name: '不存在的机构',
      data: {
        ...testData,
        data: { ...testData.data, customerName: "不存在的医院" }
      }
    }
  ];

  for (const testCase of errorCases) {
    testCase.data.data.testId = `test-${Date.now()}`;
    console.log(`\n🔍 测试: ${testCase.name}`);
    
    try {
      const response = await axios.post(
        `${config.baseURL}/api/open/sinocare/callback`,
        testCase.data,
        {
          headers: { 'Content-Type': 'application/json' },
          timeout: 5000,
        }
      );

      console.log(`   响应: ${JSON.stringify(response.data)}`);
    } catch (error) {
      if (error.response) {
        console.log(`   错误响应: ${JSON.stringify(error.response.data)}`);
      } else {
        console.log(`   网络错误: ${error.message}`);
      }
    }
  }
}

// 主函数
async function main() {
  console.log('🏥 三诺CGM数据推送接口测试工具');
  console.log('=====================================');
  
  // 检查配置
  console.log('⚙️ 配置检查:');
  console.log(`   服务器地址: ${config.baseURL}`);
  console.log(`   测试机构: ${config.customerName}`);
  console.log(`   机构ID: ${config.organizationId}`);
  
  console.log('\n⚠️ 请确保:');
  console.log('   1. 服务器已启动并可访问');
  console.log('   2. 数据库迁移已执行');
  console.log('   3. sinocare_org_mapping表中已配置机构映射');
  console.log('   4. 机构中至少有一个患者（用于测试）');

  // 等待用户确认
  console.log('\n按Enter键继续，或Ctrl+C取消...');
  await new Promise(resolve => {
    process.stdin.once('data', resolve);
  });

  try {
    // 基础功能测试
    await testSinocareCallback();
    
    // 批量数据测试
    await testMultipleData();
    
    // 错误情况测试
    await testErrorCases();

    console.log('\n🎉 所有测试完成!');
    console.log('\n📋 测试后检查项:');
    console.log('   1. 查看服务器日志确认数据处理情况');
    console.log('   2. 检查MongoDB中的sinocare_cgm_log集合');
    console.log('   3. 检查PostgreSQL中的glucose表是否有新数据');

  } catch (error) {
    console.error('\n💥 测试过程中发生错误:', error.message);
  }
}

// 处理命令行参数
const args = process.argv.slice(2);
if (args.includes('--help') || args.includes('-h')) {
  console.log(`
使用方法:
  node test-sinocare-api.js           # 运行完整测试
  node test-sinocare-api.js --single  # 只运行单次测试
  node test-sinocare-api.js --batch   # 只运行批量测试
  node test-sinocare-api.js --error   # 只运行错误测试

配置说明:
  修改脚本顶部的config对象以适配你的环境:
  - baseURL: 服务器地址
  - customerName: 在数据库中配置的医院名称
  - organizationId: 对应的机构ID
`);
  process.exit(0);
}

// 根据参数运行特定测试
if (args.includes('--single')) {
  testSinocareCallback();
} else if (args.includes('--batch')) {
  testMultipleData();
} else if (args.includes('--error')) {
  testErrorCases();
} else {
  main();
} 