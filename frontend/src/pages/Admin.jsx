import React, { useEffect, useMemo, useState } from 'react';
import { adminService } from '../utils/api';
import styles from './admin.module.css';

export function AdminPage() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [threads, setThreads] = useState([]);
  const [activeThreadUser, setActiveThreadUser] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const user = useMemo(() => {
    try {
      return JSON.parse(localStorage.getItem('user') || 'null');
    } catch {
      return null;
    }
  }, []);

  const isAdmin = user?.role === 'admin';

  const loadDashboard = async () => {
    try {
      setError('');
      const [statsRes, usersRes, chatRes] = await Promise.all([
        adminService.getSystemStats(),
        adminService.getAllUsers(0, 100),
        adminService.getChatThreads(),
      ]);

      setStats(statsRes.data);
      setUsers(usersRes.data || []);
      setThreads(chatRes.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load admin dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!isAdmin) {
      setLoading(false);
      return;
    }
    loadDashboard();
  }, [isAdmin]);

  const openThread = async (thread) => {
    try {
      setActiveThreadUser(thread);
      const threadRes = await adminService.getChatThread(thread.user_id);
      setMessages(threadRes.data || []);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to open chat thread');
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!activeThreadUser || !newMessage.trim()) return;

    try {
      await adminService.sendAdminMessage(activeThreadUser.user_id, newMessage.trim());
      setNewMessage('');
      const threadRes = await adminService.getChatThread(activeThreadUser.user_id);
      setMessages(threadRes.data || []);
      loadDashboard();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to send message');
    }
  };

  const handleTogglePremium = async (userId) => {
    try {
      await adminService.toggleUserPremium(userId, 30);
      loadDashboard();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update premium status');
    }
  };

  const handleDeactivate = async (userId) => {
    if (!window.confirm('Deactivate this user?')) return;
    try {
      await adminService.deactivateUser(userId);
      loadDashboard();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to deactivate user');
    }
  };

  if (loading) return <div className={styles.loading}>Loading admin dashboard...</div>;

  if (!isAdmin) {
    return (
      <div className={styles.page}>
        <div className={styles.denied}>Admin access required.</div>
      </div>
    );
  }

  if (error) return <div className={styles.error}>{error}</div>;

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <div className={styles.header}>
          <h1>Admin Control Center</h1>
          <p>Manage users, finances, and live player support conversations.</p>
        </div>

        <div className={styles.statsGrid}>
          <div className={styles.statCard}>
            <span>Total Users</span>
            <strong>{stats?.total_users || 0}</strong>
          </div>
          <div className={styles.statCard}>
            <span>Active Users</span>
            <strong>{stats?.active_users || 0}</strong>
          </div>
          <div className={styles.statCard}>
            <span>Premium Users</span>
            <strong>{stats?.premium_users || 0}</strong>
          </div>
          <div className={styles.statCard}>
            <span>Total Matches</span>
            <strong>{stats?.total_matches || 0}</strong>
          </div>
          <div className={styles.statCard}>
            <span>Pending Funds</span>
            <strong>Rs {Number(stats?.pending_funds || 0).toFixed(2)}</strong>
          </div>
          <div className={styles.statCard}>
            <span>Funds Remaining</span>
            <strong>Rs {Number(stats?.funds_remaining || 0).toFixed(2)}</strong>
          </div>
        </div>

        <div className={styles.layoutGrid}>
          <section className={styles.card}>
            <h2>User Operations</h2>
            <div className={styles.tableWrap}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Role</th>
                    <th>Premium</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((item) => (
                    <tr key={item.id}>
                      <td>{item.name}</td>
                      <td>{item.role}</td>
                      <td>{item.is_premium ? 'Yes' : 'No'}</td>
                      <td>{item.is_active ? 'Active' : 'Inactive'}</td>
                      <td className={styles.actionRow}>
                        <button onClick={() => handleTogglePremium(item.id)}>Toggle Premium</button>
                        <button className={styles.danger} onClick={() => handleDeactivate(item.id)}>
                          Deactivate
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className={styles.card}>
            <h2>Admin Dashboard Chats</h2>
            <div className={styles.chatLayout}>
              <div className={styles.threadList}>
                {threads.length === 0 ? (
                  <p>No player chats yet.</p>
                ) : (
                  threads.map((thread) => (
                    <button
                      key={thread.user_id}
                      className={`${styles.threadBtn} ${activeThreadUser?.user_id === thread.user_id ? styles.threadBtnActive : ''}`}
                      onClick={() => openThread(thread)}
                    >
                      <div>
                        <strong>{thread.name}</strong>
                        <small>{thread.email}</small>
                      </div>
                      {thread.unread_count > 0 && <span>{thread.unread_count}</span>}
                    </button>
                  ))
                )}
              </div>

              <div className={styles.chatWindow}>
                {!activeThreadUser ? (
                  <p>Select a player thread to start chatting.</p>
                ) : (
                  <>
                    <div className={styles.chatHeader}>
                      <h3>{activeThreadUser.name}</h3>
                      <small>{activeThreadUser.email}</small>
                    </div>
                    <div className={styles.messages}>
                      {messages.length === 0 ? (
                        <p>No messages yet.</p>
                      ) : (
                        messages.map((msg) => (
                          <div
                            key={msg.id}
                            className={msg.sender_role === 'admin' ? styles.msgAdmin : styles.msgPlayer}
                          >
                            <span>{msg.message}</span>
                            <small>{new Date(msg.created_at).toLocaleString()}</small>
                          </div>
                        ))
                      )}
                    </div>
                    <form className={styles.chatForm} onSubmit={handleSend}>
                      <input
                        type="text"
                        placeholder="Reply to player..."
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                      />
                      <button type="submit">Send</button>
                    </form>
                  </>
                )}
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
