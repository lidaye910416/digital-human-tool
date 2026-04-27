import React, { useState, useEffect } from 'react';

// 配置
const API_BASE = 'http://localhost:8001';

// Types
interface Consultation {
  id: number;
  title: string;
  content: string;
  contact: string | null;
  source: string;
  status: string;
  consultation_date: string;
  created_at: string;
  avatar_id: number | null;
  voice_id: string | null;
}

interface Statistics {
  total: number;
  pending: number;
  read: number;
  replied: number;
}

// 日期格式化
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', weekday: 'short' });
};

// 状态标签
const StatusBadge = ({ status }: { status: string }) => {
  const styles: Record<string, { bg: string; color: string; text: string }> = {
    pending: { bg: 'rgba(245, 158, 11, 0.2)', color: '#FF9500', text: '待处理' },
    read: { bg: 'rgba(99, 102, 241, 0.2)', color: '#AF52DE', text: '已查看' },
    replied: { bg: 'rgba(16, 185, 129, 0.2)', color: '#34C759', text: '已回复' },
    archived: { bg: 'rgba(134, 134, 139, 0.2)', color: '#86868B', text: '已归档' },
  };
  const style = styles[status] || styles.pending;
  return (
    <span style={{ 
      padding: '2px 8px', 
      borderRadius: '4px', 
      fontSize: '11px',
      background: style.bg, 
      color: style.color 
    }}>
      {style.text}
    </span>
  );
};

