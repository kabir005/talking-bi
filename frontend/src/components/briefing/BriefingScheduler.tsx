import { useState, useEffect } from 'react';
import { Calendar, Plus, Trash2, Send, Loader, Mail, Clock, Users } from 'lucide-react';
import {
  createBriefing,
  listBriefings,
  deleteBriefing,
  sendBriefingNow,
  getSchedulePresets,
  Briefing,
  BriefingConfig,
  SchedulePreset
} from '../../api/briefing';
import { listDatasets } from '../../api/datasets';
import toast from 'react-hot-toast';

export default function BriefingScheduler() {
  const [briefings, setBriefings] = useState<Briefing[]>([]);
  const [datasets, setDatasets] = useState<any[]>([]);
  const [presets, setPresets] = useState<SchedulePreset[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState<string | null>(null);

  const [formData, setFormData] = useState<BriefingConfig>({
    name: '',
    dataset_id: '',
    recipients: [],
    schedule: '0 8 * * *',
    timezone: 'UTC',
    include_kpis: true,
    include_trends: true,
    include_anomalies: true
  });

  const [recipientInput, setRecipientInput] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [briefingsData, datasetsData, presetsData] = await Promise.all([
        listBriefings(),
        listDatasets(),
        getSchedulePresets()
      ]);
      setBriefings(briefingsData.briefings);
      // Backend returns array directly, not wrapped
      setDatasets(Array.isArray(datasetsData) ? datasetsData : (datasetsData as any).datasets || []);
      setPresets(presetsData.presets);
    } catch (error) {
      console.error('Failed to load data:', error);
      toast.error('Failed to load data');
    }
  };

  const handleAddRecipient = () => {
    const email = recipientInput.trim();
    if (!email) return;
    
    // Basic email validation
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      toast.error('Invalid email address');
      return;
    }
    
    if (formData.recipients.includes(email)) {
      toast.error('Email already added');
      return;
    }
    
    setFormData({
      ...formData,
      recipients: [...formData.recipients, email]
    });
    setRecipientInput('');
  };

  const handleRemoveRecipient = (email: string) => {
    setFormData({
      ...formData,
      recipients: formData.recipients.filter(r => r !== email)
    });
  };

  const handleCreate = async () => {
    if (!formData.name || !formData.dataset_id || formData.recipients.length === 0) {
      toast.error('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      await createBriefing(formData);
      toast.success('Briefing created successfully');
      setShowForm(false);
      setFormData({
        name: '',
        dataset_id: '',
        recipients: [],
        schedule: '0 8 * * *',
        timezone: 'UTC',
        include_kpis: true,
        include_trends: true,
        include_anomalies: true
      });
      loadData();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create briefing');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (briefingId: string) => {
    if (!confirm('Delete this briefing?')) return;

    try {
      await deleteBriefing(briefingId);
      toast.success('Briefing deleted');
      loadData();
    } catch (error) {
      toast.error('Failed to delete briefing');
    }
  };

  const handleSendNow = async (briefingId: string) => {
    setSending(briefingId);
    try {
      const result = await sendBriefingNow(briefingId);
      toast.success(result.message);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to send briefing');
    } finally {
      setSending(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-text-primary">Morning Briefings</h2>
          <p className="text-text-secondary mt-1">Schedule automated email reports with insights</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-accent text-bg rounded-lg hover:bg-accent/90 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Create Briefing
        </button>
      </div>

      {showForm && (
        <div className="bg-surface rounded-lg shadow-sm border border-border p-6 space-y-4">
          <h3 className="text-lg font-semibold text-text-primary">New Briefing</h3>

          <div>
            <label className="block text-sm font-medium mb-1 text-text-primary">Briefing Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-border rounded-lg bg-surface text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
              placeholder="Daily Executive Summary"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-text-primary">Dataset</label>
            <select
              value={formData.dataset_id}
              onChange={(e) => setFormData({ ...formData, dataset_id: e.target.value })}
              className="w-full px-3 py-2 border border-border rounded-lg bg-surface text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
            >
              <option value="">Select dataset...</option>
              {datasets.map((ds) => (
                <option key={ds.id} value={ds.id}>
                  {ds.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-text-primary">Recipients</label>
            <div className="flex gap-2 mb-2">
              <input
                type="email"
                value={recipientInput}
                onChange={(e) => setRecipientInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddRecipient()}
                className="flex-1 px-3 py-2 border border-border rounded-lg bg-surface text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                placeholder="email@example.com"
              />
              <button
                onClick={handleAddRecipient}
                className="px-4 py-2 bg-surface-elevated text-text-primary border border-border rounded-lg hover:bg-white/[0.04] transition-colors"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.recipients.map((email) => (
                <div
                  key={email}
                  className="flex items-center gap-2 px-3 py-1 bg-accent/20 text-accent rounded-full text-sm"
                >
                  <span>{email}</span>
                  <button
                    onClick={() => handleRemoveRecipient(email)}
                    className="text-accent hover:text-accent/80"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1 text-text-primary">Schedule</label>
              <select
                value={formData.schedule}
                onChange={(e) => setFormData({ ...formData, schedule: e.target.value })}
                className="w-full px-3 py-2 border border-border rounded-lg bg-surface text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
              >
                {presets.map((preset) => (
                  <option key={preset.cron} value={preset.cron}>
                    {preset.label}
                  </option>
                ))}
              </select>
              <p className="text-xs text-text-secondary mt-1">
                {presets.find(p => p.cron === formData.schedule)?.description}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1 text-text-primary">Timezone</label>
              <select
                value={formData.timezone}
                onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
                className="w-full px-3 py-2 border border-border rounded-lg bg-surface text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
              >
                <option value="UTC">UTC</option>
                <option value="America/New_York">Eastern Time</option>
                <option value="America/Chicago">Central Time</option>
                <option value="America/Denver">Mountain Time</option>
                <option value="America/Los_Angeles">Pacific Time</option>
                <option value="Europe/London">London</option>
                <option value="Asia/Tokyo">Tokyo</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2 text-text-primary">Include in Report</label>
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-text-primary">
                <input
                  type="checkbox"
                  checked={formData.include_kpis}
                  onChange={(e) => setFormData({ ...formData, include_kpis: e.target.checked })}
                  className="rounded"
                />
                <span className="text-sm">Key Performance Indicators (KPIs)</span>
              </label>
              <label className="flex items-center gap-2 text-text-primary">
                <input
                  type="checkbox"
                  checked={formData.include_trends}
                  onChange={(e) => setFormData({ ...formData, include_trends: e.target.checked })}
                  className="rounded"
                />
                <span className="text-sm">Trends Analysis</span>
              </label>
              <label className="flex items-center gap-2 text-text-primary">
                <input
                  type="checkbox"
                  checked={formData.include_anomalies}
                  onChange={(e) => setFormData({ ...formData, include_anomalies: e.target.checked })}
                  className="rounded"
                />
                <span className="text-sm">Anomaly Detection</span>
              </label>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => setShowForm(false)}
              className="flex-1 px-4 py-2 border border-border rounded-lg hover:bg-white/[0.04] text-text-primary transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleCreate}
              disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-accent text-bg rounded-lg hover:bg-accent/90 disabled:opacity-50 transition-colors"
            >
              {loading ? <Loader className="w-4 h-4 animate-spin" /> : <Calendar className="w-4 h-4" />}
              Create Briefing
            </button>
          </div>
        </div>
      )}

      <div className="space-y-4">
        {briefings.length === 0 ? (
          <div className="text-center py-12 bg-surface rounded-lg border border-border">
            <Mail className="w-12 h-12 mx-auto mb-3 text-text-secondary" />
            <p className="text-text-primary mb-2">No briefings scheduled yet</p>
            <p className="text-sm text-text-secondary">Create your first automated briefing to get started</p>
          </div>
        ) : (
          briefings.map((briefing) => (
            <div
              key={briefing.briefing_id}
              className="bg-surface rounded-lg shadow-sm border border-border p-6"
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-text-primary">{briefing.name}</h3>
                  <p className="text-sm text-text-secondary mt-1">
                    Dataset: {briefing.dataset_name || briefing.dataset_id}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleSendNow(briefing.briefing_id)}
                    disabled={sending === briefing.briefing_id}
                    className="p-2 text-accent hover:bg-accent/10 rounded-lg disabled:opacity-50 transition-colors"
                    title="Send now"
                  >
                    {sending === briefing.briefing_id ? (
                      <Loader className="w-4 h-4 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                  </button>
                  <button
                    onClick={() => handleDelete(briefing.briefing_id)}
                    className="p-2 text-red-500 hover:bg-red-500/10 rounded-lg transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="flex items-center gap-2 text-sm">
                  <Clock className="w-4 h-4 text-text-secondary" />
                  <div>
                    <div className="text-text-secondary">Schedule</div>
                    <div className="font-medium text-text-primary">
                      {presets.find(p => p.cron === briefing.schedule)?.label || 'Custom'}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-sm">
                  <Calendar className="w-4 h-4 text-text-secondary" />
                  <div>
                    <div className="text-text-secondary">Next Run</div>
                    <div className="font-medium text-text-primary">
                      {briefing.next_run 
                        ? new Date(briefing.next_run).toLocaleString()
                        : 'Not scheduled'}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-sm">
                  <Users className="w-4 h-4 text-text-secondary" />
                  <div>
                    <div className="text-text-secondary">Recipients</div>
                    <div className="font-medium text-text-primary">{briefing.recipients.length} people</div>
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                {briefing.recipients.map((email) => (
                  <span
                    key={email}
                    className="px-2 py-1 bg-surface-elevated text-text-primary rounded text-xs"
                  >
                    {email}
                  </span>
                ))}
              </div>

              <div className="mt-4 flex gap-2">
                {briefing.include_kpis && (
                  <span className="px-2 py-1 bg-blue-500/20 text-blue-500 rounded text-xs">
                    KPIs
                  </span>
                )}
                {briefing.include_trends && (
                  <span className="px-2 py-1 bg-green-500/20 text-green-500 rounded text-xs">
                    Trends
                  </span>
                )}
                {briefing.include_anomalies && (
                  <span className="px-2 py-1 bg-orange-500/20 text-orange-500 rounded text-xs">
                    Anomalies
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
