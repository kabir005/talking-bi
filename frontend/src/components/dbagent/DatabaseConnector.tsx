import { useState, useEffect } from 'react';
import { Database, Plus, Trash2, CheckCircle, Loader } from 'lucide-react';
import { 
  testConnection, 
  createConnection, 
  listConnections, 
  deleteConnection,
  Connection,
  ConnectionConfig 
} from '../../api/dbAgent';
import toast from 'react-hot-toast';

interface DatabaseConnectorProps {
  onConnectionSelect: (connectionId: string) => void;
  selectedConnectionId?: string;
}

export default function DatabaseConnector({ onConnectionSelect, selectedConnectionId }: DatabaseConnectorProps) {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [testing, setTesting] = useState(false);
  const [creating, setCreating] = useState(false);
  
  const [formData, setFormData] = useState<ConnectionConfig>({
    name: '',
    db_type: 'postgresql',
    host: 'localhost',
    port: 5432,
    database: '',
    username: '',
    password: '',
    ssl: false
  });

  useEffect(() => {
    loadConnections();
  }, []);

  const loadConnections = async () => {
    try {
      const data = await listConnections();
      setConnections(data.connections);
    } catch (error) {
      console.error('Failed to load connections:', error);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    try {
      const result = await testConnection(formData);
      if (result.success) {
        toast.success(result.message);
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Connection test failed');
    } finally {
      setTesting(false);
    }
  };

  const handleCreate = async () => {
    setCreating(true);
    try {
      await createConnection(formData);
      toast.success('Connection created successfully');
      setShowForm(false);
      setFormData({
        name: '',
        db_type: 'postgresql',
        host: 'localhost',
        port: 5432,
        database: '',
        username: '',
        password: '',
        ssl: false
      });
      loadConnections();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create connection');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (connectionId: string) => {
    if (!confirm('Delete this connection?')) return;
    
    try {
      await deleteConnection(connectionId);
      toast.success('Connection deleted');
      loadConnections();
      if (selectedConnectionId === connectionId) {
        onConnectionSelect('');
      }
    } catch (error) {
      toast.error('Failed to delete connection');
    }
  };

  const handleDbTypeChange = (type: 'postgresql' | 'mysql' | 'sqlite') => {
    const defaultPorts = { postgresql: 5432, mysql: 3306, sqlite: 0 };
    setFormData({ ...formData, db_type: type, port: defaultPorts[type] });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center gap-2 text-text-primary">
          <Database className="w-5 h-5" />
          Database Connections
        </h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-3 py-1.5 bg-accent text-bg rounded-lg hover:bg-accent/90 text-sm transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Connection
        </button>
      </div>

      {showForm && (
        <div className="bg-surface-elevated p-4 rounded-lg border border-border space-y-3">
          <div>
            <label className="block text-sm font-medium mb-1 text-text-primary">Connection Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-border rounded-lg bg-surface text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
              placeholder="My Database"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-text-primary">Database Type</label>
            <select
              value={formData.db_type}
              onChange={(e) => handleDbTypeChange(e.target.value as any)}
              className="w-full px-3 py-2 border border-border rounded-lg bg-surface text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
            >
              <option value="postgresql">PostgreSQL</option>
              <option value="mysql">MySQL</option>
              <option value="sqlite">SQLite</option>
            </select>
          </div>

          {formData.db_type !== 'sqlite' && (
            <>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium mb-1 text-text-primary">Host</label>
                  <input
                    type="text"
                    value={formData.host}
                    onChange={(e) => setFormData({ ...formData, host: e.target.value })}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-surface text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-text-primary">Port</label>
                  <input
                    type="number"
                    value={formData.port}
                    onChange={(e) => setFormData({ ...formData, port: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-surface text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1 text-text-primary">Username</label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-surface text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1 text-text-primary">Password</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-surface text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>
            </>
          )}

          <div>
            <label className="block text-sm font-medium mb-1 text-text-primary">Database Name</label>
            <input
              type="text"
              value={formData.database}
              onChange={(e) => setFormData({ ...formData, database: e.target.value })}
              className="w-full px-3 py-2 border border-border rounded-lg bg-surface text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
              placeholder={formData.db_type === 'sqlite' ? 'path/to/database.db' : 'database_name'}
            />
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleTest}
              disabled={testing}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-surface-elevated text-text-primary border border-border rounded-lg hover:bg-white/[0.04] disabled:opacity-50 transition-colors"
            >
              {testing ? <Loader className="w-4 h-4 animate-spin" /> : <CheckCircle className="w-4 h-4" />}
              Test Connection
            </button>
            <button
              onClick={handleCreate}
              disabled={creating || !formData.name || !formData.database}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-accent text-bg rounded-lg hover:bg-accent/90 disabled:opacity-50 transition-colors"
            >
              {creating ? <Loader className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
              Create Connection
            </button>
          </div>
        </div>
      )}

      <div className="space-y-2">
        {connections.length === 0 ? (
          <div className="text-center py-8 text-text-secondary">
            <Database className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No connections yet. Add one to get started.</p>
          </div>
        ) : (
          connections.map((conn) => (
            <div
              key={conn.connection_id}
              className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                selectedConnectionId === conn.connection_id
                  ? 'border-accent bg-accent/10'
                  : 'border-border hover:border-accent/50'
              }`}
              onClick={() => onConnectionSelect(conn.connection_id)}
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-text-primary">{conn.name}</div>
                  <div className="text-sm text-text-secondary">
                    {conn.db_type} • {conn.database}
                    {conn.host && ` • ${conn.host}`}
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(conn.connection_id);
                  }}
                  className="p-2 text-red-500 hover:bg-red-500/10 rounded-lg transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
