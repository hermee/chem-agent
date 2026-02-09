import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { ApiService, SmilesResult } from '../../services/api';

@Component({
  selector: 'app-lnp-agent',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './lnp-agent.html',
  styleUrl: './lnp-agent.css',
})
export class LnpAgent {
  smiles = '';
  loading = signal(false);
  result = signal<SmilesResult | null>(null);
  error = signal('');

  examples = [
    { name: 'DLin-MC3-DMA (simplified)', smiles: 'CCCCCCCC/C=C\\CCCCCCCC(=O)OCC(CN(C)C)OC(=O)CCCCCCCC/C=C\\CCCCCCCC' },
    { name: 'ALC-0315-like', smiles: 'CCCCCCCCCCOC(=O)CC(CC(=O)OCCCCCCCCCC)N(C)C' },
    { name: 'SM-102-like', smiles: 'CCCCCCCCCCOC(=O)CCCN(C)CCCC(=O)OCCCCCCCCCC' },
  ];

  scoreLabels: Record<string, string> = {
    qed: 'QED (Drug-likeness)',
    sa_score: 'SA Score (1=easy, 10=hard)',
    mol_weight: 'Molecular Weight',
    logp: 'LogP',
    tpsa: 'TPSA (Å²)',
    hba: 'H-Bond Acceptors',
    hbd: 'H-Bond Donors',
    rotatable_bonds: 'Rotatable Bonds',
    num_rings: 'Ring Count',
    heavy_atoms: 'Heavy Atoms',
  };

  constructor(private api: ApiService, private sanitizer: DomSanitizer) {}

  analyze(smiles: string) {
    if (!smiles.trim() || this.loading()) return;
    this.smiles = smiles;
    this.loading.set(true);
    this.error.set('');
    this.result.set(null);
    this.api.analyzeSmiles(smiles).subscribe({
      next: (res) => {
        if (res.error) this.error.set(res.error);
        else this.result.set(res);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Failed to analyze SMILES');
        this.loading.set(false);
      },
    });
  }

  safeSvg(svg: string): SafeHtml {
    return this.sanitizer.bypassSecurityTrustHtml(svg);
  }

  scoreKeys(): string[] {
    return Object.keys(this.scoreLabels);
  }

  scoreColor(key: string, val: number): string {
    if (key === 'qed') return val > 0.5 ? '#059669' : val > 0.3 ? '#d97706' : '#dc2626';
    if (key === 'sa_score') return val < 3 ? '#059669' : val < 5 ? '#d97706' : '#dc2626';
    return '#334155';
  }
}
