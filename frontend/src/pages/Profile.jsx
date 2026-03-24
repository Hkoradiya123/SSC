import React, { useState, useEffect } from 'react';
import { playerService, performanceService, premiumService, adminService } from '../utils/api';
import { useParams } from 'react-router-dom';
import styles from './profile.module.css';

export function ProfilePage() {
  const { playerId } = useParams();
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState(null);
  const [performances, setPerformances] = useState([]);
  const [aiInsights, setAiInsights] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [isOwnProfile, setIsOwnProfile] = useState(false);
  const [editingStats, setEditingStats] = useState(false);
  const [statsForm, setStatsForm] = useState({
    runs: 0,
    matches: 0,
    wickets: 0,
    centuries: 0,
    half_centuries: 0,
    highest_score: 0,
  });
  const [newLogForm, setNewLogForm] = useState({
    match_date: '',
    runs_scored: '',
    wickets_taken: '',
    match_type: 'friendly',
    opponent: '',
    performance_rating: '',
    notes: '',
  });
  const [editingLogId, setEditingLogId] = useState(null);
  const [editLogForm, setEditLogForm] = useState({
    runs_scored: '',
    wickets_taken: '',
    match_type: 'friendly',
    opponent: '',
    performance_rating: '',
    notes: '',
  });

  const fetchData = async () => {
    try {
      const currentUser = JSON.parse(localStorage.getItem('user'));
      let profileId = playerId || currentUser?.id;
      const isOwn = !playerId || String(playerId) === String(currentUser?.id);
      setIsOwnProfile(isOwn);

      let playerRes;
      let statsRes;
      let logsRes;
      let aiRes;
      let chatRes;

      if (isOwn) {
        // Always resolve own profile from backend identity instead of localStorage id.
        playerRes = await playerService.getCurrentPlayer();
        if (playerRes?.data?.id !== undefined && playerRes?.data?.id !== null) {
          profileId = playerRes.data.id;
          localStorage.setItem('user', JSON.stringify(playerRes.data));
          window.dispatchEvent(new Event('authchange'));
        }

        [statsRes, logsRes, aiRes, chatRes] = await Promise.all([
          performanceService.getPlayerStats(profileId),
          performanceService.getPlayerLogs(profileId),
          performanceService.getAiInsights(profileId),
          adminService.getMyChat(),
        ]);
      } else {
        [playerRes, statsRes, logsRes, aiRes] = await Promise.all([
          playerService.getPlayer(profileId),
          performanceService.getPlayerStats(profileId),
          performanceService.getPlayerLogs(profileId),
          performanceService.getAiInsights(profileId),
        ]);
      }

      setUser(playerRes.data);
      setStats(statsRes.data);
      setPerformances(logsRes.data || []);
      setAiInsights(aiRes.data?.insights || null);

      if (isOwn && chatRes?.data) {
        setChatMessages(chatRes.data);
      }

      if (statsRes.data) {
        setStatsForm({
          runs: statsRes.data.runs || 0,
          matches: statsRes.data.matches || 0,
          wickets: statsRes.data.wickets || 0,
          centuries: statsRes.data.centuries || 0,
          half_centuries: statsRes.data.half_centuries || 0,
          highest_score: statsRes.data.highest_score || 0,
        });
      }
    } catch (error) {
      console.error('Failed to load profile:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [playerId]);

  const handleUpgradePremium = async () => {
    try {
      await premiumService.upgradePremium(30);
      alert('Upgraded to premium! ✨');
      window.location.reload();
    } catch (error) {
      alert('Premium upgrade failed');
    }
  };

  const handleStatsSave = async () => {
    try {
      await playerService.updateCareerStats({
        runs: Number(statsForm.runs),
        matches: Number(statsForm.matches),
        wickets: Number(statsForm.wickets),
        centuries: Number(statsForm.centuries),
        half_centuries: Number(statsForm.half_centuries),
        highest_score: Number(statsForm.highest_score),
      });
      setEditingStats(false);
      fetchData();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to save career stats');
    }
  };

  const handleAddLog = async (e) => {
    e.preventDefault();
    try {
      await performanceService.logPerformance({
        match_date: newLogForm.match_date || new Date().toISOString(),
        runs_scored: Number(newLogForm.runs_scored || 0),
        wickets_taken: Number(newLogForm.wickets_taken || 0),
        match_type: newLogForm.match_type,
        opponent: newLogForm.opponent || null,
        performance_rating: Number(newLogForm.performance_rating || 0),
        notes: newLogForm.notes || null,
      });
      setNewLogForm({
        match_date: '',
        runs_scored: '',
        wickets_taken: '',
        match_type: 'friendly',
        opponent: '',
        performance_rating: '',
        notes: '',
      });
      fetchData();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to add performance log');
    }
  };

  const startEditLog = (log) => {
    setEditingLogId(log.id);
    setEditLogForm({
      runs_scored: log.runs_scored,
      wickets_taken: log.wickets_taken,
      match_type: log.match_type,
      opponent: log.opponent || '',
      performance_rating: log.performance_rating,
      notes: log.notes || '',
    });
  };

  const handleSaveLog = async (logId) => {
    try {
      await performanceService.updateLog(logId, {
        runs_scored: Number(editLogForm.runs_scored || 0),
        wickets_taken: Number(editLogForm.wickets_taken || 0),
        match_type: editLogForm.match_type,
        opponent: editLogForm.opponent,
        performance_rating: Number(editLogForm.performance_rating || 0),
        notes: editLogForm.notes,
      });
      setEditingLogId(null);
      fetchData();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to update performance log');
    }
  };

  const handleDeleteLog = async (logId) => {
    if (!window.confirm('Delete this performance log?')) return;
    try {
      await performanceService.deleteLog(logId);
      fetchData();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to delete performance log');
    }
  };

  const handleSendToAdmin = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    try {
      await adminService.sendPlayerMessage(chatInput.trim());
      setChatInput('');
      const chatRes = await adminService.getMyChat();
      setChatMessages(chatRes.data || []);
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to send message to admin');
    }
  };

  if (loading) return <div className={styles.loading}>Loading profile...</div>;

  return (
    <div className={styles.profilePage}>
      <div className={styles.container}>
        {user && (
          <>
            <div className={styles.profileHeader}>
              <div className={styles.profileInfo}>
                <h1>{user.name}</h1>
                {user.is_premium && <span className={styles.premiumBadge}>⭐ Premium Member</span>}
                <p className={styles.email}>{user.email}</p>
                {user.bio && <p className={styles.bio}>{user.bio}</p>}
              </div>

              {isOwnProfile && !user.is_premium && (
                <button className={styles.premiumBtn} onClick={handleUpgradePremium}>
                  🚀 Upgrade to Premium - ₹1000/month
                </button>
              )}
            </div>

            {stats && (
              <div className={styles.statsSection}>
                <div className={styles.sectionHeader}>
                  <h2>Career Statistics</h2>
                  {isOwnProfile && (
                    <button className={styles.inlineBtn} onClick={() => setEditingStats((prev) => !prev)}>
                      {editingStats ? 'Cancel' : 'Edit Stats'}
                    </button>
                  )}
                </div>
                <div className={styles.statsGrid}>
                  {[
                    ['runs', 'Total Runs'],
                    ['matches', 'Matches'],
                    ['wickets', 'Wickets'],
                    ['centuries', 'Centuries'],
                    ['half_centuries', 'Half-Centuries'],
                    ['highest_score', 'Highest Score'],
                  ].map(([key, label]) => (
                    <div className={styles.statBox} key={key}>
                      <span className={styles.statLabel}>{label}</span>
                      {editingStats ? (
                        <input
                          type="number"
                          min="0"
                          value={statsForm[key]}
                          onChange={(e) => setStatsForm((prev) => ({ ...prev, [key]: e.target.value }))}
                        />
                      ) : (
                        <span className={styles.statValue}>{stats[key]}</span>
                      )}
                    </div>
                  ))}
                  <div className={styles.statBox}>
                    <span className={styles.statLabel}>Average Runs</span>
                    <span className={styles.statValue}>{stats.average_runs}</span>
                  </div>
                </div>
                {editingStats && (
                  <div className={styles.saveRow}>
                    <button className={styles.saveBtn} onClick={handleStatsSave}>Save Career Stats</button>
                  </div>
                )}
              </div>
            )}

            {aiInsights && (
              <div className={styles.aiSection}>
                <h2>AI-Based Performance Insights</h2>
                <div className={styles.aiGrid}>
                  <div className={styles.aiCard}>
                    <span>Current Form</span>
                    <strong>{aiInsights.form}</strong>
                  </div>
                  <div className={styles.aiCard}>
                    <span>Consistency Score</span>
                    <strong>{aiInsights.consistency_score}%</strong>
                  </div>
                  <div className={styles.aiCard}>
                    <span>Recent Avg Runs</span>
                    <strong>{aiInsights.recent_average_runs || 0}</strong>
                  </div>
                </div>
                <div className={styles.aiTextGrid}>
                  <div>
                    <h4>Strengths</h4>
                    <ul>
                      {(aiInsights.strengths || []).map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4>Focus Areas</h4>
                    <ul>
                      {(aiInsights.focus_areas || []).map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {isOwnProfile && (
              <div className={styles.performanceSection}>
                <h2>Recent Performances</h2>

                <form className={styles.logForm} onSubmit={handleAddLog}>
                  <h3>Add Match Performance</h3>
                  <div className={styles.logGrid}>
                    <input
                      type="datetime-local"
                      value={newLogForm.match_date}
                      onChange={(e) => setNewLogForm((prev) => ({ ...prev, match_date: e.target.value }))}
                    />
                    <input
                      type="number"
                      min="0"
                      placeholder="Runs"
                      value={newLogForm.runs_scored}
                      onChange={(e) => setNewLogForm((prev) => ({ ...prev, runs_scored: e.target.value }))}
                      required
                    />
                    <input
                      type="number"
                      min="0"
                      placeholder="Wickets"
                      value={newLogForm.wickets_taken}
                      onChange={(e) => setNewLogForm((prev) => ({ ...prev, wickets_taken: e.target.value }))}
                    />
                    <input
                      type="text"
                      placeholder="Opponent"
                      value={newLogForm.opponent}
                      onChange={(e) => setNewLogForm((prev) => ({ ...prev, opponent: e.target.value }))}
                    />
                    <input
                      type="number"
                      min="0"
                      max="10"
                      step="0.1"
                      placeholder="Rating (0-10)"
                      value={newLogForm.performance_rating}
                      onChange={(e) => setNewLogForm((prev) => ({ ...prev, performance_rating: e.target.value }))}
                    />
                    <select
                      value={newLogForm.match_type}
                      onChange={(e) => setNewLogForm((prev) => ({ ...prev, match_type: e.target.value }))}
                    >
                      <option value="friendly">Friendly</option>
                      <option value="league">League</option>
                      <option value="tournament">Tournament</option>
                    </select>
                  </div>
                  <textarea
                    placeholder="Notes"
                    value={newLogForm.notes}
                    onChange={(e) => setNewLogForm((prev) => ({ ...prev, notes: e.target.value }))}
                  />
                  <button type="submit">Add Performance</button>
                </form>

                <div className={styles.performancesList}>
                  {performances.length > 0 ? (
                    performances.map((perf) => (
                      <div key={perf.id} className={styles.performanceItem}>
                        {editingLogId === perf.id ? (
                          <div className={styles.editLogGrid}>
                            <input
                              type="number"
                              min="0"
                              value={editLogForm.runs_scored}
                              onChange={(e) => setEditLogForm((prev) => ({ ...prev, runs_scored: e.target.value }))}
                            />
                            <input
                              type="number"
                              min="0"
                              value={editLogForm.wickets_taken}
                              onChange={(e) => setEditLogForm((prev) => ({ ...prev, wickets_taken: e.target.value }))}
                            />
                            <input
                              type="text"
                              value={editLogForm.opponent}
                              onChange={(e) => setEditLogForm((prev) => ({ ...prev, opponent: e.target.value }))}
                              placeholder="Opponent"
                            />
                            <input
                              type="number"
                              min="0"
                              max="10"
                              step="0.1"
                              value={editLogForm.performance_rating}
                              onChange={(e) => setEditLogForm((prev) => ({ ...prev, performance_rating: e.target.value }))}
                            />
                            <select
                              value={editLogForm.match_type}
                              onChange={(e) => setEditLogForm((prev) => ({ ...prev, match_type: e.target.value }))}
                            >
                              <option value="friendly">Friendly</option>
                              <option value="league">League</option>
                              <option value="tournament">Tournament</option>
                            </select>
                            <input
                              type="text"
                              value={editLogForm.notes}
                              onChange={(e) => setEditLogForm((prev) => ({ ...prev, notes: e.target.value }))}
                              placeholder="Notes"
                            />
                            <div className={styles.actionButtons}>
                              <button className={styles.saveBtn} onClick={() => handleSaveLog(perf.id)}>
                                Save
                              </button>
                              <button className={styles.cancelBtn} onClick={() => setEditingLogId(null)}>
                                Cancel
                              </button>
                            </div>
                          </div>
                        ) : (
                          <>
                            <div>
                              <p className={styles.perfDate}>
                                {new Date(perf.match_date).toLocaleDateString()}
                              </p>
                              <p className={styles.perfOpponent}>{perf.opponent || 'Friendly Match'}</p>
                              <p className={styles.perfType}>{perf.match_type}</p>
                            </div>
                            <div className={styles.perfStats}>
                              <span className={styles.runs}>{perf.runs_scored} runs</span>
                              {perf.wickets_taken > 0 && (
                                <span className={styles.wickets}>{perf.wickets_taken} wickets</span>
                              )}
                              <span className={styles.rating}>Rating {perf.performance_rating}</span>
                            </div>
                            <div className={styles.actions}>
                              <button onClick={() => startEditLog(perf)}>Edit</button>
                              <button className={styles.deleteBtn} onClick={() => handleDeleteLog(perf.id)}>
                                Delete
                              </button>
                            </div>
                          </>
                        )}
                      </div>
                    ))
                  ) : (
                    <p>No performance logs yet</p>
                  )}
                </div>
              </div>
            )}

            {isOwnProfile && (
              <div className={styles.chatSection}>
                <h2>Admin Support Chat</h2>
                <div className={styles.chatMessages}>
                  {chatMessages.length === 0 ? (
                    <p>No messages yet. Ask admin anything about your account.</p>
                  ) : (
                    chatMessages.map((msg) => (
                      <div
                        key={msg.id}
                        className={msg.sender_role === 'admin' ? styles.chatAdmin : styles.chatPlayer}
                      >
                        <span>{msg.message}</span>
                        <small>{new Date(msg.created_at).toLocaleString()}</small>
                      </div>
                    ))
                  )}
                </div>
                <form className={styles.chatForm} onSubmit={handleSendToAdmin}>
                  <input
                    type="text"
                    placeholder="Type a message to admin..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                  />
                  <button type="submit">Send</button>
                </form>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
