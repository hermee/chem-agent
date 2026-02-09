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
    { id: 2, icon: '🔍', title: 'FAISS Retrieval', description: '454 vectors searched — papers, rules, reaction templates, compound data', color: 'linear-gradient(135deg, #3b82f6, #6366f1)' },
    { id: 3, icon: '⚗️', title: 'Reaction Expert', description: 'Analyzes applicable SMARTS templates, functional groups, conditions', color: 'linear-gradient(135deg, #8b5cf6, #a855f7)', parallel: true },
    { id: 4, icon: '📏', title: 'Design Rules Expert', description: 'Validates tail config, MCTS compatibility, synthesizability', color: 'linear-gradient(135deg, #8b5cf6, #a855f7)', parallel: true },
    { id: 5, icon: '🧪', title: 'Synthesis Planner', description: 'Step-by-step route with reaction IDs, building blocks, MCTS actions', color: 'linear-gradient(135deg, #f59e0b, #ef4444)' },
    { id: 6, icon: '📋', title: 'Final Answer', description: 'Comprehensive response with recommendations, compliance, and caveats', color: 'linear-gradient(135deg, #10b981, #059669)' },
  ];
}
