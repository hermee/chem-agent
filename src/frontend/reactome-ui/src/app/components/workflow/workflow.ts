import { Component } from '@angular/core';

@Component({
  selector: 'app-workflow',
  standalone: true,
  templateUrl: './workflow.html',
  styleUrl: './workflow.css',
})
export class Workflow {
  steps = [
    { id: 1, icon: '❓', title: 'User Query', description: 'Natural language question about ionizable lipid design', color: 'linear-gradient(135deg, #10b981, #06b6d4)' },
    { id: 2, icon: '🔄', title: 'Query Rewrite', description: 'Rewrites question to be self-contained using chat history', color: 'linear-gradient(135deg, #64748b, #94a3b8)' },
    { id: 3, icon: '🧭', title: 'Router', description: 'Classifies query as synthesis, lookup, or general', color: 'linear-gradient(135deg, #3b82f6, #6366f1)' },
    { id: 4, icon: '🔍', title: 'FAISS Retrieval + Rerank', description: '454 vectors searched — papers, rules, reaction templates, compound data', color: 'linear-gradient(135deg, #3b82f6, #6366f1)' },
    { id: 5, icon: '⚗️', title: 'Reaction Expert', description: 'SMARTS template matching, functional group analysis, feasibility', color: 'linear-gradient(135deg, #8b5cf6, #a855f7)', parallel: true },
    { id: 6, icon: '🧬', title: 'Lipid Design Expert', description: 'Retrosynthesis routes, SAR analysis, design rule compliance', color: 'linear-gradient(135deg, #8b5cf6, #a855f7)', parallel: true },
    { id: 7, icon: '🤖', title: 'Generative AI Expert', description: 'De novo generation models, RL optimization, reward functions', color: 'linear-gradient(135deg, #8b5cf6, #a855f7)', parallel: true },
    { id: 8, icon: '📊', title: 'Property Prediction Expert', description: 'ML model recommendations, uncertainty quantification', color: 'linear-gradient(135deg, #8b5cf6, #a855f7)', parallel: true },
    { id: 9, icon: '📚', title: 'Literature Scout', description: 'PubMed, PubChem, and web search for external evidence', color: 'linear-gradient(135deg, #8b5cf6, #a855f7)', parallel: true },
    { id: 10, icon: '🧠', title: 'Lead Agent', description: 'Supervisor — critically evaluates all expert outputs, resolves conflicts, produces final answer', color: 'linear-gradient(135deg, #10b981, #059669)' },
  ];
}
