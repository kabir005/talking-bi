import { useState } from 'react';
import DatabaseConnector from '../components/dbagent/DatabaseConnector';
import LiveQueryPanel from '../components/dbagent/LiveQueryPanel';

export default function DatabaseAgentPage() {
  const [selectedConnectionId, setSelectedConnectionId] = useState<string>('');

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-text-primary">Database Agent</h1>
          <p className="text-text-secondary mt-2">
            Connect to live databases and query them using natural language
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-surface rounded-lg shadow-sm p-6 border border-border">
            <DatabaseConnector
              onConnectionSelect={setSelectedConnectionId}
              selectedConnectionId={selectedConnectionId}
            />
          </div>

          <div className="bg-surface rounded-lg shadow-sm p-6 border border-border">
            {selectedConnectionId ? (
              <LiveQueryPanel connectionId={selectedConnectionId} />
            ) : (
              <div className="flex items-center justify-center h-full text-text-secondary">
                <div className="text-center">
                  <p className="text-lg mb-2">Select a connection to start querying</p>
                  <p className="text-sm">or create a new connection on the left</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
