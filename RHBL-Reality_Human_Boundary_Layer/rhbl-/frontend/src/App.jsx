import React, { useState, useEffect } from "react";
import { ShieldCheck, Activity, Brain, AlertTriangle, Play, Square, Upload, Send } from "lucide-react";

const BACKEND = "http://localhost:7000";

function App() {
  const [isPaused, setIsPaused] = useState(false);
  const [manualText, setManualText] = useState("");
  const [stats, setStats] = useState({
    trust_score: 0,
    layer_scores: { human_authenticity: 0, reality_consistency: 0, manipulation_risk: 0 },
    violated_rules: [],
    prompt: "INITIALIZING...",
    rppg_wave: []
  });

  const handleAudioUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch(`${BACKEND}/analyze_audio`, { method: "POST", body: formData });
      const data = await res.json();
      if (data.error) { alert("Backend Error: " + data.error); return; }
      if (data.stats) setStats(data.stats);
    } catch (err) { console.error("Audio error", err); }
  };

  const handleTextSubmit = async () => {
    if (!manualText) return;
    const res = await fetch(`${BACKEND}/analyze_text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: manualText })
    });
    const data = await res.json();
    if (data.stats) setStats(data.stats);
    setManualText("");
  };

  useEffect(() => {
    if (isPaused) return;
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${BACKEND}/stats`);
        const data = await res.json();
        if (data && data.layer_scores) setStats(data);
      } catch (err) { console.error("Poll error", err); }
    }, 200);
    return () => clearInterval(interval);
  }, [isPaused]);

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8 font-sans">
      <header className="flex justify-between items-center mb-8 border-b border-slate-700 pb-4">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <ShieldCheck className="text-cyan-400" /> RHBL Infrastructure
        </h1>
        <div className="flex items-center gap-4">
          <div className="flex bg-slate-800 rounded-lg border border-slate-600 overflow-hidden">
            <input className="bg-transparent px-3 py-1 text-sm outline-none w-48" placeholder="Type triggers (e.g. police)..." value={manualText} onChange={(e) => setManualText(e.target.value)} />
            <button onClick={handleTextSubmit} className="p-2 bg-slate-700 hover:bg-slate-600 text-cyan-400"><Send size={16}/></button>
          </div>
          <label className="flex items-center gap-2 px-4 py-2 bg-slate-800 rounded-lg cursor-pointer hover:bg-slate-700 border border-slate-600">
            <Upload size={18} className="text-cyan-400" />
            <span className="text-sm font-bold uppercase">Analyze Audio</span>
            <input type="file" className="hidden" onChange={handleAudioUpload} accept="audio/*" />
          </label>
          <button onClick={() => setIsPaused(!isPaused)} className={`px-6 py-2 rounded-lg font-bold shadow-lg ${isPaused ? "bg-green-600" : "bg-red-600"}`}>
            {isPaused ? <><Play size={18} className="inline mr-2"/> RESUME</> : <><Square size={18} className="inline mr-2"/> STOP</>}
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-4">
          <div className="relative rounded-2xl overflow-hidden border-4 border-slate-800 bg-black aspect-video shadow-2xl">
            {!isPaused && <img src={`${BACKEND}/video_feed`} className="w-full h-full object-cover" alt="Live Feed" />}
            <div className="absolute top-4 left-4 bg-black/60 px-4 py-2 rounded-lg border border-white/20">
              <p className="text-cyan-400 font-bold animate-pulse">{stats.prompt}</p>
            </div>
          </div>
          <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700 h-24 flex items-end gap-1 overflow-hidden">
            {stats.rppg_wave.slice(-100).map((v, i) => (
              <div key={i} className="bg-cyan-500 w-1 rounded-t" style={{ height: `${v * 100}%` }} />
            ))}
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-xl text-center">
            <h2 className="text-slate-400 text-xs uppercase mb-2">Final Trust</h2>
            <div className="text-6xl font-black">{stats.trust_score.toFixed(2)}%</div>
            <div className="w-full bg-slate-700 h-3 rounded-full overflow-hidden mt-4">
              <div className="h-full bg-green-500 transition-all duration-700" style={{ width: `${stats.trust_score}%` }} />
            </div>
          </div>

          {[
            { label: "Human Authenticity", value: stats.layer_scores.human_authenticity, bar: "bg-cyan-500", text: "text-cyan-400" },
            { label: "Reality Consistency", value: stats.layer_scores.reality_consistency, bar: "bg-purple-500", text: "text-purple-400" },
            { label: "Manipulation Risk", value: stats.layer_scores.manipulation_risk, bar: "bg-red-500", text: "text-red-400" }
          ].map((layer) => (
            <div key={layer.label} className="bg-slate-800 p-4 rounded-xl border border-slate-700">
              <div className="flex justify-between mb-2 text-sm">
                <span className="text-slate-400">{layer.label}</span>
                <span className={`${layer.text} font-bold`}>{layer.value}%</span>
              </div>
              <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
                <div className={`${layer.bar} h-full transition-all duration-500`} style={{ width: `${layer.value}%` }} />
              </div>
            </div>
          ))}

          <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 min-h-[200px]">
            <h3 className="text-xs uppercase text-slate-400 mb-4 flex items-center gap-2"><Brain size={16} /> Reasoning Trace</h3>
            {stats.violated_rules.map((rule, i) => (
              <div key={i} className="flex gap-2 text-red-400 text-sm mb-2"><AlertTriangle size={16} className="shrink-0"/>{rule}</div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
export default App;