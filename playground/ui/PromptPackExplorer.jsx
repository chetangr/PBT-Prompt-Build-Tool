import React, { useEffect, useState } from 'react';

export default function PromptPackExplorer() {
  const [packs, setPacks] = useState([]);

  useEffect(() => {
    fetch('/api/promptpacks/list')
      .then(res => res.json())
      .then(data => setPacks(data.packs || []));
  }, []);

  return (
    <div>
      <h3>Prompt Pack Explorer</h3>
      <ul>
        {packs.map(p => (
          <li key={p.name}>
            <strong>{p.name}</strong> – v{p.version}<br />
            {p.description}
          </li>
        ))}
      </ul>
    </div>
  );
}