export default function ConsultationPage() {
  const [consultations, setConsultations] = useState<Consultation[]>([]);
  const [statistics, setStatistics] = useState<Statistics>({ total: 0, pending: 0, read: 0, replied: 0 });
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [availableDates, setAvailableDates] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedConsultation, setSelectedConsultation] = useState<Consultation | null>(null);
  const [message, setMessage] = useState('');

  // 新建咨询表单
  const [newTitle, setNewTitle] = useState('');
  const [newContent, setNewContent] = useState('');
  const [newContact, setNewContact] = useState('');

  // 读取中的咨询
  const [readingId, setReadingId] = useState<number | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const userId = 1;

  // 加载数据
  useEffect(() => {
    loadStatistics();
    loadAvailableDates();
    loadConsultations();
  }, [selectedDate]);

  const loadStatistics = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/consultations/statistics?user_id=${userId}`);
      const data = await res.json();
      if (data.success) setStatistics(data.data);
    } catch (e) {
      console.error('Failed to load statistics:', e);
    }
  };

  const loadAvailableDates = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/consultations/dates?user_id=${userId}`);
      const data = await res.json();
      if (data.success) setAvailableDates(data.data);
    } catch (e) {
      console.error('Failed to load dates:', e);
    }
  };

  const loadConsultations = async () => {
    setLoading(true);
    try {
      const url = `${API_BASE}/api/consultations?user_id=${userId}${selectedDate ? `&date=${selectedDate}` : ''}`;
      const res = await fetch(url);
      const data = await res.json();
      if (data.success) setConsultations(data.data);
    } catch (e) {
      console.error('Failed to load consultations:', e);
    }
    setLoading(false);
  };

  const handleCreateConsultation = async () => {
    if (!newTitle.trim() || !newContent.trim()) {
      setMessage('请填写标题和内容');
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/api/consultations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newTitle,
          content: newContent,
          contact: newContact || null,
          source: 'web',
          user_id: userId
        })
      });
      const data = await res.json();
      if (data.success) {
        setMessage('✅ 咨询提交成功！');
        setShowCreateModal(false);
        setNewTitle('');
        setNewContent('');
        setNewContact('');
        loadStatistics();
        loadAvailableDates();
        loadConsultations();
      }
    } catch (e) {
      setMessage('❌ 提交失败');
    }
  };

  const handleReadAloud = async (consultation: Consultation) => {
    setReadingId(consultation.id);
    setSelectedConsultation(consultation);
    setAudioUrl(null);

    try {
      const res = await fetch(
        `${API_BASE}/api/consultations/${consultation.id}/read-aloud?voice_id=female-tianmei`,
        { method: 'POST' }
      );
      const data = await res.json();
      if (data.success && data.data.audio_url) {
        setAudioUrl(data.data.audio_url);
      } else {
        setMessage('❌ 朗读生成失败');
      }
    } catch (e) {
      setMessage('❌ 朗读生成失败');
    }
    setReadingId(null);
  };

  const handleStatusChange = async (consultationId: number, status: string) => {
    try {
      await fetch(`${API_BASE}/api/consultations/${consultationId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });
      loadStatistics();
      loadConsultations();
    } catch (e) {
      console.error('Failed to update status:', e);
    }
  };

  const handleDelete = async (consultationId: number) => {
    if (!confirm('确定删除这条咨询？')) return;
    try {
      await fetch(`${API_BASE}/api/consultations/${consultationId}`, { method: 'DELETE' });
      loadStatistics();
      loadConsultations();
      setMessage('✅ 已删除');
    } catch (e) {
      setMessage('❌ 删除失败');
    }
  };

  return (
    <div className="consultation-page">
      {/* 消息提示 */}
      {message && (
        <div style={{
          position: 'fixed', top: '20px', left: '50%', transform: 'translateX(-50%)',
          padding: '12px 24px', background: message.includes('✅') ? 'rgba(16, 185, 129, 0.9)' : 'rgba(239, 68, 68, 0.9)',
          borderRadius: '8px', color: '#fff', zIndex: 1000, fontSize: '14px'
        }} onClick={() => setMessage('')}>
          {message}
        </div>
      )}

      {/* 头部 */}
      <div className="page-header">
        <h1>📋 技术咨询</h1>
        <button className="btn-primary" onClick={() => setShowCreateModal(true)}>
          + 新建咨询
        </button>
      </div>

      {/* 统计卡片 */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{statistics.total}</div>
          <div className="stat-label">总咨询</div>
        </div>
        <div className="stat-card pending">
          <div className="stat-value">{statistics.pending}</div>
          <div className="stat-label">待处理</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{statistics.read}</div>
          <div className="stat-label">已查看</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{statistics.replied}</div>
          <div className="stat-label">已回复</div>
        </div>
      </div>

      {/* 日期筛选 */}
      <div className="date-filter">
        <button 
          className={`date-btn ${!selectedDate ? 'active' : ''}`}
          onClick={() => setSelectedDate(null)}
        >
          全部
        </button>
        {availableDates.map(date => (
          <button
            key={date}
            className={`date-btn ${selectedDate === date ? 'active' : ''}`}
            onClick={() => setSelectedDate(date)}
          >
            {formatDate(date)}
          </button>
        ))}
      </div>

      {/* 咨询列表 */}
      <div className="consultation-list">
        {loading ? (
          <div className="loading">加载中...</div>
        ) : consultations.length === 0 ? (
          <div className="empty-state">
            <div style={{ fontSize: '48px' }}>📭</div>
            <div>暂无咨询</div>
            <div style={{ fontSize: '13px', color: '#86868B' }}>点击上方按钮新建咨询</div>
          </div>
        ) : (
          consultations.map(c => (
            <div key={c.id} className="consultation-card">
              <div className="consultation-header">
                <div className="consultation-title">{c.title}</div>
                <StatusBadge status={c.status} />
              </div>
              <div className="consultation-content">{c.content}</div>
              <div className="consultation-meta">
                <span>📅 {c.consultation_date}</span>
                <span>📱 {c.source}</span>
                {c.contact && <span>📧 {c.contact}</span>}
              </div>
              <div className="consultation-actions">
                <button onClick={() => handleReadAloud(c)} disabled={readingId === c.id}>
                  {readingId === c.id ? '⏳ 生成中...' : '🔊 朗读'}
                </button>
                <button onClick={() => handleStatusChange(c.id, c.status === 'pending' ? 'read' : 'replied')}>
                  {c.status === 'pending' ? '标记已读' : '标记已回复'}
                </button>
                <button className="delete-btn" onClick={() => handleDelete(c.id)}>删除</button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* 朗读播放器 */}
      {selectedConsultation && (
        <div className="audio-player-bar">
          <div className="player-info">
            <span>🔊 正在朗读:</span>
            <span style={{ fontWeight: 500 }}>{selectedConsultation.title}</span>
          </div>
          {audioUrl ? (
            <audio src={audioUrl} controls autoPlay style={{ height: '36px', flex: 1 }} />
          ) : readingId === null ? null : (
            <span>生成中...</span>
          )}
          <button onClick={() => { setSelectedConsultation(null); setAudioUrl(null); }}>✕</button>
        </div>
      )}

      {/* 新建咨询弹窗 */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📝 新建技术咨询</h2>
              <button onClick={() => setShowCreateModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>咨询标题 *</label>
                <input
                  type="text"
                  value={newTitle}
                  onChange={e => setNewTitle(e.target.value)}
                  placeholder="简要描述您的问题"
                />
              </div>
              <div className="form-group">
                <label>咨询内容 *</label>
                <textarea
                  value={newContent}
                  onChange={e => setNewContent(e.target.value)}
                  placeholder="详细描述您遇到的技术问题..."
                  rows={6}
                />
              </div>
              <div className="form-group">
                <label>联系方式（可选）</label>
                <input
                  type="text"
                  value={newContact}
                  onChange={e => setNewContact(e.target.value)}
                  placeholder="邮箱或电话"
                />
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowCreateModal(false)}>取消</button>
              <button className="btn-primary" onClick={handleCreateConsultation}>提交咨询</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
