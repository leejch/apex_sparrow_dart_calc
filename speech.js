const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const SpeechSynthesis = window.speechSynthesis;

class SpeechHandler {
  constructor() {
    this.recognition = new SpeechRecognition();
    this.recognition.interimResults = false;
    this.recognition.lang = 'zh-CN';
    this.recognition.continuous = false;
    this.recognition.maxAlternatives = 1;
    
    this.isListening = false;
    this.isSpeaking = false;
    this.lastWindowFocus = true;
    this.speechQueue = [];
    this.setupRecognition();

    // 监听窗口焦点变化
    window.addEventListener('focus', () => {
      this.lastWindowFocus = true;
      if (this.isListening && !this.isSpeaking) {
        this.recognition.start();
      }
    });
    
    window.addEventListener('blur', () => {
      this.lastWindowFocus = false;
      if (this.isListening) {
        this.recognition.stop();
      }
    });

    this.lastSetDistance = null;  // 添加距离记录
    this.lastSetAngle = null;     // 添加角度记录
  }

  createLogBox() {
    // 先移除已存在的日志框
    const existingLogBox = document.getElementById('voiceLogBox');
    if (existingLogBox) {
      existingLogBox.remove();
    }

    // 创建新的日志框容器
    const logBox = document.createElement('div');
    logBox.id = 'voiceLogBox';
    
    // 设置样式
    logBox.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      width: 300px;
      max-height: 400px;
      overflow-y: auto;
      background: rgba(0, 0, 0, 0.8);
      color: white;
      padding: 10px;
      border-radius: 5px;
      font-size: 14px;
      z-index: 9999;
      font-family: Arial, sans-serif;
      box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    `;

    // 创建标题
    const title = document.createElement('div');
    title.style.cssText = `
      font-weight: bold;
      margin-bottom: 10px;
      padding-bottom: 5px;
      border-bottom: 1px solid rgba(255,255,255,0.3);
    `;
    title.textContent = '语音识别日志';
    
    // 创建日志内容容器
    const logContent = document.createElement('div');
    logContent.id = 'voiceLogContent';
    
    // 组装日志框
    logBox.appendChild(title);
    logBox.appendChild(logContent);
    
    // 添加到页面
    document.body.appendChild(logBox);
    
    // 确认日志框已创建
    this.addLog('日志系统初始化完成');
  }

  addLog(text, type = 'info') {
    const logContent = document.getElementById('voiceLogContent');
    if (!logContent) {
      console.error('日志容器不存在');
      return;
    }
    
    const logEntry = document.createElement('div');
    logEntry.style.cssText = `
      padding: 5px 0;
      border-bottom: 1px solid rgba(255,255,255,0.1);
      color: ${type === 'error' ? '#ff6b6b' : '#fff'};
      font-size: 13px;
    `;
    
    const time = new Date().toLocaleTimeString();
    logEntry.textContent = `[${time}] ${text}`;
    
    // 在顶部插入新日志
    logContent.insertBefore(logEntry, logContent.firstChild);
    
    // 限制日志数量
    while (logContent.children.length > 10) {
      logContent.removeChild(logContent.lastChild);
    }
  }

  setupRecognition() {
    this.recognition.addEventListener('result', (event) => {
      const transcript = event.results[0][0].transcript.trim();
      this.addLog(`识别结果: ${transcript}`);
      this.processCommand(transcript);
    });

    this.recognition.addEventListener('end', () => {
      if (this.isListening && !this.isSpeaking) {
        this.recognition.start();
      }
    });

    this.recognition.addEventListener('error', (event) => {
      this.addLog(`识别错误: ${event.error}`, 'error');
      if (this.isListening && !this.isSpeaking) {
        setTimeout(() => {
          this.recognition.start();
        }, 1000);
      }
    });
  }

  processCommand(transcript) {
    // 汉字数字映射表
    const chineseNumbers = {
      '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
      '十': 10, '百': 100, '千': 1000, '万': 10000,
      '点': '.', '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9
    };

    // 将汉字数字转换为阿拉伯数字
    function parseChineseNumber(text) {
      let result = 0;
      let decimal = 0;
      let isDecimal = false;
      let temp = 0;
      let lastUnit = 1;

      for (let i = 0; i < text.length; i++) {
        const char = text[i];
        if (char === '点') {
          isDecimal = true;
          continue;
        }

        const num = chineseNumbers[char];
        if (num !== undefined) {
          if (isDecimal) {
            decimal = decimal * 10 + num;
          } else if (num >= 10) {
            if (temp === 0) temp = 1;
            if (num > lastUnit) {
              result = (result + temp) * num;
              temp = 0;
            } else {
              result = result + temp * num;
              temp = 0;
            }
            lastUnit = num;
          } else {
            temp = num;
          }
        }
      }

      result += temp;
      if (decimal > 0) {
        result += decimal / Math.pow(10, decimal.toString().length);
      }

      return result;
    }

    // 处理阿拉伯数字（包括小数）
    function parseArabicNumber(text) {
      // 移除所有空格
      text = text.replace(/\s+/g, '');
      // 确保小数点前后的数字被正确解析
      const number = parseFloat(text.replace(/[^0-9.]/g, ''));
      return isNaN(number) ? 0 : number;
    }

    // 处理距离命令 - 匹配汉字数字和阿拉伯数字
    const distancePattern = /.*?([零一二三四五六七八九十百千万\d]+(?:点[零一二三四五六七八九\d]+)?|\d+(?:\.\d+)?)\s*米/;
    const distanceMatch = transcript.match(distancePattern);
    if (distanceMatch) {
      const distanceText = distanceMatch[1];
      const distance = /^\d+\.?\d*$/.test(distanceText) ? 
        parseArabicNumber(distanceText) : 
        parseChineseNumber(distanceText);

      this.addLog(`解析距离: ${distance} (原文: ${distanceText})`);
      document.getElementById('inputD').value = distance;
      this.speak(`设置距离${distance}米`);
      this.lastSetDistance = distance;  // 记录设置的距离
      this.checkAndCalculate();  // 检查是否可以计算
      return;
    }

    // 处理倾角命令 - 匹配汉字数字和阿拉伯数字
    const anglePattern = /.*?([零一二三四五六七八九十百千万\d]+(?:点[零一二三四五六七八九\d]+)?|\d+(?:\.\d+)?)\s*[度°]/;
    const angleMatch = transcript.match(anglePattern);
    if (angleMatch) {
      const angleText = angleMatch[1];
      let angle = /^\d+\.?\d*$/.test(angleText) ? 
        parseArabicNumber(angleText) : 
        parseChineseNumber(angleText);
      
      // 检查是否包含负数指示词（包括所有fu音的汉字）
      const negativeIndicators = [
        '负', '付', '复', '府', '父', '腹', '赴', '富', '副', '妇', '抚', '辅', '俯', '斧', '釜', '脯', '腐', '覆',
        '赋', '咐', '附', '驸', '氟', '伏', '扶', '浮', '符', '芙', '苻', '蝠', '凫', '孵', '敷', '肤', '麸', '服',
        '福', '幅', '府', '辐', '蝮', '黼', '弗', '拂', '茯', '氟', '桴', '涪', '菔', '蚨', '绂', '绋', '茀', '郛',
        '艴', '拊', '黻', '荂', '芾', '咐', '赙', '复', '馥', '蝜', '蚹', '蜉', '蝮', '鲋', '鳆', '鳺', '鮒', '鵩',
        '负的', '付的', '复的', '负得', '付得', '复得', 'fu'
      ];
      
      const hasNegativeIndicator = negativeIndicators.some(indicator => 
        transcript.toLowerCase().includes(indicator.toLowerCase())
      );

      if (hasNegativeIndicator) {
        angle = -Math.abs(angle);
      }

      // 添加日志以便调试
      this.addLog(`解析角度: ${angle} (原文: ${angleText})`);

      document.getElementById('inputThetaAim').value = angle;
      const angleText2 = angle >= 0 ? `${angle}` : `负${Math.abs(angle)}`;
      this.speak(`设置瞄准角度${angleText2}度`);
      this.lastSetAngle = angle;  // 记录设置的角度
      this.checkAndCalculate();  // 检查是否可以计算
      return;
    }

    // 处理计算命令
    if (transcript.includes('计算') || transcript.includes('计算角度')) {
      document.getElementById('calcBtn').click();
      return;
    }
  }

  speak(text) {
    // 将新的语音文本添加到队列
    this.speechQueue.push(text);
    
    // 如果当前没有在播放，开始处理队列
    if (!this.isSpeaking) {
      this.processSpeechQueue();
    }
  }

  processSpeechQueue() {
    if (this.speechQueue.length === 0 || this.isSpeaking) {
      return;
    }

    const text = this.speechQueue[0];
    this.isSpeaking = true;
    speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'zh-CN';
    utterance.rate = 2.0;
    utterance.pitch = 1.0;
    
    utterance.onend = () => {
      this.isSpeaking = false;
      this.addLog(`播报完成: ${text}`);
      // 移除已播放的文本
      this.speechQueue.shift();
      
      // 如果队列中还有文本，继续播放
      if (this.speechQueue.length > 0) {
        setTimeout(() => {
          this.processSpeechQueue();
        }, 300); // 添加短暂延迟，确保语音之间有间隔
      } else if (this.isListening) {
        setTimeout(() => {
          this.recognition.start();
        }, 500);
      }
    };
    
    utterance.onerror = () => {
      this.isSpeaking = false;
      this.addLog('播报出错', 'error');
      // 出错时也要移除当前文本并继续处理队列
      this.speechQueue.shift();
      if (this.speechQueue.length > 0) {
        setTimeout(() => {
          this.processSpeechQueue();
        }, 300);
      }
    };
    
    speechSynthesis.speak(utterance);
  }

  startListening() {
    if (!this.isListening) {
      this.isListening = true;
      try {
        this.createLogBox(); // 确保日志框存在
        if (this.lastWindowFocus) {
          this.recognition.start();
        }
        this.speak('语音控制已开启');
        this.addLog('语音控制已开启');
        
        // 显示通知
        if ('Notification' in window) {
          Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
              new Notification('语音控制已开启', {
                body: '使用 Alt+C 可以关闭语音控制',
                icon: '/favicon.ico'
              });
            }
          });
        }
      } catch (error) {
        this.addLog(`启动失败: ${error.message}`, 'error');
        this.isListening = false;
      }
    }
  }

  stopListening() {
    if (this.isListening) {
      this.isListening = false;
      this.recognition.stop();
      this.speak('语音控制已关闭');
      this.addLog('语音控制已关闭');
      
      // 显示通知
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('语音控制已关闭', {
          body: '使用 Alt+V 可以重新开启语音控制',
          icon: '/favicon.ico'
        });
      }
    }
  }

  // 添加检查和计算方法
  checkAndCalculate() {
    if (this.lastSetDistance !== null && this.lastSetAngle !== null) {
      // 自动选择琉雀追踪器飞镖
      document.getElementById('btnTrackerDart').click();

      // 点击计算按钮
      document.getElementById('calcBtn').click();

      // 等待计算完成
      setTimeout(() => {
        const results = document.getElementById('results');
        if (results) {
          const resultText = results.textContent || results.innerText;
          this.addLog(`原始结果文本: ${resultText}`);
          
          const lowAngleMatch = resultText.match(/低射角度:?\s*(\d+\.?\d*)/);
          const highAngleMatch = resultText.match(/高射角度:?\s*(\d+\.?\d*)/);
          
          let announcement = '计算完成，';
          if (lowAngleMatch) {
            const lowAngle = Math.round(parseFloat(lowAngleMatch[1]) * 100) / 100;
            announcement += `低射角度${lowAngle}度`;
          }
          if (highAngleMatch) {
            const highAngle = Math.round(parseFloat(highAngleMatch[1]) * 100) / 100;
            announcement += `${lowAngleMatch ? '，' : ''}高射角度${highAngle}度`;
          }
          if (!lowAngleMatch && !highAngleMatch) {
            announcement = '计算完成，但未找到有效结果，请检查参数';
          }
          
          this.addLog(`匹配结果: 低射=${lowAngleMatch?.[1] || '无'}, 高射=${highAngleMatch?.[1] || '无'}`);
          this.addLog(`计算结果: ${announcement}`);
          
          this.speak(announcement);
        }
      }, 1000);
    }
  }
}

// 创建全局实例
const speechHandler = new SpeechHandler();

// 添加语音控制按钮和全局快捷键
document.addEventListener('DOMContentLoaded', () => {
  const controlsDiv = document.createElement('div');
  controlsDiv.className = 'flex gap-2 mt-4';
  controlsDiv.innerHTML = `
    <button id="startVoice" class="bg-green-500 hover:bg-green-600 text-white font-semibold px-4 py-2 rounded">
      开启语音控制 (Alt+V)
    </button>
    <button id="stopVoice" class="bg-red-500 hover:bg-red-600 text-white font-semibold px-4 py-2 rounded">
      关闭语音控制 (Alt+C)
    </button>
  `;

  document.querySelector('.bg-white').appendChild(controlsDiv);

  // 添加语音指令提示
  const commandTips = document.createElement('div');
  commandTips.style.cssText = `
    position: fixed;
    left: 20px;
    top: 20px;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 15px;
    border-radius: 5px;
    font-size: 14px;
    z-index: 9999;
    max-width: 300px;
  `;
  commandTips.innerHTML = `
    <div style="margin-bottom: 10px;"><strong>语音指令说明：</strong></div>
    <div style="margin-bottom: 8px;">1. 设置距离：</div>
    <div style="margin-left: 15px; margin-bottom: 5px; color: #a0e4b0;">
      - "距离150米"
      - "设置距离200米"
      - "三百五十米"
    </div>
    <div style="margin-bottom: 8px;">2. 设置角度：</div>
    <div style="margin-left: 15px; margin-bottom: 5px; color: #a0e4b0;">
      - "角度30度"
      - "设置角度45度"
      - "负20度"
      - "付35度"（负角度）
    </div>
    <div style="margin-bottom: 8px;">3. 支持小数：</div>
    <div style="margin-left: 15px; margin-bottom: 5px; color: #a0e4b0;">
      - "三点五米"
      - "二十五点八度"
    </div>
  `;
  document.body.appendChild(commandTips);

  // 添加按钮点击事件
  document.getElementById('startVoice').addEventListener('click', () => {
    speechHandler.startListening();
  });

  document.getElementById('stopVoice').addEventListener('click', () => {
    speechHandler.stopListening();
  });

  // 添加全局快捷键支持
  window.addEventListener('keydown', (event) => {
    // Alt + V 开启语音控制
    if (event.altKey && event.key.toLowerCase() === 'v') {
      event.preventDefault(); // 阻止默认行为
      speechHandler.startListening();
    }
    // Alt + C 关闭语音控制
    if (event.altKey && event.key.toLowerCase() === 'c') {
      event.preventDefault(); // 阻止默认行为
      speechHandler.stopListening();
    }
  });

  // 添加快捷键提示
  const helpText = document.createElement('div');
  helpText.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 10px;
    border-radius: 5px;
    font-size: 14px;
    z-index: 9999;
  `;
  helpText.innerHTML = `
    <div style="margin-bottom: 5px;"><strong>快捷键说明：</strong></div>
    <div>开启语音控制：Alt + V</div>
    <div>关闭语音控制：Alt + C</div>
  `;
  document.body.appendChild(helpText);
}); 