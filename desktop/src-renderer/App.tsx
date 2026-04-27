import React, { useState, useEffect, useCallback } from 'react';

// 配置
const API_BASE = 'http://localhost:8001';

// 默认占位图片 (内联 SVG) - Apple 风格
const DEFAULT_AVATAR_SVG = 'data:image/svg+xml;base64,' + btoa(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <rect fill="#F5F5F7" width="200" height="200" rx="40"/>
  <circle fill="#007AFF" cx="100" cy="80" r="40"/>
  <ellipse fill="#007AFF" cx="100" cy="165" rx="50" ry="35"/>
</svg>
`);

// Types
declare global {
  interface Window {
    electronAPI: {
      getUserData: () => Promise<any>;
      saveUserData: (data: any) => Promise<boolean>;
      getAppVersion: () => Promise<string>;
      getStoragePath: () => Promise<string>;
      windowMinimize: () => Promise<void>;
      windowMaximize: () => Promise<void>;
      windowClose: () => Promise<void>;
      windowIsMaximized: () => Promise<boolean>;
    };
  }
}

type Page = 'editor' | 'projects' | 'settings';
type AvatarType = 'ai' | 'photo' | 'template' | null;

// Voice options - 将从后端动态加载
const DEFAULT_VOICES = [
  { id: 'female-tianmei', name: '甜美女声', gender: 'female' },
  { id: 'female-shaonv', name: '少女声', gender: 'female' },
  { id: 'female-yujie', name: '御姐女声', gender: 'female' },
  { id: 'male-tianmei', name: '甜美男声', gender: 'male' },
  { id: 'male-shaonv', name: '少年男声', gender: 'male' },
  { id: 'male-chengshu', name: '成熟男声', gender: 'male' },
];

// Scene options - 将从后端动态加载
const DEFAULT_SCENES = [
  { id: 'office', name: '现代办公室', icon: '🏢' },
  { id: 'studio', name: '专业演播室', icon: '🎬' },
  { id: 'classroom', name: '智慧教室', icon: '📚' },
  { id: 'outdoor', name: '户外自然', icon: '🌳' },
];

// AvatarCard 组件 - 处理图片加载和显示
function AvatarCard({ avatar, onSelect }: { avatar: any; onSelect: () => void }) {
  const [imgError, setImgError] = useState(false);
  const [imgLoading, setImgLoading] = useState(true);

  const config = avatar.config || {};
  const genderIcon = config.gender === 'male' ? '👨' : '👩';
  const styleLabel = {
    professional: '💼专业',
    business: '🤝商务',
    friendly: '😊亲和',
    casual: '👕休闲'
  }[config.style] || '';

  const handleImageError = () => {
    console.log(`Image load failed for avatar ${avatar.id}: ${avatar.image_url}`);
    setImgError(true);
    setImgLoading(false);
  };

  const handleImageLoad = () => {
    setImgLoading(false);
    setImgError(false);
  };

  return (
    <div
      onClick={onSelect}
      style={{
        background: 'var(--bg-secondary)',
        borderRadius: '12px',
        padding: '12px',
        cursor: 'pointer',
        transition: 'all 0.2s',
        border: '2px solid transparent',
        position: 'relative'
      }}
      onMouseEnter={e => {
        (e.currentTarget as HTMLElement).style.borderColor = '#007AFF';
        (e.currentTarget as HTMLElement).style.transform = 'translateY(-2px)';
      }}
      onMouseLeave={e => {
        (e.currentTarget as HTMLElement).style.borderColor = 'transparent';
        (e.currentTarget as HTMLElement).style.transform = 'translateY(0)';
      }}
    >
      {/* 图片容器 */}
      <div style={{
        width: '100%',
        aspectRatio: '1',
        borderRadius: '8px',
        marginBottom: '8px',
        background: '#F5F5F7',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
        position: 'relative'
      }}>
        {/* 加载中 */}
        {imgLoading && (
          <div style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '24px'
          }}>
            ⏳
          </div>
        )}

        {/* 图片 */}
        {!imgError ? (
          <img
            src={avatar.image_url || DEFAULT_AVATAR_SVG}
            alt={avatar.name}
            onError={handleImageError}
            onLoad={handleImageLoad}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              display: imgLoading ? 'none' : 'block'
            }}
          />
        ) : (
          /* 加载失败显示占位 */
          <div style={{
            fontSize: '64px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '4px'
          }}>
            <span>{genderIcon}</span>
            <span style={{ fontSize: '12px', color: '#86868B' }}>加载失败</span>
          </div>
        )}

        {/* 类型标签 */}
        <div style={{
          position: 'absolute',
          top: '6px',
          right: '6px',
          background: avatar.type === 'ai_generated' ? 'rgba(99, 102, 241, 0.8)' : 'rgba(16, 185, 129, 0.8)',
          padding: '2px 6px',
          borderRadius: '4px',
          fontSize: '10px',
          color: '#fff'
        }}>
          {avatar.type === 'ai_generated' ? '🤖 AI' : '📷 照片'}
        </div>
      </div>

      {/* 名称 */}
      <div style={{ fontSize: '13px', textAlign: 'center', color: '#fff', marginBottom: '4px' }}>
        {avatar.name || `数字人 #${avatar.id}`}
      </div>

      {/* 特征标签 */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        gap: '4px',
        flexWrap: 'wrap'
      }}>
        <span style={{
          fontSize: '10px',
          padding: '2px 6px',
          background: 'rgba(99, 102, 241, 0.2)',
          borderRadius: '4px',
          color: 'rgba(0, 122, 255, 0.15)'
        }}>
          {genderIcon} {config.age === 'young' ? '年轻' : config.age === 'adult' ? '成年' : '成熟'}
        </span>
        {styleLabel && (
          <span style={{
            fontSize: '10px',
            padding: '2px 6px',
            background: 'rgba(16, 185, 129, 0.2)',
            borderRadius: '4px',
            color: 'rgba(52, 199, 89, 0.2)'
          }}>
            {styleLabel}
          </span>
        )}
      </div>
    </div>
  );
}

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('editor');
  const [version, setVersion] = useState('0.0.0');
  const [credits, setCredits] = useState(100);
  const [apiStatus, setApiStatus] = useState<any>(null);

  useEffect(() => {
    window.electronAPI?.getAppVersion().then(setVersion);
    window.electronAPI?.getUserData().then(data => {
      if (data?.credits) setCredits(data.credits);
    });
    // 获取 API 状态
    fetch(`${API_BASE}/api/status`).then(r => r.json()).then(data => {
      setApiStatus(data);
      if (data.minimax_api?.tts?.available) {
        setCredits(100);
      }
    }).catch(console.error);
  }, []);

  const handleMinimize = () => window.electronAPI?.windowMinimize();
  const handleMaximize = () => window.electronAPI?.windowMaximize();
  const handleClose = () => window.electronAPI?.windowClose();

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-logo">
          <div className="header-logo-icon">🎬</div>
          <span className="header-title">数字人播报</span>
        </div>
        <div className="header-actions">
          <div className="credits-badge">
            <span className="credits-icon">⚡</span>
            <span className="credits-value">{credits}</span>
          </div>
          {apiStatus?.minimax_api?.tts?.available && (
            <span style={{ fontSize: '12px', color: '#34C759' }}>● API 已连接</span>
          )}
          <div className="window-controls">
            <button className="window-btn" onClick={handleMinimize} title="最小化">─</button>
            <button className="window-btn" onClick={handleMaximize} title="最大化">□</button>
            <button className="window-btn close" onClick={handleClose} title="关闭">✕</button>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="nav">
        <button className={`nav-btn ${currentPage === 'editor' ? 'active' : ''}`} onClick={() => setCurrentPage('editor')}>
          <span className="nav-icon">✨</span>
          创建视频
        </button>
        <button className={`nav-btn ${currentPage === 'projects' ? 'active' : ''}`} onClick={() => setCurrentPage('projects')}>
          <span className="nav-icon">📁</span>
          我的项目
        </button>
        <button className={`nav-btn ${currentPage === 'settings' ? 'active' : ''}`} onClick={() => setCurrentPage('settings')}>
          <span className="nav-icon">⚙️</span>
          设置
        </button>
      </nav>

      {/* Main Content */}
      <main className="main">
        {currentPage === 'editor' && <EditorPage onCreditsChange={setCredits} />}
        {currentPage === 'projects' && <ProjectsPage />}
        {currentPage === 'settings' && <SettingsPage />}
      </main>

      {/* Footer */}
      <footer className="footer">
        <span className="footer-version">v{version}</span>
        <div className="footer-links">
          <span className="footer-link">帮助</span>
          <span className="footer-link">关于</span>
        </div>
      </footer>
    </div>
  );
}

