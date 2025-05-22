import React, { useState } from 'react';

export default function PromptPackPublisher() {
  const [name, setName] = useState('');
  const [version, setVersion] = useState('');
  const [desc, setDesc] = useState('');
  const [msg, setMsg] = useState('');

  async function handlePublish(e) {
    e.preventDefault();
    const res = await fetch('/api/promptpacks/publish', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, version, description: desc })
    });
    const data = await res.json();
    setMsg(data.message || 'Published!');
  }

  return (
    <form onSubmit={handlePublish}>
      <h3>Publish Prompt Pack</h3>
      <input value={name} onChange={e => setName(e.target.value)} placeholder="Pack name" />
      <input value={version} onChange={e => setVersion(e.target.value)} placeholder="Version" />
      <textarea value={desc} onChange={e => setDesc(e.target.value)} placeholder="Description" />
      <button type="submit">Publish</button>
      {msg && <p>{msg}</p>}
    </form>
  );
}