function EditorPage({ onCreditsChange }: { onCreditsChange?: (c: number) => void }) {
  // 默认播报文稿
  const DEFAULT_SCRIPT = `欢迎收看我为您准备的数字人播报内容。

今天，我们将为您介绍数字人技术的最新发展趋势。数字人是人工智能领域的重要创新，它可以广泛应用于教育培训、新闻播报、企业宣传、电商直播等多个场景。

传统的视频制作需要专业的拍摄设备、场地和后期制作团队，耗时耗力。而使用数字人技术，您只需输入文稿，即可自动生成逼真的数字人播报视频，大大降低了视频制作的成本和时间。

我们的平台支持多种音色选择，可以根据不同场景和受众群体，定制专属的数字人形象和声音。感谢您的观看！`;

  const [script, setScript] = useState(DEFAULT_SCRIPT);
  const [avatarType, setAvatarType] = useState<AvatarType>(null);
  const [avatarUrl, setAvatarUrl] = useState('');
  const [selectedVoice, setSelectedVoice] = useState('female-tianmei');
  const [selectedScene, setSelectedScene] = useState<number>(1);
  const [selectedLanguage, setSelectedLanguage] = useState('zh-CN');
  const [isGenerating, setIsGenerating] = useState(false);
  const [userId] = useState(1);
  const [avatarId, setAvatarId] = useState<number | null>(null);
  const [avatars, setAvatars] = useState<any[]>([]);
  const [voices, setVoices] = useState<any[]>(DEFAULT_VOICES);
  const [scenes, setScenes] = useState<any[]>(DEFAULT_SCENES);
  const [languages, setLanguages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [showSceneModal, setShowSceneModal] = useState(false);
  const [showVoiceModal, setShowVoiceModal] = useState(false);
  const [showAIGenerateModal, setShowAIGenerateModal] = useState(false);

  // 预览状态
  const [previewHtml, setPreviewHtml] = useState<string>('');
  const [previewImageUrl, setPreviewImageUrl] = useState<string>('');
  const [sceneBackground, setSceneBackground] = useState<string>('');
  const [sceneIcon, setSceneIcon] = useState<string>('🏢');
  const [isGeneratingPreview, setIsGeneratingPreview] = useState(false);

  // AI 生成参数
  const [aiGender, setAiGender] = useState('female');
  const [aiAge, setAiAge] = useState('young');
  const [aiStyle, setAiStyle] = useState('professional');
  const [customPrompt, setCustomPrompt] = useState('');
  const [optimizedPrompt, setOptimizedPrompt] = useState('');
  const [promptError, setPromptError] = useState('');
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // 实时优化提示词
  useEffect(() => {
    if (!customPrompt.trim()) {
      setOptimizedPrompt('');
      setPromptError('');
      return;
    }

    const timer = setTimeout(async () => {
      setIsOptimizing(true);
      try {
        const response = await fetch(`${API_BASE}/api/avatars/validate-prompt`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt: customPrompt,
            gender: aiGender,
            age: aiAge,
            style: aiStyle
          })
        });
        const data = await response.json();
        if (data.valid) {
          setOptimizedPrompt(data.optimized_prompt);
          setPromptError('');
        } else {
          setOptimizedPrompt('');
          setPromptError(data.error || '提示词包含不合适的内容');
        }
      } catch (e) {
        console.error('Prompt optimization failed:', e);
      }
      setIsOptimizing(false);
    }, 500);

    return () => clearTimeout(timer);
  }, [customPrompt, aiGender, aiAge, aiStyle]);

  // 加载预览（仅显示当前组合，不生成）
  const loadPreview = useCallback(async () => {
    if (!avatarId || !selectedScene) return;

    try {
      const response = await fetch(
        `${API_BASE}/api/preview?avatar_id=${avatarId}&scene_id=${selectedScene}`
      );
      if (response.ok) {
        const data = await response.json();
        setPreviewHtml(data.preview_html || '');
        setPreviewImageUrl('');
        setSceneBackground(data.scene_background || '');
        setSceneIcon(data.scene_icon || '🏢');
      }
    } catch (e) {
      console.error('Failed to load preview:', e);
    }
  }, [avatarId, selectedScene]);

  // 手动生成预览
  const generatePreview = async () => {
    if (!avatarId || !selectedScene) {
      setMessage('⚠️ 请先选择数字人和背景场景');
      return;
    }

    setIsGeneratingPreview(true);
    setMessage('⏳ 正在生成播报预览图...');

    try {
      const response = await fetch(
        `${API_BASE}/api/preview/generate?avatar_id=${avatarId}&scene_id=${selectedScene}`,
        { method: 'POST' }
      );

      if (response.ok) {
        const data = await response.json();
        if (data.preview_image_url) {
          setPreviewImageUrl(data.preview_image_url);
          setMessage('✅ 播报预览图生成成功！');
        }
      } else {
        const error = await response.json();
        setMessage('❌ ' + (error.detail || '生成失败'));
      }
    } catch (e) {
      setMessage('❌ 生成失败: ' + e);
    }
    setIsGeneratingPreview(false);
  };

  // 当数字人或场景变化时加载预览
  useEffect(() => {
    if (avatarId && selectedScene) {
      loadPreview();
    }
  }, [avatarId, selectedScene, loadPreview]);

  // 加载数据
  useEffect(() => {
    // 加载声音列表
    fetch(`${API_BASE}/api/voices`)
      .then(r => r.json())
      .then(data => {
        if (data.voices && Array.isArray(data.voices)) {
          setVoices(data.voices);
        }
      })
      .catch(console.error);

    // 加载场景列表
    fetch(`${API_BASE}/api/scenes`)
      .then(r => r.json())
      .then(data => {
        if (Array.isArray(data)) {
          const formattedScenes = data.map((s: any) => ({
            id: s.id,
            name: s.name,
            icon: s.category === 'business' ? '🏢' : s.category === 'media' ? '🎬' : s.category === 'education' ? '📚' : '🌳'
          }));
          setScenes(formattedScenes);
        }
      })
      .catch(console.error);

    // 加载语言列表
    fetch(`${API_BASE}/api/languages`)
      .then(r => r.json())
      .then(data => {
        if (data.languages && Array.isArray(data.languages)) {
          setLanguages(data.languages);
        }
      })
      .catch(console.error);

    // 加载用户数字人列表
    fetch(`${API_BASE}/api/avatars?user_id=${userId}`)
      .then(r => r.json())
      .then(data => setAvatars(Array.isArray(data) ? data : []))
      .catch(console.error);
  }, [userId]);

  const handleAvatarSelect = async (type: AvatarType) => {
    setAvatarType(type);
    setMessage('');

    if (type === 'ai') {
      setLoading(true);
      try {
        // 先验证自定义提示词
        if (customPrompt.trim()) {
          const validateRes = await fetch(`${API_BASE}/api/avatars/validate-prompt`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              prompt: customPrompt,
              gender: aiGender,
              age: aiAge,
              style: aiStyle
            })
          });
          const validateData = await validateRes.json();
          if (!validateData.valid) {
            setMessage(validateData.error || '⚠️ 提示词包含不合适的内容');
            setLoading(false);
            return;
          }
        }

        const response = await fetch(`${API_BASE}/api/avatars/generate-ai`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: userId,
            gender: aiGender,
            age: aiAge,
            style: aiStyle,
            custom_prompt: customPrompt.trim() || null
          })
        });
        const data = await response.json();
        if (data.id) {
          setAvatarId(data.id);
          setAvatarUrl(data.image_url);
          setAvatars(prev => [...prev, {
            ...data,
            name: data.name || `AI数字人 #${data.id}`
          }]);
          setMessage('✅ AI 数字人创建成功！');
        } else {
          setMessage('❌ 创建失败: ' + (data.detail || '未知错误'));
        }
      } catch (error) {
        setMessage('❌ 创建失败: ' + error);
      }
      setLoading(false);
    } else if (type === 'photo') {
      // 模拟上传照片
      const photoUrl = prompt('请输入照片 URL (或使用示例图片):', 'https://api.dicebear.com/7.x/avataaars/svg?seed=456');
      if (photoUrl) {
        setLoading(true);
        try {
          const response = await fetch(`${API_BASE}/api/avatars/from-photo`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              user_id: userId,
              photo_url: photoUrl,
              name: '照片数字人'
            })
          });
          const data = await response.json();
          if (data.id) {
            setAvatarId(data.id);
            setAvatarUrl(data.image_url);
            setMessage('✅ 照片数字人创建成功！');
          }
        } catch (error) {
          setMessage('❌ 创建失败: ' + error);
        }
        setLoading(false);
      }
    }
  };

  const handleGenerate = async () => {
    if (!script.trim()) {
      setMessage('⚠️ 请输入播报文稿');
      return;
    }
    if (!avatarId) {
      setMessage('⚠️ 请先选择数字人形象');
      return;
    }

    setIsGenerating(true);
    setMessage('⏳ 正在生成视频...');

    try {
      // 1. 创建项目
      const createResponse = await fetch(`${API_BASE}/api/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          title: `播报视频_${new Date().toLocaleString()}`,
          script_text: script,
          avatar_id: avatarId,
          scene_id: String(selectedScene),
          voice_config: { voice_id: selectedVoice, speed: 1.0 }
        })
      });
      const project = await createResponse.json();

      if (project.id) {
        // 2. 生成视频
        setMessage('⏳ 正在合成语音并生成视频...');
        const generateResponse = await fetch(`${API_BASE}/api/projects/${project.id}/generate`, {
          method: 'POST'
        });
        const result = await generateResponse.json();

        if (result.status === 'completed') {
          setMessage('✅ 视频生成成功！请到"我的项目"查看');
          if (onCreditsChange && result.credits_used) {
            onCreditsChange(prev => Math.max(0, prev - result.credits_used));
          }
          // 刷新项目列表
          window.location.hash = '#projects';
          window.location.reload();
        } else {
          setMessage('❌ 生成失败: ' + (result.note || '未知错误'));
        }
      }
    } catch (error) {
      setMessage('❌ 生成失败: ' + error);
    }

    setIsGenerating(false);
  };

  // 语音预览状态
  const [voicePreview, setVoicePreview] = useState<{url: string; name: string} | null>(null);

  const handleTestVoice = async () => {
    setMessage('🔊 正在生成语音...');
    setVoicePreview(null);
    try {
      const response = await fetch(`${API_BASE}/api/voices/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: script || '您好，欢迎使用数字人播报系统！',
          voice_id: selectedVoice,
          speed: 1.0
        })
      });
      const data = await response.json();
      if (data.audio_url) {
        setVoicePreview({ url: data.audio_url, name: selectedVoice });
        setMessage('✅ 语音已生成，点击播放按钮试听');
      } else {
        setMessage('❌ 语音生成失败: ' + (data.error || '未知错误'));
      }
    } catch (error) {
      setMessage('❌ 语音测试失败: ' + error);
    }
  };

  return (
    <div className="editor">
      {/* Left Panel - Settings */}
      <div className="editor-left">
        {/* Message */}
        {message && (
          <div style={{
            padding: '12px 16px',
            background: message.includes('✅') ? 'rgba(16, 185, 129, 0.2)' :
                       message.includes('❌') ? 'rgba(239, 68, 68, 0.2)' :
                       'rgba(99, 102, 241, 0.2)',
            borderRadius: '10px',
            color: '#fff',
            fontSize: '14px',
            marginBottom: '16px'
          }}>
            {message}
          </div>
        )}

        {/* Script Input */}
        <div className="card">
          <div className="card-header">
            <div className="card-icon">📝</div>
            <span className="card-title">播报文稿</span>
          </div>
          <div className="form-group">
            <textarea
              className="form-textarea"
              value={script}
              onChange={(e) => setScript(e.target.value)}
              placeholder="输入您想要播报的内容，AI 将自动生成视频..."
              rows={5}
            />
          </div>
        </div>

        {/* Avatar Selection */}
        <div className="card">
          <div className="card-header">
            <div className="card-icon">👤</div>
            <span className="card-title">数字人形象</span>
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              style={{
                marginLeft: 'auto',
                background: 'transparent',
                border: 'none',
                color: '#AF52DE',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              {showAdvanced ? '收起高级选项 ▲' : '高级选项 ▼'}
            </button>
          </div>

          {/* 高级选项 */}
          {showAdvanced && (
            <div style={{
              background: 'var(--bg-secondary)',
              borderRadius: '10px',
              padding: '12px',
              marginBottom: '12px'
            }}>
              {/* 性别 */}
              <div style={{ marginBottom: '10px' }}>
                <label style={{ fontSize: '12px', color: '#86868B', display: 'block', marginBottom: '4px' }}>性别</label>
                <div style={{ display: 'flex', gap: '8px' }}>
                  {[
                    { value: 'female', label: '👩 女性' },
                    { value: 'male', label: '👨 男性' }
                  ].map(opt => (
                    <button
                      key={opt.value}
                      onClick={() => setAiGender(opt.value)}
                      style={{
                        flex: 1,
                        padding: '6px 8px',
                        background: aiGender === opt.value ? 'rgba(99, 102, 241, 0.3)' : 'transparent',
                        border: `1px solid ${aiGender === opt.value ? '#007AFF' : 'rgba(0, 0, 0, 0.1)'}`,
                        borderRadius: '6px',
                        color: aiGender === opt.value ? '#fff' : '#86868B',
                        cursor: 'pointer',
                        fontSize: '13px'
                      }}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* 年龄 */}
              <div style={{ marginBottom: '10px' }}>
                <label style={{ fontSize: '12px', color: '#86868B', display: 'block', marginBottom: '4px' }}>年龄</label>
                <div style={{ display: 'flex', gap: '8px' }}>
                  {[
                    { value: 'young', label: '🌱 年轻' },
                    { value: 'adult', label: '👤 成年' },
                    { value: 'middle', label: '👴 成熟' }
                  ].map(opt => (
                    <button
                      key={opt.value}
                      onClick={() => setAiAge(opt.value)}
                      style={{
                        flex: 1,
                        padding: '6px 8px',
                        background: aiAge === opt.value ? 'rgba(99, 102, 241, 0.3)' : 'transparent',
                        border: `1px solid ${aiAge === opt.value ? '#007AFF' : 'rgba(0, 0, 0, 0.1)'}`,
                        borderRadius: '6px',
                        color: aiAge === opt.value ? '#fff' : '#86868B',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* 风格 */}
              <div style={{ marginBottom: '10px' }}>
                <label style={{ fontSize: '12px', color: '#86868B', display: 'block', marginBottom: '4px' }}>风格</label>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {[
                    { value: 'professional', label: '💼 专业' },
                    { value: 'business', label: '🤝 商务' },
                    { value: 'friendly', label: '😊 亲和' },
                    { value: 'casual', label: '👕 休闲' }
                  ].map(opt => (
                    <button
                      key={opt.value}
                      onClick={() => setAiStyle(opt.value)}
                      style={{
                        padding: '6px 10px',
                        background: aiStyle === opt.value ? 'rgba(99, 102, 241, 0.3)' : 'transparent',
                        border: `1px solid ${aiStyle === opt.value ? '#007AFF' : 'rgba(0, 0, 0, 0.1)'}`,
                        borderRadius: '6px',
                        color: aiStyle === opt.value ? '#fff' : '#86868B',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* 自定义提示词 */}
              <div>
                <label style={{ fontSize: '12px', color: '#86868B', display: 'block', marginBottom: '4px' }}>
                  自定义描述（可选）
                </label>
                <input
                  type="text"
                  value={customPrompt}
                  onChange={(e) => setCustomPrompt(e.target.value)}
                  placeholder="例如：长发、戴眼镜、穿西装..."
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    background: 'var(--bg-primary)',
                    border: '1px solid rgba(0, 0, 0, 0.1)',
                    borderRadius: '6px',
                    color: '#fff',
                    fontSize: '13px',
                    outline: 'none'
                  }}
                />
                <div style={{ fontSize: '11px', color: '#86868B', marginTop: '4px' }}>
                  描述外貌特征，系统将自动优化提示词生成多样化数字人
                </div>
              </div>
            </div>
          )}

          <div className="avatar-options">
            <div className={`avatar-option ${avatarType === 'ai' ? 'active' : ''}`} onClick={() => {
              setShowAIGenerateModal(true);
            }}>
              <div className="avatar-option-icon">🤖</div>
              <span className="avatar-option-label">AI 生成</span>
            </div>
            <div className={`avatar-option ${avatarType === 'photo' ? 'active' : ''}`} onClick={() => handleAvatarSelect('photo')}>
              <div className="avatar-option-icon">📷</div>
              <span className="avatar-option-label">上传照片</span>
            </div>
            <div className={`avatar-option ${avatarType === 'template' ? 'active' : ''}`} onClick={() => {
              setShowTemplateModal(true);
            }}>
              <div className="avatar-option-icon">🖼️</div>
              <span className="avatar-option-label">选择模板</span>
            </div>
          </div>
          {avatars.length > 0 && (
            <div style={{ marginTop: '12px', fontSize: '12px', color: '#86868B' }}>
              已创建 {avatars.length} 个数字人
            </div>
          )}
        </div>

        {/* Voice Selection */}
        <div className="card">
          <div className="card-header">
            <div className="card-icon">🎙️</div>
            <span className="card-title">
              声音选择 ({voices.filter(v => v.available !== false).length}种可用)
            </span>
            <button
              onClick={() => setShowVoiceModal(true)}
              style={{
                marginLeft: 'auto',
                background: 'transparent',
                border: 'none',
                color: '#AF52DE',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >查看全部 →</button>
          </div>
          <div className="voice-grid">
            {voices.filter(v => v.available !== false).slice(0, 4).map(voice => (
              <div
                key={voice.id}
                className={`voice-option ${selectedVoice === voice.id ? 'active' : ''}`}
                onClick={() => setSelectedVoice(voice.id)}
              >
                <div className={`voice-avatar ${voice.gender || 'female'}`}>
                  {voice.gender === 'female' ? '👩' : '👨'}
                </div>
                <div className="voice-info">
                  <div className="voice-name">{voice.name}</div>
                  <div className="voice-gender">{voice.gender === 'male' ? '男声' : '女声'}</div>
                </div>
              </div>
            ))}
          </div>

          {/* 语音预览播放器 */}
          {voicePreview && (
            <div style={{
              marginTop: '12px',
              padding: '12px',
              background: 'var(--bg-secondary)',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px'
            }}>
              <audio
                src={voicePreview.url}
                controls
                style={{ flex: 1, height: '36px' }}
              />
              <button
                onClick={() => {
                  const a = document.createElement('a');
                  a.href = voicePreview.url;
                  a.download = `voice_${voicePreview.name}.mp3`;
                  a.click();
                }}
                style={{
                  padding: '6px 12px',
                  background: 'rgba(16, 185, 129, 0.2)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  borderRadius: '6px',
                  color: '#34C759',
                  cursor: 'pointer',
                  fontSize: '12px'
                }}
              >
                📥 下载
              </button>
            </div>
          )}

          <button
            onClick={handleTestVoice}
            disabled={loading}
            style={{
              marginTop: '12px',
              padding: '10px 16px',
              background: loading ? 'rgba(99, 102, 241, 0.3)' : 'rgba(99, 102, 241, 0.2)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              borderRadius: '8px',
              color: '#AF52DE',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '13px',
              fontWeight: '500'
            }}
          >
            {loading ? '⏳ 生成中...' : '🔊 测试语音'}
          </button>
        </div>

        {/* Language Selection */}
        <div className="card">
          <div className="card-header">
            <div className="card-icon">🌐</div>
            <span className="card-title">语言选择</span>
          </div>
          <select
            className="form-select"
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
          >
            {languages.map(lang => (
              <option key={lang.code} value={lang.code}>
                {lang.native || lang.name}
              </option>
            ))}
          </select>
        </div>

        {/* Scene Selection */}
        <div className="card">
          <div className="card-header">
            <div className="card-icon">🎬</div>
            <span className="card-title">背景场景</span>
            <button
              onClick={() => setShowSceneModal(true)}
              style={{
                marginLeft: 'auto',
                background: 'transparent',
                border: 'none',
                color: '#AF52DE',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >{sceneIcon} 选择</button>
          </div>
          <select
            className="form-select"
            value={selectedScene}
            onChange={(e) => setSelectedScene(Number(e.target.value))}
          >
            {scenes.map(scene => (
              <option key={scene.id} value={scene.id}>{scene.icon} {scene.name}</option>
            ))}
          </select>
        </div>

        {/* Generate Button */}
        <button className="btn-generate" onClick={handleGenerate} disabled={isGenerating || !avatarId}>
          {isGenerating ? (
            <>
              <span className="loading">⏳</span>
              正在生成...
            </>
          ) : (
            <>
              <span>🚀</span>
              开始生成视频
            </>
          )}
        </button>
      </div>

      {/* Right Panel - Preview */}
      <div className="editor-right">
        <div className="preview-card">
          <div className="preview-header">
            <span className="preview-title">视频预览</span>
            {isGeneratingPreview ? (
              <span className="preview-badge" style={{ background: 'rgba(245, 158, 11, 0.2)', color: '#FF9500' }}>
                ⏳ 生成中...
              </span>
            ) : previewImageUrl ? (
              <span className="preview-badge" style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#34C759' }}>
                ✅ 预览就绪
              </span>
            ) : avatarUrl && selectedScene ? (
              <span className="preview-badge" style={{ background: 'rgba(99, 102, 241, 0.2)', color: '#AF52DE' }}>
                {sceneIcon} 待生成
              </span>
            ) : null}
          </div>
          <div className="preview-content">
            {isGeneratingPreview ? (
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                minHeight: '180px',
                background: sceneBackground || '#1a1a2e',
                borderRadius: '12px'
              }}>
                <div style={{ fontSize: '40px', marginBottom: '12px', animation: 'pulse 1.5s infinite' }}>🎬</div>
                <div style={{ color: '#fff', fontSize: '14px' }}>AI 正在生成播报预览...</div>
              </div>
            ) : previewImageUrl ? (
              <div
                style={{ width: '100%', height: '100%', position: 'relative' }}
              >
                <img
                  src={previewImageUrl}
                  alt="播报预览"
                  style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '12px' }}
                />
              </div>
            ) : previewHtml ? (
              <div
                dangerouslySetInnerHTML={{ __html: previewHtml }}
                style={{ width: '100%', height: '100%', minHeight: '180px' }}
              />
            ) : avatarUrl ? (
              <div style={{ textAlign: 'center' }}>
                <img
                  src={avatarUrl}
                  alt="数字人"
                  style={{
                    width: '100%',
                    maxHeight: '180px',
                    objectFit: 'contain',
                    borderRadius: '12px',
                    background: sceneBackground || '#1a1a2e'
                  }}
                />
                <div style={{ marginTop: '12px', fontSize: '13px', color: '#86868B' }}>
                  {sceneIcon} 选择背景场景，点击下方按钮生成预览
                </div>
              </div>
            ) : (
              <div className="preview-placeholder">
                <div className="preview-placeholder-icon">🎬</div>
                <div className="preview-placeholder-text">选择数字人形象后预览</div>
                <div className="preview-placeholder-hint">支持 AI 生成、上传照片或选择模板</div>
              </div>
            )}
          </div>

          {/* 生成预览按钮 */}
          {avatarUrl && selectedScene && !isGeneratingPreview && (
            <button
              onClick={generatePreview}
              style={{
                width: '100%',
                marginTop: '12px',
                padding: '10px 16px',
                background: previewImageUrl
                  ? 'rgba(16, 185, 129, 0.2)'
                  : 'linear-gradient(135deg, #007AFF 0%, #AF52DE 100%)',
                border: previewImageUrl ? '1px solid rgba(16, 185, 129, 0.3)' : 'none',
                borderRadius: '10px',
                color: previewImageUrl ? '#34C759' : '#fff',
                fontSize: '13px',
                fontWeight: '500',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              {previewImageUrl ? '🔄 重新生成预览' : '🎬 生成播报预览'}
            </button>
          )}
        </div>
      </div>

      {/* 声音选择弹窗 */}
      {showVoiceModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }} onClick={() => setShowVoiceModal(false)}>
          <div style={{
            background: 'var(--bg-card)',
            borderRadius: '16px',
            padding: '24px',
            maxWidth: '700px',
            width: '90%',
            maxHeight: '80vh',
            overflow: 'auto'
          }} onClick={e => e.stopPropagation()}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '20px'
            }}>
              <h2 style={{ margin: 0, fontSize: '18px' }}>🎙️ 选择声音</h2>
              <button
                onClick={() => setShowVoiceModal(false)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#fff',
                  fontSize: '24px',
                  cursor: 'pointer'
                }}
              >✕</button>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <div style={{ fontSize: '13px', color: '#86868B', marginBottom: '8px' }}>女声</div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '12px' }}>
                {voices.filter(v => v.gender === 'female' || !v.gender).map(voice => (
                  <div
                    key={voice.id}
                    onClick={() => {
                      setSelectedVoice(voice.id);
                      setShowVoiceModal(false);
                      setMessage(`✅ 已选择: ${voice.name}`);
                    }}
                    style={{
                      background: selectedVoice === voice.id ? 'rgba(99, 102, 241, 0.3)' : 'var(--bg-secondary)',
                      borderRadius: '12px',
                      padding: '16px',
                      cursor: 'pointer',
                      border: `2px solid ${selectedVoice === voice.id ? '#007AFF' : 'transparent'}`,
                      transition: 'all 0.2s'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div style={{ fontSize: '32px' }}>👩</div>
                      <div>
                        <div style={{ fontSize: '14px', color: '#fff', fontWeight: '500' }}>{voice.name}</div>
                        <div style={{ fontSize: '12px', color: '#86868B' }}>{voice.id}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '13px', color: '#86868B', marginBottom: '8px' }}>男声</div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '12px' }}>
                {voices.filter(v => v.gender === 'male').map(voice => (
                  <div
                    key={voice.id}
                    onClick={() => {
                      setSelectedVoice(voice.id);
                      setShowVoiceModal(false);
                      setMessage(`✅ 已选择: ${voice.name}`);
                    }}
                    style={{
                      background: selectedVoice === voice.id ? 'rgba(99, 102, 241, 0.3)' : 'var(--bg-secondary)',
                      borderRadius: '12px',
                      padding: '16px',
                      cursor: 'pointer',
                      border: `2px solid ${selectedVoice === voice.id ? '#007AFF' : 'transparent'}`,
                      transition: 'all 0.2s'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div style={{ fontSize: '32px' }}>👨</div>
                      <div>
                        <div style={{ fontSize: '14px', color: '#fff', fontWeight: '500' }}>{voice.name}</div>
                        <div style={{ fontSize: '12px', color: '#86868B' }}>{voice.id}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI 生成数字人弹窗 */}
      {showAIGenerateModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.85)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1001
        }} onClick={() => setShowAIGenerateModal(false)}>
          <div style={{
            background: 'var(--bg-card)',
            borderRadius: '20px',
            padding: '28px',
            maxWidth: '550px',
            width: '90%',
            maxHeight: '85vh',
            overflow: 'auto'
          }} onClick={e => e.stopPropagation()}>
            {/* 标题 */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '24px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '24px' }}>🤖</span>
                <h2 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>AI 生成数字人</h2>
              </div>
              <button
                onClick={() => setShowAIGenerateModal(false)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#86868B',
                  fontSize: '20px',
                  cursor: 'pointer',
                  padding: '4px'
                }}
              >✕</button>
            </div>

            {/* 性别选择 */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{ fontSize: '13px', color: '#86868B', display: 'block', marginBottom: '8px', fontWeight: '500' }}>
                👤 性别
              </label>
              <div style={{ display: 'flex', gap: '10px' }}>
                {[
                  { value: 'female', label: '👩 女性', color: '#ec4899' },
                  { value: 'male', label: '👨 男性', color: '#3b82f6' }
                ].map(opt => (
                  <button
                    key={opt.value}
                    onClick={() => setAiGender(opt.value)}
                    style={{
                      flex: 1,
                      padding: '12px 16px',
                      background: aiGender === opt.value ? `${opt.color}22` : 'var(--bg-secondary)',
                      border: `2px solid ${aiGender === opt.value ? opt.color : 'transparent'}`,
                      borderRadius: '10px',
                      color: aiGender === opt.value ? '#fff' : '#86868B',
                      cursor: 'pointer',
                      fontSize: '14px',
                      fontWeight: aiGender === opt.value ? '600' : '400',
                      transition: 'all 0.2s'
                    }}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {/* 年龄选择 */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{ fontSize: '13px', color: '#86868B', display: 'block', marginBottom: '8px', fontWeight: '500' }}>
                🎂 年龄
              </label>
              <div style={{ display: 'flex', gap: '8px' }}>
                {[
                  { value: 'young', label: '🌱 年轻 (20-25岁)' },
                  { value: 'adult', label: '👤 成年 (30-35岁)' },
                  { value: 'middle', label: '👴 成熟 (45-50岁)' }
                ].map(opt => (
                  <button
                    key={opt.value}
                    onClick={() => setAiAge(opt.value)}
                    style={{
                      flex: 1,
                      padding: '10px 8px',
                      background: aiAge === opt.value ? 'rgba(99, 102, 241, 0.3)' : 'var(--bg-secondary)',
                      border: `2px solid ${aiAge === opt.value ? '#007AFF' : 'transparent'}`,
                      borderRadius: '8px',
                      color: aiAge === opt.value ? '#fff' : '#86868B',
                      cursor: 'pointer',
                      fontSize: '12px',
                      transition: 'all 0.2s'
                    }}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {/* 风格选择 */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{ fontSize: '13px', color: '#86868B', display: 'block', marginBottom: '8px', fontWeight: '500' }}>
                🎨 风格
              </label>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {[
                  { value: 'professional', label: '💼 专业', icon: '💼' },
                  { value: 'business', label: '🤝 商务', icon: '🤝' },
                  { value: 'friendly', label: '😊 亲和', icon: '😊' },
                  { value: 'casual', label: '👕 休闲', icon: '👕' }
                ].map(opt => (
                  <button
                    key={opt.value}
                    onClick={() => setAiStyle(opt.value)}
                    style={{
                      padding: '10px 14px',
                      background: aiStyle === opt.value ? 'rgba(99, 102, 241, 0.3)' : 'var(--bg-secondary)',
                      border: `2px solid ${aiStyle === opt.value ? '#007AFF' : 'transparent'}`,
                      borderRadius: '8px',
                      color: aiStyle === opt.value ? '#fff' : '#86868B',
                      cursor: 'pointer',
                      fontSize: '13px',
                      transition: 'all 0.2s'
                    }}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {/* 自定义描述 */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{ fontSize: '13px', color: '#86868B', display: 'block', marginBottom: '8px', fontWeight: '500' }}>
                ✏️ 自定义描述（可选）
              </label>
              <textarea
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder="描述你想要的数字人外貌特征...
例如：黑色长发、戴眼镜、穿商务西装、微笑"
                rows={3}
                style={{
                  width: '100%',
                  padding: '12px',
                  background: 'var(--bg-secondary)',
                  border: `1px solid ${promptError ? '#ef4444' : 'rgba(0, 0, 0, 0.1)'}`,
                  borderRadius: '10px',
                  color: '#fff',
                  fontSize: '14px',
                  resize: 'vertical',
                  outline: 'none',
                  fontFamily: 'inherit',
                  lineHeight: '1.5'
                }}
              />
              {promptError && (
                <div style={{
                  marginTop: '6px',
                  fontSize: '12px',
                  color: '#ef4444',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}>
                  ⚠️ {promptError}
                </div>
              )}
            </div>

            {/* 优化后的提示词预览 */}
            {(optimizedPrompt || isOptimizing) && (
              <div style={{
                marginBottom: '24px',
                padding: '16px',
                background: 'rgba(16, 185, 129, 0.1)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                borderRadius: '12px'
              }}>
                <div style={{
                  fontSize: '12px',
                  color: '#34C759',
                  marginBottom: '8px',
                  fontWeight: '500',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}>
                  {isOptimizing ? '⏳ 正在优化...' : '✅ 优化后的提示词'}
                </div>
                {optimizedPrompt && (
                  <div style={{
                    fontSize: '12px',
                    color: '#d1d5db',
                    lineHeight: '1.6',
                    wordBreak: 'break-word'
                  }}>
                    {optimizedPrompt}
                  </div>
                )}
              </div>
            )}

            {/* 生成按钮 */}
            <button
              onClick={async () => {
                // 先验证提示词
                if (promptError) {
                  setMessage('⚠️ ' + promptError);
                  return;
                }

                setShowAIGenerateModal(false);
                setLoading(true);
                setMessage('⏳ 正在生成 AI 数字人...');

                try {
                  const response = await fetch(`${API_BASE}/api/avatars/generate-ai`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                      user_id: userId,
                      gender: aiGender,
                      age: aiAge,
                      style: aiStyle,
                      custom_prompt: customPrompt.trim() || null
                    })
                  });
                  const data = await response.json();
                  if (data.id) {
                    setAvatarId(data.id);
                    setAvatarUrl(data.image_url);
                    setAvatarType('ai');
                    setAvatars(prev => [...prev, {
                      ...data,
                      name: data.name || `AI数字人 #${data.id}`,
                      config: { gender: aiGender, age: aiAge, style: aiStyle }
                    }]);
                    setMessage('✅ AI 数字人创建成功！');
                  } else {
                    setMessage('❌ 创建失败: ' + (data.detail || '未知错误'));
                  }
                } catch (error) {
                  setMessage('❌ 创建失败: ' + error);
                }
                setLoading(false);
              }}
              disabled={loading}
              style={{
                width: '100%',
                padding: '14px 24px',
                background: loading ? '#4b5563' : 'linear-gradient(135deg, #007AFF 0%, #AF52DE 100%)',
                border: 'none',
                borderRadius: '12px',
                color: '#fff',
                fontSize: '15px',
                fontWeight: '600',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              {loading ? (
                <>⏳ 生成中...</>
              ) : (
                <>
                  🤖 开始生成
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* 场景选择弹窗 */}
      {showSceneModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }} onClick={() => setShowSceneModal(false)}>
          <div style={{
            background: 'var(--bg-card)',
            borderRadius: '16px',
            padding: '24px',
            maxWidth: '700px',
            width: '90%',
            maxHeight: '80vh',
            overflow: 'auto'
          }} onClick={e => e.stopPropagation()}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '20px'
            }}>
              <h2 style={{ margin: 0, fontSize: '18px' }}>🎬 选择背景场景</h2>
              <button
                onClick={() => setShowSceneModal(false)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#fff',
                  fontSize: '24px',
                  cursor: 'pointer'
                }}
              >✕</button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '16px' }}>
              {scenes.map(scene => (
                <div
                  key={scene.id}
                  onClick={() => {
                    setSelectedScene(scene.id);
                    setShowSceneModal(false);
                    setMessage(`✅ 已选择场景: ${scene.name}`);
                  }}
                  style={{
                    background: selectedScene === scene.id ? 'rgba(99, 102, 241, 0.3)' : 'var(--bg-secondary)',
                    borderRadius: '12px',
                    padding: '16px',
                    cursor: 'pointer',
                    border: `2px solid ${selectedScene === scene.id ? '#007AFF' : 'transparent'}`,
                    transition: 'all 0.2s',
                    textAlign: 'center'
                  }}
                >
                  <div style={{ fontSize: '48px', marginBottom: '8px' }}>{scene.icon}</div>
                  <div style={{ fontSize: '14px', color: '#fff', fontWeight: '500' }}>{scene.name}</div>
                  <div style={{ fontSize: '12px', color: '#86868B', marginTop: '4px' }}>ID: {scene.id}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 模板选择弹窗 */}
      {showTemplateModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.85)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }} onClick={() => setShowTemplateModal(false)}>
          <div style={{
            background: 'var(--bg-card)',
            borderRadius: '20px',
            padding: '28px',
            maxWidth: '500px',
            width: '90%',
            maxHeight: '80vh',
            overflow: 'auto'
          }} onClick={e => e.stopPropagation()}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '16px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '20px' }}>🖼️</span>
                <h2 style={{ margin: 0, fontSize: '18px' }}>已创建的数字人</h2>
              </div>
              <button
                onClick={() => setShowTemplateModal(false)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#86868B',
                  fontSize: '18px',
                  cursor: 'pointer'
                }}
              >✕</button>
            </div>

            <p style={{ fontSize: '13px', color: '#86868B', marginBottom: '16px' }}>
              共 {avatars.length} 个模板，点击选择
            </p>

            {avatars.length === 0 ? (
              <div style={{
                textAlign: 'center',
                padding: '40px 20px',
                background: 'var(--bg-secondary)',
                borderRadius: '12px'
              }}>
                <div style={{ fontSize: '48px', marginBottom: '12px' }}>📭</div>
                <div style={{ color: '#86868B', marginBottom: '8px' }}>暂无模板</div>
                <div style={{ fontSize: '13px', color: '#86868B' }}>
                  点击上方「AI 生成」创建数字人
                </div>
              </div>
            ) : (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: '12px'
              }}>
                {avatars.slice(0, 8).map(avatar => (
                  <div
                    key={avatar.id}
                    onClick={() => {
                      setAvatarId(avatar.id);
                      setAvatarUrl(avatar.image_url);
                      setAvatarType('template');
                      setShowTemplateModal(false);
                      setMessage(`✅ 已选择: ${avatar.name}`);
                    }}
                    style={{
                      background: 'var(--bg-secondary)',
                      borderRadius: '12px',
                      padding: '12px',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      border: '2px solid transparent'
                    }}
                    onMouseEnter={e => {
                      (e.currentTarget as HTMLElement).style.borderColor = '#007AFF';
                    }}
                    onMouseLeave={e => {
                      (e.currentTarget as HTMLElement).style.borderColor = 'transparent';
                    }}
                  >
                    <img
                      src={avatar.image_url || DEFAULT_AVATAR_SVG}
                      alt={avatar.name}
                      style={{
                        width: '100%',
                        aspectRatio: '1',
                        objectFit: 'cover',
                        borderRadius: '8px',
                        marginBottom: '8px',
                        background: '#F5F5F7'
                      }}
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = DEFAULT_AVATAR_SVG;
                      }}
                    />
                    <div style={{ fontSize: '12px', color: '#fff', textAlign: 'center' }}>
                      {avatar.name}
                    </div>
                    <div style={{
                      fontSize: '10px',
                      color: '#86868B',
                      textAlign: 'center',
                      marginTop: '4px'
                    }}>
                      {avatar.config?.gender === 'female' ? '👩 女' : '👨 男'} · {
                        avatar.config?.age === 'young' ? '年轻' :
                        avatar.config?.age === 'adult' ? '成年' : '成熟'
                      }
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function ProjectsPage() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [exportingId, setExportingId] = useState<number | null>(null);
  const userId = 1;

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = () => {
    setLoading(true);
    fetch(`${API_BASE}/api/projects?user_id=${userId}`)
      .then(r => r.json())
      .then(data => {
        setProjects(Array.isArray(data) ? data.reverse() : []);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  };

  const handlePlayVideo = async (projectId: number) => {
    try {
      const response = await fetch(`${API_BASE}/api/projects/${projectId}`);
      const data = await response.json();
      if (data.output_url) {
        window.open(data.output_url, '_blank');
      } else {
        alert('暂无视频链接');
      }
    } catch (error) {
      alert('获取失败: ' + error);
    }
  };

  const handleExportMP4 = async (projectId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setExportingId(projectId);
    try {
      const response = await fetch(`${API_BASE}/api/export/${projectId}/mp4?quality=1080p`);
      const data = await response.json();
      if (data.download_url) {
        window.open(data.download_url, '_blank');
      } else {
        alert('导出失败: ' + (data.detail || '未知错误'));
      }
    } catch (error) {
      alert('导出失败: ' + error);
    }
    setExportingId(null);
  };

  const handleExportGIF = async (projectId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setExportingId(projectId);
    try {
      const response = await fetch(`${API_BASE}/api/export/${projectId}/gif?fps=10`);
      const data = await response.json();
      if (data.download_url) {
        window.open(data.download_url, '_blank');
      } else {
        alert('导出失败: ' + (data.detail || '未知错误'));
      }
    } catch (error) {
      alert('导出失败: ' + error);
    }
    setExportingId(null);
  };

  const handleShare = async (projectId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const response = await fetch(`${API_BASE}/api/share/${projectId}`);
      const data = await response.json();
      if (data.share_url) {
        await navigator.clipboard.writeText(data.share_url);
        alert('分享链接已复制到剪贴板！\n' + data.share_url);
      } else {
        alert('生成分享链接失败');
      }
    } catch (error) {
      alert('分享失败: ' + error);
    }
  };

  return (
    <div className="projects">
      <div className="projects-header">
        <h1 className="projects-title">我的项目</h1>
        <button
          className="btn-generate"
          style={{ width: 'auto', padding: '12px 24px' }}
          onClick={() => window.location.reload()}
        >
          🔄 刷新列表
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#86868B' }}>
          加载中...
        </div>
      ) : projects.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#86868B' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📁</div>
          <div>暂无项目</div>
          <div style={{ fontSize: '14px', marginTop: '8px' }}>点击"创建视频"开始制作</div>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map(project => (
            <div
              key={project.id}
              className="project-card"
              onClick={() => handlePlayVideo(project.id)}
              style={{ cursor: 'pointer' }}
            >
              <div className="project-thumbnail">
                {project.status === 'completed' ? '🎬' : project.status === 'processing' ? '⏳' : '❌'}
              </div>
              <div className="project-info">
                <h3 className="project-title">{project.title || `项目 #${project.id}`}</h3>
                <div className="project-meta">
                  <span className={`project-status ${project.status}`}>
                    {project.status === 'completed' ? '✓ 已完成' :
                     project.status === 'processing' ? '⏳ 处理中' :
                     project.status === 'pending' ? '⏸️ 待处理' : '✗ 失败'}
                  </span>
                  <span className="project-date">ID: {project.id}</span>
                </div>
                {project.status === 'completed' && (
                  <div style={{ marginTop: '8px' }}>
                    <div style={{
                      fontSize: '12px',
                      color: '#007AFF',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}>
                      👆 点击查看视频
                    </div>
                    <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                      <button
                        onClick={(e) => handleExportMP4(project.id, e)}
                        disabled={exportingId === project.id}
                        style={{
                          flex: 1,
                          padding: '6px 8px',
                          background: 'rgba(16, 185, 129, 0.2)',
                          border: '1px solid rgba(16, 185, 129, 0.3)',
                          borderRadius: '6px',
                          color: '#34C759',
                          fontSize: '11px',
                          cursor: 'pointer'
                        }}
                      >
                        📥 MP4
                      </button>
                      <button
                        onClick={(e) => handleExportGIF(project.id, e)}
                        disabled={exportingId === project.id}
                        style={{
                          flex: 1,
                          padding: '6px 8px',
                          background: 'rgba(245, 158, 11, 0.2)',
                          border: '1px solid rgba(245, 158, 11, 0.3)',
                          borderRadius: '6px',
                          color: '#FF9500',
                          fontSize: '11px',
                          cursor: 'pointer'
                        }}
                      >
                        🎬 GIF
                      </button>
                      <button
                        onClick={(e) => handleShare(project.id, e)}
                        style={{
                          flex: 1,
                          padding: '6px 8px',
                          background: 'rgba(139, 92, 246, 0.2)',
                          border: '1px solid rgba(139, 92, 246, 0.3)',
                          borderRadius: '6px',
                          color: '#AF52DE',
                          fontSize: '11px',
                          cursor: 'pointer'
                        }}
                      >
                        🔗 分享
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function SettingsPage() {
  const [apiKey, setApiKey] = useState('');
  const [autoSave, setAutoSave] = useState(true);
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/status`)
      .then(r => r.json())
      .then(setStatus)
      .catch(console.error);
  }, []);

  return (
    <div className="settings">
      <div className="settings-section">
        <h2 className="settings-section-title">
          <span>🔑</span> API 状态
        </h2>
        {status && (
          <div style={{
            padding: '16px',
            background: 'var(--bg-card)',
            borderRadius: '12px',
            marginBottom: '16px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: status.minimax_api_key_set ? '#34C759' : '#ef4444'
              }}></span>
              <span>MiniMax API: {status.minimax_api_key_set ? '已配置' : '未配置'}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: status.minimax_api?.tts?.available ? '#34C759' : '#ef4444'
              }}></span>
              <span>TTS 语音: {status.minimax_api?.tts?.available ? '可用' : '不可用'}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: status.minimax_api?.video?.available ? '#34C759' : '#FF9500'
              }}></span>
              <span>视频生成: {status.minimax_api?.video?.available ? '可用' : '需要配置'}</span>
            </div>
          </div>
        )}
      </div>

      <div className="settings-section">
        <h2 className="settings-section-title">
          <span>⚡</span> 偏好设置
        </h2>
        <div className="settings-item">
          <div>
            <div className="settings-item-label">自动保存</div>
            <div className="settings-item-desc">编辑时自动保存草稿</div>
          </div>
          <div
            className={`settings-toggle ${autoSave ? 'active' : ''}`}
            onClick={() => setAutoSave(!autoSave)}
          />
        </div>
        <div className="settings-item">
          <div>
            <div className="settings-item-label">高清导出</div>
            <div className="settings-item-desc">默认导出 1080P 视频</div>
          </div>
          <div className="settings-toggle active" />
        </div>
      </div>

      <div className="settings-section">
        <h2 className="settings-section-title">
          <span>💬</span> 支持
        </h2>
        <div className="settings-item">
          <div>
            <div className="settings-item-label">帮助文档</div>
            <div className="settings-item-desc">查看使用教程和常见问题</div>
          </div>
          <span>→</span>
        </div>
        <div className="settings-item">
          <div>
            <div className="settings-item-label">联系客服</div>
            <div className="settings-item-desc">获取技术支持和反馈</div>
          </div>
          <span>→</span>
        </div>
      </div>
    </div>
  );
}

export default App;
